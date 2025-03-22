#
# Copyright 2004-2007 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#

"""
Module for parsing Qt .ts files for translation.

Currently this module supports the old format of .ts files. Some applictaions
use the newer .ts format which are documented here:
`TS file format 4.3 <http://doc.qt.io/archives/4.3/linguist-ts-file-format.html>`_,
`Example <http://svn.ez.no/svn/ezcomponents/trunk/Translation/docs/linguist-format.txt>`_

`Specification of the valid variable entries <http://doc.qt.io/qt-5/qstring.html#arg>`_,
`2 <http://doc.qt.io/qt-5/qstring.html#arg-2>`_
"""

from translate.misc import ourdom


class QtTsParser:
    contextancestors = dict.fromkeys(["TS"])
    messageancestors = dict.fromkeys(["TS", "context"])

    def __init__(self, inputfile=None):
        """Make a new QtTsParser, reading from the given inputfile if required."""
        self.filename = getattr(inputfile, "filename", None)
        self.knowncontextnodes = {}
        self.indexcontextnodes = {}
        if inputfile is None:
            self.document = ourdom.parseString("<!DOCTYPE TS><TS></TS>")
        else:
            self.document = ourdom.parse(inputfile)
            assert self.document.documentElement.tagName == "TS"

    def addtranslation(
        self,
        contextname,
        source,
        translation,
        comment=None,
        transtype=None,
        createifmissing=False,
    ):
        """Adds the given translation (will create the nodes required if asked). Returns success."""
        contextnode = self.getcontextnode(contextname)
        if contextnode is None:
            if not createifmissing:
                return False
            # construct a context node with the given name
            contextnode = self.document.createElement("context")
            namenode = self.document.createElement("name")
            nametext = self.document.createTextNode(contextname)
            namenode.appendChild(nametext)
            contextnode.appendChild(namenode)
            self.document.documentElement.appendChild(contextnode)
        if not createifmissing:
            return False
        messagenode = self.document.createElement("message")
        sourcenode = self.document.createElement("source")
        sourcetext = self.document.createTextNode(source)
        sourcenode.appendChild(sourcetext)
        messagenode.appendChild(sourcenode)
        if comment:
            commentnode = self.document.createElement("comment")
            commenttext = self.document.createTextNode(comment)
            commentnode.appendChild(commenttext)
            messagenode.appendChild(commentnode)
        translationnode = self.document.createElement("translation")
        translationtext = self.document.createTextNode(translation)
        translationnode.appendChild(translationtext)
        if transtype:
            translationnode.setAttribute("type", transtype)
        messagenode.appendChild(translationnode)
        contextnode.appendChild(messagenode)
        return True

    def getxml(self):
        """Return the ts file as xml."""
        xml = self.document.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")
        # This line causes empty lines in the translation text to be removed
        # (when there are two newlines)
        return "\n".join(line for line in xml.split("\n") if line.strip())

    @staticmethod
    def getcontextname(contextnode):
        """Returns the name of the given context."""
        namenode = ourdom.getFirstElementByTagName(contextnode, "name")
        return ourdom.getnodetext(namenode)

    def getcontextnode(self, contextname):
        """Finds the contextnode with the given name."""
        contextnode = self.knowncontextnodes.get(contextname)
        if contextnode is not None:
            return contextnode
        contextnodes = self.document.searchElementsByTagName(
            "context", self.contextancestors
        )
        for contextnode in contextnodes:
            if self.getcontextname(contextnode) == contextname:
                self.knowncontextnodes[contextname] = contextnode
                return contextnode
        return None

    def getmessagenodes(self, context=None):
        """Returns all the messagenodes, limiting to the given context (name or node) if given."""
        if context is None:
            return self.document.searchElementsByTagName(
                "message", self.messageancestors
            )
        if isinstance(context, str):
            # look up the context node by name
            context = self.getcontextnode(context)
            if context is None:
                return []
        return context.searchElementsByTagName("message", self.messageancestors)

    @staticmethod
    def getmessagesource(message):
        """Returns the message source for a given node."""
        sourcenode = ourdom.getFirstElementByTagName(message, "source")
        return ourdom.getnodetext(sourcenode)

    @staticmethod
    def getmessagetranslation(message):
        """Returns the message translation for a given node."""
        translationnode = ourdom.getFirstElementByTagName(message, "translation")
        return ourdom.getnodetext(translationnode)

    @staticmethod
    def getmessagetype(message):
        """Returns the message translation attributes for a given node."""
        translationnode = ourdom.getFirstElementByTagName(message, "translation")
        return translationnode.getAttribute("type")

    @staticmethod
    def getmessagecomment(message):
        """Returns the message comment for a given node."""
        commentnode = ourdom.getFirstElementByTagName(message, "comment")
        # NOTE: handles only one comment per msgid (OK)
        # and only one-line comments (can be VERY wrong) TODO!!!
        return ourdom.getnodetext(commentnode)

    def iteritems(self):
        """Iterates through (contextname, messages)."""
        for contextnode in self.document.searchElementsByTagName(
            "context", self.contextancestors
        ):
            yield self.getcontextname(contextnode), self.getmessagenodes(contextnode)

    def __del__(self):
        """Clean up the document if required."""
        if hasattr(self, "document"):
            self.document.unlink()
