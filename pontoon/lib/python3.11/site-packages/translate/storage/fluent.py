#
# Copyright 2021 Jack Grigg
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

r"""
Manage the Fluent translation format.

It is a monolingual base class derived format with :class:`FluentFile`
and :class:`FluentUnit` providing file and unit level access.
"""

from __future__ import annotations

import re
import textwrap
from typing import TYPE_CHECKING, BinaryIO

from fluent.syntax import FluentSerializer, ast, parse, serialize, visitor

from translate.storage import base

if TYPE_CHECKING:
    from collections.abc import Iterator


class _SanitizeVisitor(visitor.Visitor):
    """
    Private class used to replace special characters at the start of Fluent
    Patterns.
    """

    def visit_Pattern(self, pattern: ast.Pattern) -> None:
        if not pattern.elements:
            # Unexpected since a Pattern wouldn't be created if it had no
            # content.
            # No children to descend into either, so we just return.
            return

        first_element = pattern.elements[0]
        if isinstance(first_element, ast.TextElement):
            # Replace the special characters "*", "[" and "." with a
            # StringLiteral if they appear at the start of a line.
            # NOTE: These are specified in the fluent EBNF's "indented_char".
            # Normally, these characters cannot appear at the start of a line
            # for a value because they are part of the syntax, so they must be
            # escaped. However, as an exception, these characters may appear at
            # the very start of a Pattern, on the same line as the "=" sign or
            # a Selection Variant key "[other]".
            # For example:
            #     m = .start
            # or
            #     m = *start
            #         another line
            #
            # We want to escape these special characters for two reasons:
            #   1. For consistency with other lines not being able to start with
            #      such a character in multiline values. For a Message or Term's
            #      value, there is no "=" sign in the derived source to indicate
            #      the exception.
            #   2. To make re-serialization easier. In particular, when we
            #      serialize the FluentUnit's source, we place the source on a
            #      newline for consistent behaviour and to preserve common
            #      indents.
            #   3. For better presentation of multiline Attribute or Variant
            #      values. These will consistently be printed on newlines, where
            #      the common-indent rule is clearer.
            #   4. To make sure that serializing a sub-pattern produces the same
            #      sub-string as it appears in the parent (modulo indents).
            first_char = first_element.value[0]
            if first_char in {"[", ".", "*"}:
                # Replace with literals.
                # NOTE: An empty TextElement is ok for the FluentSerializer.
                first_element.value = first_element.value[1:]
                pattern.elements.insert(0, ast.Placeable(ast.StringLiteral(first_char)))

        self.generic_visit(pattern)


def _fluent_pattern_to_source(pattern: ast.Pattern) -> str:
    """Convert the fluent Pattern into a source string."""
    if not pattern.elements:
        raise ValueError("Unexpected fluent Pattern without any elements")

    sanitizer = _SanitizeVisitor()
    sanitizer.visit(pattern)

    # Create a fluent Message with the given pattern and serialize it.
    # We use serialize_entry which is part of python-fluent's public API.
    source = FluentSerializer().serialize_entry(
        ast.Message(ast.Identifier("i"), value=pattern)
    )

    # Strip away the id part: "i =". For single-line values, a space is also
    # added. For multi-line values, a newline is added.
    # NOTE: Since we escaped any leading special character, the newline is
    # expected to always be added for multiline values.
    source = re.sub(r"^i =( |\n)", "", source, count=1)
    # Strip away the trailing newline that the serializer adds.
    source = re.sub(r"\n$", "", source, count=1)

    # Remove the common indent.
    # NOTE: textwrap.dedent also collapses blank lines.
    return textwrap.dedent(source)


class FluentReference:
    """Represents a reference Expression found in a fluent Pattern."""

    def __init__(
        self,
        reference: (ast.MessageReference | ast.TermReference | ast.VariableReference),
    ) -> None:
        """
        :param reference: The reference this represents.
        :type reference: MessageReference or TermReference or VariableReference
        """
        if isinstance(reference, ast.MessageReference):
            self._type_name = "message"
            attribute = reference.attribute
        elif isinstance(reference, ast.TermReference):
            self._type_name = "term"
            attribute = reference.attribute
        elif isinstance(reference, ast.VariableReference):
            self._type_name = "variable"
            attribute = None
        else:
            raise TypeError(f"Unhandled reference type {reference.__class__.__name__}")
        ref_name = reference.id.name
        if attribute:
            ref_name += f".{attribute.name}"
        self._name = ref_name

    @property
    def type_name(self) -> str:
        """
        The name for the type of reference.

        :type: str
        """
        return self._type_name

    @property
    def name(self) -> str:
        """
        The the reference name.

        :type: str
        """
        return self._name


class _ReferenceVisitor(visitor.Visitor):
    """
    Private class used to extract the Fluent references found below a fluent
    object.
    """

    def __init__(self) -> None:
        self.refs: list[FluentReference] = []

    def _add_ref(
        self,
        node: ast.MessageReference | ast.TermReference | ast.VariableReference,
    ) -> None:
        self.refs.append(FluentReference(node))

    def visit_MessageReference(self, node: ast.MessageReference) -> None:
        self._add_ref(node)
        # NOTE: We do not call Visitor.generic_visit because there is no child
        # to descend into for this type.

    def visit_TermReference(self, node: ast.TermReference) -> None:
        self._add_ref(node)

    def visit_VariableReference(self, node: ast.VariableReference) -> None:
        self._add_ref(node)


# NOTES to help understand FluentSelectorBranch and FluentSelectorNode:
#
# Given some fluent Pattern, we can break it down into a tree-like
# structure using the SelectExpressions as splitting points.
#
# For example, consider:
#
# upload { $num ->
#   [one] a photo
#  *[other] { FUNC($num) ->
#      [a] some
#     *[b] { $num }
#   } photos
# } immediately to { -server.vowel ->
#   [yes] an
#  *[no] a
# } { -sever } server.
#
# This would be broken down into
#
#                 [   top-branch  ]
#                 /               \
#                /                 \
# "upload "($num)" immediately to "(-server.vowel)" { -server } server."
#         /      \                     \        \
#     [one]      [other]               [yes]    [no]
#  "a photo"        |                   "an"     "a"
#              (FUNC($num))" photos"
#               /         \
#             [a]         [b]
#            "some"    "{ $num }"
#
#
# The parts in square-brackets are the FluentSelectorBranches and the parts
# in curved-brackets are the FluentSelectorNodes. The vertical lines
# represent the parent-child relation between a branch and a node, or a node
# and a branch. The parts in quotes are the text content that is filled in
# between the nodes, which would be "owned" by the branch above, but we do
# not show this relation.
#
# The top-branch just represents the top Pattern itself.
#
# Basically, each SelectExpression becomes a node, identified by the
# SelectExpression's selector (the part before the "->"). And its Variants
# become branches of that node, identified by the Variant's key (the part in
# the square brackets). Any SelectExpression in the Variant's Pattern
# becomes a node of that branch, and so on.
#
# This forms an overall tree-like structure which iterates between
# FluentSelectorBranch and FluentSelectorNode at each level. In particular,
# note that each FluentSelectorBranch may have any number of
# FluentSelectorNode children.
#
# Put another way, each node represents a point in the string where some
# variant/alternative sub-strings could be placed. Each branch represents
# one of these options.
#
# The end user will only ever see one variant of this string where each node
# is replaced with the text content of *one* of its branches. Although some
# branches can be ignored if their parent was not selected, such as the [a]
# and [b] branch if the [one] branch was selected.
#
# Each such variant can be expressed as the sequence of branches that are
# selected. These are the "branch_paths" for this Pattern. For this example
# there 6 different overall variants/branch_paths:
#
# [one]-[yes]
#   "upload a photo immediately to an { -server } server."
# [other]-[a]-[yes]
#   "upload some photos immediately to an { -server } server."
# [other]-[b]-[yes]
#   "upload { $num } photos immediately to an { -server } server."
# [one]-[no]
#   "upload a photo immediately to a { -server } server."
# [other]-[a]-[no]
#   "upload some photos immediately to a { -server } server."
# [other]-[b]-[no]
#   "upload { $num } photos immediately to a { -server } server."


class FluentSelectorNode:
    """
    Represents a single Fluent SelectExpression.

    Each instance will store details about the SelectExpression's selector, and
    will have a child FluentSelectorBranch for each Variant in the
    SelectExpression. It's parent FluentSelectorBranch represents the Fluent
    Pattern this SelectExpression was found within.
    """

    def __init__(
        self,
        select_expression: ast.SelectExpression,
        parent_branch: FluentSelectorBranch,
    ) -> None:
        """
        :param select_expression: The SelectExpression this represents.
        :type selector: SelectExpression
        :param parent_branch: The branch this node belongs to.
        :type parent_branch: FluentSelectorBranch
        """
        self._selector = select_expression.selector.clone()
        self._serialized_selector: str | None = None
        self._selector_references: list[FluentReference] | None = None

        self._parent_branch = parent_branch

        # We create a new FluentSelectorBranch for each Variant found in this
        # select expression.
        # NOTE: We expect _child_branches to be non-empty since a
        # SelectExpression must have at least one (default) variant.
        self._child_branches = [
            FluentSelectorBranch(variant.value, variant, self)
            for variant in select_expression.variants
        ]

    @property
    def parent_branch(self) -> FluentSelectorBranch:
        """
        The branch this node is below.

        The branch represents the Fluent Pattern the SelectExpression was found
        within.

        :type: FluentSelectorBranch
        """
        return self._parent_branch

    @property
    def child_branches(self) -> list[FluentSelectorBranch]:
        """
        The child branches for this node.

        The child branches represent the Variants found within the
        SelectExpression.

        :type: list[FluentSelectorBranch]
        """
        return self._child_branches

    @property
    def serialized_selector(self) -> str:
        """
        A serialized form of the SelectExpression's selector Expression.

        :type: str
        """
        if self._serialized_selector is None:
            # NOTE: Current fluent.syntax library only allows the select
            # expression's selector to be a:
            #  + TermReference with an attribute,
            #  + VariableReference,
            #  + FunctionReference,
            #  + StringLiteral, or
            #  + NumberLiteral
            pattern = ast.Pattern([ast.Placeable(self._selector)])
            serialized = _fluent_pattern_to_source(pattern)
            # Strip the outer pattern that we wrapped it in.
            serialized = re.sub("^{ *", "", serialized, count=1)
            serialized = re.sub(" *}$", "", serialized, count=1)
            self._serialized_selector = serialized
        return self._serialized_selector

    @property
    def selector_references(self) -> list[FluentReference]:
        """
        The references found in the SelectExpression's selector Expression.

        These are in the order of appearance.

        :type: list[FluentReference]
        """
        if self._selector_references is None:
            ref_visitor = _ReferenceVisitor()
            ref_visitor.visit(self._selector)
            # Take the refs from the visitor.
            self._selector_references = ref_visitor.refs
        return self._selector_references


class FluentSelectorBranch:
    """
    Represents a Fluent Pattern.

    The Pattern can either be the Fluent value or Attribute for a Message or
    Term, or it can belong to a SelectExpression's Variant.

    Each instance will have one FluentSelectorNode child for each
    SelectExpression found within the Pattern.

    If an instance represents a Variant Pattern, it will also store other
    details about the Variant and it will have a parent FluentSelectorNode that
    represents the SelectExpression the Variant was found within.
    """

    def __init__(
        self,
        pattern: ast.Pattern,
        variant: ast.Variant | None,
        parent_node: FluentSelectorNode | None,
    ) -> None:
        """
        :param pattern: The Pattern this represents.
        :type pattern: Pattern
        :param variant: The Variant this Pattern belongs to, or None if this is
        a top-level Pattern.
        :type variant: Variant or None
        :param parent_node: The parent node this belongs to, or None if this is
        a top-level Pattern.
        :type selector: FluentSelectorNode or None
        """
        self._variant = variant.clone() if variant else None
        self._top_references: list[FluentReference] | None = None

        self._parent_node = parent_node

        self._child_nodes: list[FluentSelectorNode] = []
        self._elements: list[FluentSelectorNode | ast.PatternElement] = []
        for element in pattern.elements:
            # If we have a select expression, we convert it into a
            # FluentSelectorNode. Otherwise we keep a copy of the raw
            # PatternElement.
            # NOTE: It is important to keep the FluentSelectorNodes and
            # PatternElements ordered in the same list to be able to generate
            # the flat Patterns.
            select_expression = self._get_select_expression(element)
            if select_expression:
                node = FluentSelectorNode(select_expression, self)
                self._elements.append(node)
                self._child_nodes.append(node)
            else:
                self._elements.append(element.clone())

    @staticmethod
    def _get_select_expression(
        fluent_node: ast.PatternElement,
    ) -> ast.SelectExpression | None:
        """
        Get the SelectExpression found below the given PatternElement
        fluent_node, or return None if the PatternElement does not contain one.
        """
        # A SelectExpression will be wrapped by at least on Placeable, but in
        # principle could be be wrapped by a longer series of Placeables.
        while isinstance(fluent_node, ast.Placeable):
            fluent_node = fluent_node.expression
            if isinstance(fluent_node, ast.SelectExpression):
                return fluent_node
        return None

    @property
    def parent_node(self) -> FluentSelectorNode | None:
        """
        The parent this branch is below, if any.

        The node represents the SelectExpression the Fluent Pattern was found
        within if it belonged to a Variant.

        :type: FluentSelectorNode or None
        """
        return self._parent_node

    @property
    def child_nodes(self) -> list[FluentSelectorNode]:
        """
        The child nodes for this branch.

        The child nodes represent the SelectExpressions found within the
        Pattern.

        :type: list[FluentSelectorNode]
        """
        return self._child_nodes

    @property
    def top_references(self) -> list[FluentReference]:
        """
        The references found in the Pattern.

        This excludes any references found within any child SelectExpression.

        These are in the order of appearance.

        :type: list[FluentReference]
        """
        if self._top_references is None:
            ref_visitor = _ReferenceVisitor()
            for element in self._elements:
                if isinstance(element, FluentSelectorNode):
                    continue
                ref_visitor.visit(element)
            # Take the refs from the visitor.
            self._top_references = ref_visitor.refs
        return self._top_references

    @property
    def key(self) -> str:
        """
        The key value for the Variant this Pattern belonged to.

        This will be an empty string if this Pattern did not belong to a
        Variant.

        :type: str
        """
        if not self._variant:
            return ""
        key = self._variant.key
        if isinstance(key, ast.NumberLiteral):
            return key.value
        if isinstance(key, ast.Identifier):
            return key.name
        raise ValueError(f"Unhandled key type {key.__class__.__name__}")

    @property
    def default(self) -> bool:
        """
        Whether the Variant this Pattern belonged to was the default.

        This will default to True if this Pattern was top-level and did not
        belong to a Variant.

        :type: bool
        """
        if not self._variant:
            return True
        return self._variant.default

    def to_flat_pattern_elements(
        self,
        branches: list[FluentSelectorBranch],
    ) -> Iterator[ast.PatternElement]:
        """
        Extract a stream of PatternElements using the given branches.

        This will yield the PatternElements found in the original Pattern in
        the same order, except it will never yield a SelectExpression, and hence
        be "flat". Instead, for any SelectExpression that would have
        been present, this method will choose only one of its Variants and yield
        the PatternElements found within, and so on for any further
        SelectExpressions found within.

        The Variants are chosen using the `branches` list, by finding the first
        branch that belongs to the node representing the SelectExpression.
        Therefore, the `branches` list must contain a branch for every such
        decision. This should be a list of branches returned by
        :meth:`~FluentSelectorBranch.branch_paths`.

        :param branches: The branches we should follow when we reach nodes.
        :type branches: list(FluentSelectorBranch)
        :return: A iterator of pattern elements.
        :rtype: Iterator[PatternElement]
        :raise ValueError: If we reach a node that has no branch in the given
        list.
        """
        for element in self._elements:
            if isinstance(element, FluentSelectorNode):
                branch = None
                for child in element.child_branches:
                    if child in branches:
                        branch = child
                        break
                if branch is None:
                    raise ValueError(
                        "branches is missing a branch for a FluentSelectorNode"
                    )
                yield from branch.to_flat_pattern_elements(branches)
            else:
                yield element.clone()

    def to_flat_string(self, branches: list[FluentSelectorBranch]) -> str:
        """
        The Pattern in a flat string form using the given branches.

        This will extract a flat Pattern using the given branches as specified
        in :meth:`~FluentSelectorBranch.to_flat_pattern_elements`, and will
        serialize it. The returned string represents one of the possible
        variants for the original Pattern.

        :param branches: The branches we should follow when we reach nodes.
        :type branches: list(FluentSelectorBranch)
        :return: The flat string.
        :rtype: str
        :raise ValueError: If we reach a node that has no branch in the given
        list.
        """
        pattern = ast.Pattern(list(self.to_flat_pattern_elements(branches)))
        return _fluent_pattern_to_source(pattern)

    def branch_paths(self) -> Iterator[list[FluentSelectorBranch]]:
        """
        Generates a list of unique branch paths.

        Each "path" is a list of branches, not including this instance itself,
        that selects one of the possible variants for the original Pattern.

        This is similar to all permutations of the branches found in any
        descendant node, with the condition that every branch in the permutation
        must also have its ancestor branch, other than this instance, in the
        same permutation. This ensures that each path would produce a unique
        result when passed to :meth:`~FluentSelectorBranch.to_flat_string` and
        :meth:`~FluentSelectorBranch.to_flat_pattern_elements`.

        :return: An iterator over all unique branch paths.
        :rtype: Iterator[list[FluentSelectorBranch]]
        """
        # This involves a mix of depth-first tree-traversal over the
        # nodes and and permutations over the individual children of the
        # branches.
        # NOTE: We do *not* want to simply traverse over all permutations of all
        # descendant branches. This is because some of these permutations
        # produce the same flat Pattern. E.g.
        #
        #   message = { $var1 ->
        #       [one] first
        #      *[other]
        #           { $var2 ->
        #               [one] second
        #              *[other] third
        #           }
        #   }
        #
        # All permutations would give:
        #
        #     $var1    $var2    final text
        #     ____________________________
        #     one      one      first
        #     one      other    first
        #     other    one      second
        #     other    other    third
        #
        # So we would get the same text "first" twice.
        #
        # Instead, we only want to increment over the permutations of a
        # node if its ancestor branch is included.
        iterator = _SelectorBranchIterator(self)
        while True:
            yield list(iterator.selected_branches())
            if not iterator.next():
                return


class _SelectorBranchIterator:
    """
    Private class to iterate over the nodes in a branch.

    At any given stage, this will track the selection state of all of its child
    branches.
    """

    def __init__(self, branch: FluentSelectorBranch) -> None:
        """
        :param branch: The branch to iterate over.
        :type branch: FluentSelectorBranch
        """
        self.branch = branch
        self.node_iterators = [
            _SelectorNodeIterator(node) for node in branch.child_nodes
        ]

    def next(self) -> bool:
        """
        Iterate the selection state of this branch forward one step.

        :return: True if the node was able to iterate forward, otherwise resets
        itself and returns False.
        :rtype: bool
        """
        # We try and iterate the selection state of one of our node children
        # until one of them does not reset itself.
        # This is similar to a digit counter: we try and increment a digit by 1,
        # otherwise we reset the digit to 0 and try and increment the next digit
        # instead.
        return any(node_iterator.next() for node_iterator in self.node_iterators)

    def selected_branches(self) -> Iterator[FluentSelectorBranch]:
        """
        Return all the branches that are selected at this stage.

        This does not include this branch itself.

        :return: An iterator over all currently selected branches.
        :rtype: Iterator[FluentSelectorBranch]
        """
        for node_it in self.node_iterators:
            branch_it = node_it.selected_branch_iterator()
            yield branch_it.branch
            yield from branch_it.selected_branches()


class _SelectorNodeIterator:
    """
    Private class to iterate over the branches in a node.

    At at any given stage, only one of the branches is selected.
    """

    def __init__(self, node: FluentSelectorNode) -> None:
        """
        :param node: The node whose branches we want to iterate over.
        :type node: FluentSelectorNode
        """
        self.node = node
        self._index = 0
        self.branch_iterators = [
            _SelectorBranchIterator(branch) for branch in node.child_branches
        ]

    def next(self) -> bool:
        """
        Iterate the selection state of this branch forward one step.

        :return: True if the node was able to iterate forward, otherwise resets
        itself and returns False.
        :rtype: bool
        """
        # First we try to iterate the selected branch.
        if self.branch_iterators[self._index].next():
            return True
        # The selected branch was reset, so we try and select the next branch
        # instead if possible.
        self._index += 1
        if self._index >= len(self.branch_iterators):
            # We reset our selection to the first branch again.
            self._index = 0
            return False
        return True

    def selected_branch_iterator(self) -> _SelectorBranchIterator:
        """
        The iterator for the currently selected branch.

        :return: The selected branch.
        :rtype: _SelectorBranchIterator
        """
        return self.branch_iterators[self._index]


class FluentPart:
    """
    Represents a "part" of a fluent Entry.

    This can either represent its value or one of its Attributes.
    """

    def __init__(self, name: str, pattern: ast.Pattern) -> None:
        """
        :param name: The name of this part.
        :type name: str
        :param pattern: The Fluent Pattern for this part.
        :type pattern: Pattern
        """
        self._name = name
        self._pattern = pattern
        self._top_branch: FluentSelectorBranch | None = None

    @property
    def name(self) -> str:
        """
        The name of the part.

        This will be an empty string for Entry values, and the attribute name
        for Entry Attributes.

        :type: str
        """
        return self._name

    @property
    def top_branch(self) -> FluentSelectorBranch:
        """
        The top-level selector branch that represents this part's Pattern.

        :type: FluentSelectorBranch
        """
        if not self._top_branch:
            self._top_branch = FluentSelectorBranch(self._pattern, None, None)
        return self._top_branch


def _duplicate_attribute(entry: ast.Term | ast.Message) -> ast.Attribute | None:
    """
    Return the first attribute in the given Term or Message entry that
    has the same id as a previous attribute, or None if none of the attributes
    clash.
    """
    for index, attr in enumerate(entry.attributes):
        for other_index in range(index + 1, len(entry.attributes)):
            other_attr = entry.attributes[other_index]
            if attr.id.name == other_attr.id.name:
                return other_attr
    return None


class FluentUnit(base.TranslationUnit):
    """
    Represents a single fluent Message, Term, a ResourceComment, a
    GroupComment or a stand-alone Comment.
    """

    def __init__(
        self,
        source: str | None = None,
        unit_id: str | None = None,
        comment: str = "",
        fluent_type: str = "Message",
        placeholders: list[str] | None = None,
    ) -> None:
        """
        :param source: The serialized fluent value, or None.
        :type source: str or None
        :param unit_id: An optional id to set (see :meth:`~FluentUnit.setid`),
            otherwise an id is generated from the given `source`.
        :type unit_id: str or None
        :param str comment: An optional comment for the unit.
        :param str fluent_type: The fluent type this unit corresponds to.
        :param placeholders: An optional list of sub-strings of the source that
            should be highlighted as placeholders. A translation of this unit
            would be expected to contain the same sub-strings.
        :type placeholders: list[str] or None
        """
        if fluent_type not in {
            "Message",
            "Term",
            "ResourceComment",
            "GroupComment",
            "DetachedComment",
        }:
            raise ValueError(f'Unknown value "{fluent_type}" for fluent_type')
        super().__init__(source)
        self._fluent_type = fluent_type
        self._is_comment = fluent_type.endswith("Comment")
        self.placeholders = placeholders or []
        self.target = source
        if unit_id is None and fluent_type == "Message" and source:
            unit_id = self._id_from_source(source)
        self.setid(unit_id)
        self.addnote(comment)

    @staticmethod
    def _id_from_source(source: str) -> str:
        # If the caller does not provide a unit ID, we need to generate one
        # ourselves.
        # The set of valid ids is restricted, so we cannot use the source string
        # as the identifier (as e.g. PO files do). Instead, we hash the source
        # string with a collision-resistant hash function.
        # By default, we choose an id that indicates that this represents a
        # fluent Message.
        import hashlib

        return "gen-" + hashlib.sha256(source.encode()).hexdigest()

    def getid(self) -> str | None:
        return self._id

    # From fluent EBNF.
    _FLUENT_ID_PATTERN = r"[a-zA-Z][a-zA-Z0-9_-]*"
    _FLUENT_ID_REGEXES = {
        "Message": _FLUENT_ID_PATTERN,
        "Term": r"-" + _FLUENT_ID_PATTERN,
    }

    def setid(self, value: str | None) -> None:
        """
        Set the id of the unit.
        A valid fluent identifier is [a-zA-Z][a-zA-Z0-9_-]*
        For a FluentUnit that represents a fluent Message, the id must be a
        valid fluent identifier.
        For a fluent Term, the id must be a valid fluent identifier prefixed by
        a "-".
        For a fluent Comment, GroupComment or ResourceComment, the id is unused.
        """
        regex = self._FLUENT_ID_REGEXES.get(self._fluent_type, "")
        if not re.fullmatch(regex, value or ""):
            raise ValueError(
                f"Invalid id for a {self._fluent_type} FluentUnit: {value}"
            )
        self._id = value or None

    def isheader(self) -> bool:
        return self._is_comment

    @property
    def fluent_type(self) -> str:
        """The fluent type this unit corresponds to."""
        return self._fluent_type

    def getplaceables(self) -> list[str]:
        """Still called in Weblate. Returns :attr:`~FluentUnit.placeholders`."""
        return self.placeholders

    @classmethod
    def new_from_entry(cls, fluent_entry: ast.Entry, comment: str = "") -> FluentUnit:
        """
        Create a new unit corresponding to the given fluent AST entry.

        :param fluent_entry: A fluent Entry to convert.
        :type fluent_entry: Entry
        :param comment: A comment to set on the unit. For fluent Comments the
            comment is taken from the object instead.
        :type comment: str

        :return: A new FluentUnit.
        :rtype: FluentUnit
        """
        if isinstance(fluent_entry, ast.ResourceComment):
            return cls(comment=fluent_entry.content, fluent_type="ResourceComment")
        if isinstance(fluent_entry, ast.GroupComment):
            return cls(comment=fluent_entry.content, fluent_type="GroupComment")
        if isinstance(fluent_entry, ast.Comment):
            return cls(comment=fluent_entry.content, fluent_type="DetachedComment")
        if isinstance(fluent_entry, ast.Term):
            return cls._create_from_fluent_pattern(
                fluent_entry, "Term", f"-{fluent_entry.id.name}", comment
            )
        if isinstance(fluent_entry, ast.Message):
            return cls._create_from_fluent_pattern(
                fluent_entry, "Message", fluent_entry.id.name, comment
            )
        raise ValueError(f"Unhandled fluent type: {fluent_entry.__class__.__name__}")

    @classmethod
    def _create_from_fluent_pattern(
        cls,
        fluent_entry: ast.Message | ast.Term,
        fluent_type: str,
        unit_id: str,
        comment: str,
    ) -> FluentUnit:
        """Create a new unit from a fluent entry that has a Pattern value."""
        lines = []
        if fluent_entry.value:
            lines.append(_fluent_pattern_to_source(fluent_entry.value))
        for attr in fluent_entry.attributes:
            attr_source = _fluent_pattern_to_source(attr.value)
            source = f".{attr.id.name} ="
            if "\n" in attr_source:
                # Multi-line Attributes placed on newline.
                source += "\n"
            else:
                source += " "
            source += attr_source
            lines.append(source)
        return cls(
            source="\n".join(lines),
            unit_id=unit_id,
            comment=comment,
            fluent_type=fluent_type,
            placeholders=cls._fluent_pattern_placeholders(fluent_entry, fluent_type),
        )

    @classmethod
    def _descendant_refs(
        cls, branch: FluentSelectorBranch
    ) -> Iterator[FluentReference]:
        yield from branch.top_references
        for node in branch.child_nodes:
            for child_branch in node.child_branches:
                yield from cls._descendant_refs(child_branch)

    @classmethod
    def _fluent_pattern_placeholders(
        cls, fluent_entry: ast.Message | ast.Term, fluent_type: str
    ) -> list[str]:
        """Get the placeholders expected for the given fluent entry."""
        # NOTE: For Terms, we do not look through references in the Attributes.
        # Only Term's have their Attributes appear in their source, and Term
        # Attributes tend to be locale-specific, which we don't want to
        # influence the placeholders.
        # FIXME: For Messages, we expect Attributes to contain the same
        # references in translations, but the placeholders have no way to
        # distinguish between whether the placeholder is found in the same
        # attribute or not. So we do not include them.
        if not fluent_entry.value:
            return []
        placeholders = set()
        for ref in cls._descendant_refs(FluentPart("", fluent_entry.value).top_branch):
            if ref.type_name == "message":
                placeholders.add(f"{{ {ref.name} }}")
            elif ref.type_name == "term":
                placeholders.add(f"{{ -{ref.name} }}")
            elif ref.type_name == "variable" and fluent_type != "Term":
                # For Terms, variables tend to be locale-specific.
                placeholders.add(f"{{ ${ref.name} }}")
        return list(placeholders)

    def to_entry(self) -> ast.Entry | None:
        """
        Convert the unit into a corresponding fluent AST Entry.

        :return: A new fluent AST Entry, if one was created.
        :rtype: Entry or None
        :raises ValueError: if the unit source contains an error.
        """
        fluent_id = self.getid()
        if fluent_id:
            # Remove the leading "-" for Terms.
            fluent_id = re.sub(r"^-", "", fluent_id, count=1)
        if self.fluent_type == "ResourceComment":
            # Create a comment, even if empty. Especially since empty
            # GroupComments are meant to end a previous GroupComment's
            # scope.
            return ast.ResourceComment(content=(self.getnotes() or ""))
        if self.fluent_type == "GroupComment":
            return ast.GroupComment(content=(self.getnotes() or ""))
        if self.fluent_type == "DetachedComment":
            return ast.Comment(content=(self.getnotes() or ""))
        if self.fluent_type in {"Term", "Message"}:
            return self._source_to_fluent_entry()
        raise ValueError(f"Unhandled fluent_type: {self.fluent_type}")

    def _source_to_fluent_entry(self) -> ast.Entry | None:
        """Convert a FluentUnit's source to a fluent Term or Message."""
        entry_or_error = self._try_source_to_fluent_entry()
        if isinstance(entry_or_error, str):
            raise TypeError(
                f'Error in source of FluentUnit "{self.getid()}":\n{entry_or_error}'
            )
        return entry_or_error

    def _try_source_to_fluent_entry(self) -> ast.Message | ast.Term | str | None:
        """
        Convert a FluentUnit's source to a generic fluent Entry. Returns a
        string with an error message if this fails.
        """
        source = self.source
        if not source:
            return None

        # Create a fluent Message by prefixing the source with "unit-id = \n"
        # and parsing it. After each newline we also indent so that it is
        # considered part of the same entry.
        source_lines = [(f"{self.getid()} =", "")]
        source_lines.extend((" ", line) for line in source.split("\n"))
        source = "\n".join([added + orig for (added, orig) in source_lines])

        # We use parse which is part of python-fluent's public API.
        # The other advantage is that the entry will return Junk with an error
        # description if there are syntax errors.
        # NOTE: We cannot reliably use FluentParser.parse_entry because it does
        # not parse the entire input, but only up until the entry ends. So if a
        # source contains syntax to start another entry it will not throw an
        # error. For example, a line that starts with "*" will end an entry.
        res = parse(source)

        # First look for junk.
        for entry in res.body:
            if isinstance(entry, ast.Junk):
                error_message = []
                for annotation in entry.annotations:
                    # Convert the fluent error position into a line number and
                    # offset of the unit's source.
                    offset = annotation.span.start
                    line = 0
                    for added, orig in source_lines:
                        if not orig:
                            # Entire line was added, so we want to skip this
                            # line. If we are within this line, then the offset
                            # will be set to "0" for the next loop.
                            line_len = len(added) + 1
                            offset = max(0, offset - line_len)
                            continue
                        added_len = len(added)
                        # Plus one for the newline/end-of-line.
                        line_len = added_len + len(orig) + 1
                        if offset < line_len:
                            # On this line.
                            offset = max(0, offset - added_len)
                            break
                        offset -= line_len
                        line += 1
                    error_message.append(
                        f"{annotation.code}: {annotation.message} "
                        f"[line {line + 1}, column {offset + 1}]"
                    )
                return "\n".join(error_message)
        if len(res.body) != 1:
            # This is unexpected since if the user tried to insert extra
            # Entries, they would have likely given us Junk above since we
            # indented *all* lines, which would prevent starting a new entry.
            return "Unexpectedly found {len(res.body)} fluent Entries"
        entry = res.body[0]
        if self.fluent_type == "Term" and not isinstance(entry, ast.Term):
            # Also unexpected since we started with "-tmp =", which starts a new
            # Term.
            return (
                f"Unexpectedly found a fluent {entry.__class__.name__} "
                "Entry rather than a Term"
            )
        if self.fluent_type != "Term" and not isinstance(entry, ast.Message):
            # Also unexpected since we started with "tmp =", which starts a new
            # Message.
            return (
                f"Unexpectedly found a fluent {entry.__class__.name__} "
                "Entry rather than a Message"
            )

        dup_attr = _duplicate_attribute(entry)
        if dup_attr:
            return f'The "{dup_attr.id.name}" attribute is assigned to more than once'

        return entry

    # API used in weblate.

    def get_syntax_error(self) -> str | None:
        """
        Get the Fluent syntax error for this unit, if it has one.

        :return: The syntax error message, or None if it has no error.
        :rtype: str or None
        """
        if self.fluent_type not in {"Term", "Message"}:
            return None
        entry_or_error = self._try_source_to_fluent_entry()
        if isinstance(entry_or_error, str):
            return entry_or_error
        return None

    def get_parts(self) -> list[FluentPart] | None:
        """
        Get all the distinct parts that make up the fluent Pattern generated
        by the unit's source.

        A Term and Message unit may have a value part, which is the entry's main
        string value, as well as multiple additional attribute parts.

        :return: The parts that make up the string, or None if it has some
            syntax error.
        :rtype: list[FluentPart] or None
        """
        if self.fluent_type not in {"Term", "Message"}:
            return []

        entry_or_error = self._try_source_to_fluent_entry()
        if isinstance(entry_or_error, str):
            return None

        if not entry_or_error:
            # Empty.
            return []

        parts = []
        if entry_or_error.value:
            parts.append(FluentPart("", entry_or_error.value))
        parts.extend(
            FluentPart(attr.id.name, attr.value) for attr in entry_or_error.attributes
        )
        return parts


class FluentFile(base.TranslationStore):
    """A Fluent file."""

    Name = "Fluent file"
    Mimetypes = []
    Extensions = ["ftl"]
    UnitClass = FluentUnit

    def __init__(self, inputfile: BinaryIO | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.filename = getattr(inputfile, "name", "")
        if inputfile is not None:
            self.parse(inputfile.read())

    def parse(self, fluentsrc: bytes) -> None:
        found_ids = []
        resource = parse(fluentsrc.decode("utf-8"))
        for entry in resource.body:
            # Handle this unit separately if it is invalid.
            if isinstance(entry, ast.Junk):
                raise self._fluent_junk_to_error(entry)

        # We add another line to the comments, even if it is blank.
        resource_comment_list = [
            entry.content
            for entry in resource.body
            if isinstance(entry, ast.ResourceComment)
        ]

        resource_comments = "\n".join(resource_comment_list)
        comment_prefix = resource_comments
        for entry in resource.body:
            if isinstance(entry, ast.BaseComment):
                self.addunit(FluentUnit.new_from_entry(entry))
                if isinstance(entry, ast.GroupComment):
                    # A GroupComment replaces the previous GroupComment.
                    comment_prefix = self._combine_comments(resource_comments, entry)
            elif isinstance(entry, (ast.Term, ast.Message)):
                unit = FluentUnit.new_from_entry(
                    entry,
                    self._combine_comments(comment_prefix, entry.comment),
                )
                unit_id = unit.getid()
                if unit_id in found_ids:
                    raise ValueError(
                        f'Entry "{unit_id}" has the same id as a previous entry'
                        f" [offset {entry.span.start}]"
                    )
                found_ids.append(unit_id)

                dup_attr = _duplicate_attribute(entry)
                if dup_attr:
                    raise ValueError(
                        f'Entry "{unit_id}" assigns to the same '
                        f'"{dup_attr.id.name}" attribute more than once '
                        f"[offset {dup_attr.span.start}]"
                    )
                self.addunit(unit)
            else:
                raise TypeError(
                    f"Unhandled fluent Entry type: {entry.__class__.__name__}"
                )

    @staticmethod
    def _fluent_junk_to_error(junk: ast.Junk) -> ValueError:
        """Convert the given fluent Junk object into a ValueError."""
        error_message = [
            "Parsing error for fluent source: "
            + junk.content.strip()[0:64].replace("\n", "\\n")
            + "[...]"
        ]
        error_message.extend(
            f"{annotation.code}: {annotation.message} [offset {annotation.span.start}]"
            for annotation in junk.annotations
        )
        return ValueError("\n".join(error_message))

    @staticmethod
    def _combine_comments(*comments: ast.BaseComment | str) -> str:
        """
        Combine the given string or fluent BaseComment objects into a single
        string.
        """
        comment_text = []
        for part in comments:
            if isinstance(part, ast.BaseComment):
                comment_text.append(part.content)
            else:
                comment_text.append(part)
        return "\n".join(text for text in comment_text if text)

    def serialize(self, out):
        prefix_comments = [
            unit.getnotes() or ""
            for unit in self.units
            if unit.fluent_type == "ResourceComment"
        ]
        prev_group_comment = ""

        body = []
        for unit in self.units:
            entry = unit.to_entry()
            if not entry:
                continue
            if unit.fluent_type == "GroupComment":
                group_comment = entry.content
                if group_comment != prev_group_comment:
                    if not prev_group_comment:
                        prefix_comments.append(group_comment)
                    elif not group_comment:
                        prefix_comments = prefix_comments[:-1]
                    else:
                        prefix_comments[-1] = group_comment
                    prev_group_comment = group_comment
            elif unit.fluent_type in {"Term", "Message"}:
                comment = self._strip_prefix_from_comment(unit, prefix_comments)
                if comment:
                    entry.comment = ast.Comment(comment)
            body.append(entry)

        serialized = serialize(ast.Resource(body))
        # The Fluent parser may insert a blank line "    \n" in a multiline
        # value that has a gap. We tidy those up here.
        serialized = re.sub(r"\n +\n", "\n\n", serialized)
        out.write(serialized.encode(self.encoding))

    @staticmethod
    def _strip_prefix_from_comment(unit: FluentUnit, prefix_comments: list[str]) -> str:
        """
        Try to remove each prefix in `prefix_comments` in turn from the start
        of `unit`'s comment.
        """
        unit_comment = unit.getnotes() or ""
        for prefix in prefix_comments:
            if unit_comment == prefix:
                return ""
            # Remove the prefix as a block.
            # NOTE: removeprefix only available in python 3.9+.
            block = prefix + "\n"
            unit_comment = unit_comment.removeprefix(block)
        return unit_comment
