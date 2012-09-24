from ...core import EntityList, Entity
from .structure import HTMLStructure

from xml.dom import minidom
from xml.dom import Node

class HTMLParser():

    @classmethod
    def parse(cls, text, code='default'):
        dtd = HTMLStructure()
        cls.build_element_list(text, dtd, code=code)
        dtd.fallback = code
        return dtd

    @classmethod
    def parse_to_entitylist(cls, text, code='default'):
        entitylist = EntityList()
        xmldoc = minidom.parseString(text)
        nodes = xmldoc.getElementsByTagName('*')
        for node in nodes:
            for cnode in node.childNodes:
                if cnode.nodeType == node.TEXT_NODE:
                    entitylist.add_entity(cls.parse_entity(cnode,  code))
        return entitylist

    @classmethod
    def parse_entity(cls, node, code='default'):
        id = abs_path(cnode)
        val = cnode.data
        return Entity(id,  val,  code)

    @classmethod
    def build_element_list (cls, text, object, type='comment', code='default', pointer=0, end=None):
        raise NotImplementedError()

#Mapping from node type to XPath node test function name
OTHER_NODES = {
    Node.TEXT_NODE: 'text',
    Node.COMMENT_NODE: 'comment',
    Node.PROCESSING_INSTRUCTION_NODE: 'processing-instruction'
    }

def abs_path(node):
    """
    Return an XPath expression that provides a unique path to
    the given node (supports elements, attributes, root nodes,
    text nodes, comments and PIs) within a document
    """
    if node.nodeType == Node.ELEMENT_NODE:
        count = 1
        #Count previous siblings with same node name
        previous = node.previousSibling
        while previous:
            if previous.localName == node.localName: count += 1
            previous = previous.previousSibling
        step = u'%s[%i]' % (node.nodeName, count)
        ancestor = node.parentNode
    elif node.nodeType == Node.ATTRIBUTE_NODE:
        step = u'@%s' % (node.nodeName)
        ancestor = node.ownerElement
    elif node.nodeType in OTHER_NODES:
        #Text nodes, comments and PIs
        count = 1
        #Count previous siblings of the same node type
        previous = node.previousSibling
        while previous:
            if previous.nodeType == node.nodeType: count += 1
            previous = previous.previousSibling
        test_func = OTHER_NODES[node.nodeType]
        step = u'%s()[%i]' % (test_func, count)
        ancestor = node.parentNode
    elif not node.parentNode:
        #Root node
        step = u''
        ancestor = node
    else:
        raise TypeError('Unsupported node type for abs_path')
    if ancestor.parentNode:
        return abs_path(ancestor) + u'/' + step
    else:
        return u'/' + step

