from ...core import Package, Structure, Comment, EntityList, Entity
from ...diff import StructureDiff, EntityListDiff, BlobDiff

import os

class TextSerializer():
    @classmethod
    def serialize(cls, element, fallback=None):
        if isinstance(element, Package):
            return cls.dump_package(element)
        else:
            return cls.dump_structure(element)

    @classmethod
    def dump_entity (cls, entity, indent=0):
        string = (u'    '*indent)+u'Entity(id:'+entity.id+u', value:"'+entity.value+u'")\n'
        return string

    @classmethod
    def dump_comment (cls, comment, indent=0):
        string = (u'    '*indent)+u'Comment(\n'
        for element in comment:
            string += cls.dump_element(element, indent+1)
        string += (u'    '*indent)+u')\n'
        return string

    @classmethod
    def dump_string(cls, unicode, indent=0):
        return (u'    '*indent)+u"String(\""+unicode.replace('\n',"\\n")+"\")\n"

    @classmethod
    def dump_element(cls, element, indent=0):
        if isinstance(element, Entity):
            return cls.dump_entity(element, indent)
        elif isinstance(element, Comment):
            return cls.dump_comment(element, indent)
        elif isinstance(element, unicode) or isinstance(element, str):
            return cls.dump_string(element, indent)
        else:
            return element

    @classmethod
    def dump_structure (cls, l10nobject, indent=0, content=True):
        string = (u'    '*indent)+u"== L10nObject: " + unicode(l10nobject.id) + u" ==\n"
        if content == True:
            for element in l10nobject:
                string += cls.dump_element(element, indent+1)
        return string

    @classmethod
    def dump_entitylist (cls, elist, indent=0, content=True):
        string = (u'    '*indent)+u"== EntityList: " + unicode(elist.id) + u" ==\n"
        if content == True:
            for entity in elist.values():
                string += cls.dump_entity(entity, indent+1)
        return string

    @classmethod
    def dump_blob (cls, blob, indent=0):
        string = (u'    '*indent)+'Blob: ' + blob.id + "\n"
        return string

    @classmethod
    def dump_package (cls, l10npack, indent=0, content=True):
        string = u''
        string += (u'    '*indent)+u'=== L10nPackage: ' + l10npack.id + u' ===\n'
        for key, package in l10npack.packages.items():
            string += cls.dump_package(package, indent+1, content)
        for key, object in l10npack.objects.items():
            if isinstance(object, Structure):
                string += cls.dump_structure(object, indent+1, content)
            elif isinstance(object, EntityList):
                string += cls.dump_entitylist(object, indent+1, content)
            else:
                string += cls.dump_blob(object, indent+1)
        return string

# diff part

    @classmethod
    def dump_blobdiff (cls, objectdiff, indent=0):
        string = u''
        if objectdiff.diff:
            string += u'     '*indent + 'object modified\n'
        else:
            string += u'     '*indent + 'object not modified\n'
        return string

    @classmethod
    def dump_entitylistdiff (cls, entitylistdiff, indent=0):
        string = u''
        added = entitylistdiff.entities('added')
        if len(added):
            string += u'     '*indent + u'added entites:\n'
            for entity in added.values():
                string += u'     '*(indent+1) + entity.id + u'\n'
        removed = entitylistdiff.entities('removed')
        if len(removed):
            string += u'     '*indent + u'removed entities:\n' 
            for entity in removed.values():
                string += u'     '*(indent+1) + entity.id + u'\n'
        modified = entitylistdiff.entities('modified')
        if len(modified):
            string += u'     '*indent + u'modified entities:\n'
            for entitydiff in modified.values():
                string += u'     '*(indent+1) + entitydiff.id + u"(value '"+entitydiff.value()[0]+u"' -> '"+entitydiff.value()[1]+u"')\n"
        return string

    @classmethod
    def dump_structurediff (cls, l10nobjectdiff, indent=0):
        return cls.dump_entitylistdiff(l10nobjectdiff.entitylistdiff(), indent=indent)

    @classmethod
    def dump_packagediff (cls, l10npackagediff, indent=0):
        string = u''
        added = l10npackagediff.structures('added')
        if len(added):
            string += u'     '*indent + u'\033[1mnew in the latter package:\033[0m\n'
            for object in added:
                string += u'     '*(indent+1) + os.path.join('.', object.id) + u'\n'
        removed = l10npackagediff.structures('removed')
        if len(removed):
            string += u'     '*indent + u'\033[1mremoved in the latter package:\033[0m\n'
            for object in removed:
                string += u'     '*(indent+1) + os.path.join('.', object.id) + u'\n'
        modified = l10npackagediff.structures('modified')
        if len(modified):
            string += u'     '*indent + u'\033[1mmodified in the latter package:\033[0m\n'
            for object in modified:
                string += u'     '*(indent+1) + os.path.join('.', object.id) + u'\n'
                if isinstance(object, StructureDiff):
                    string += cls.dump_structurediff(l10npackagediff._structures[object.id]['struct'], indent+2)
                elif isinstance(object, EntityListDiff):
                    string += cls.dump_entitylistdiff(l10npackagediff._structures[object.id]['struct'], indent+2)
                elif isinstance(object, BlobDiff):
                    string += cls.dump_blobdiff(l10npackagediff._structures[object.id]['struct'], indent+2)

        added = l10npackagediff.packages('added')
        if len(added):
            string += u'     '*indent + u'\033[1mnew in the latter package:\033[0m\n'
            for package in added:
                string += u'     '*(indent+1) + os.path.join('.',package.id) + u'\n'
        removed = l10npackagediff.packages('removed')
        if len(removed):
            string += u'     '*indent + '\033[1mremoved from latter package:\033[0m\n'
            for package in removed:
                string += u'     '*(indent+1) + os.path.join('.',package.id) + u'\n'
        modified = l10npackagediff.packages('modified')
        if len(modified):
            string += u'     '*indent + u'\033[1mmodified in the latter package:\033[0m\n'
            for package in modified:
                string += u'     '*(indent+1) + os.path.join('.',package.id) + u'\n'
                string += cls.dump_packagediff(l10npackagediff._packages[package.id]['package'], indent+2)
        if not len(string):
            string += u'\nThe packages are identical'
        return string
