from silme.diff import *
import cgi
import os

class HTMLSerializer():
    @classmethod
    def serialize(cls, l10nobject, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_element (cls, element, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_entity (cls, entity, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_entitylist(cls, elist, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_comment (cls, comment):
        raise NotImplementedError()

    @classmethod
    def dump_entitylistdiff (cls, eld, justbody=False):
        string = '<h2>%s</h2>' % eld.id
        string += '<table>'
        string += '<tr><th>ID</th>'
        #for i in range(0,eld.count):
        #    string += '<th>locale%s</th>' % (i+1)
        string += '<th>es-MX</th><th>es-BO</th></tr>'
        added = eld.entities('added')
        if len(added):
            string += '<tr><td>Added</td><td colspan="%s">&nbsp;</td></tr>' % (eld.count+2)
            for entity in added.values():
                string += '<tr><td>&nbsp;</td><td colspan="%s">%s</td></tr>' % (eld.count+2,entity.id)
        removed = eld.entities('removed')
        if len(removed):
            string += '<tr><td>Removed</td><td colspan="%s">&nbsp;</td></tr>'  % (eld.count+2)
            for entity in removed.values():
                string += '<tr><td>&nbsp;</td><td colspan="%s">%s</td></tr>' % (eld.count+2,entity.id)
        modified = eld.entities('modified')
        if len(modified):
            for entitydiff in modified.values():
                values = entitydiff.value
                string += '<tr><td>%s</td>' % entitydiff.id
                for i in range(0,eld.count):
                    string += '<td>%s</td>' % (cgi.escape(values[i]) if values[i] else 'None')
                string += '</tr>' 
        string += '</table>'
        if justbody:
            return string
        else:
            return header % ('EntityListDiff: %s' % eld.id, css, string)

    @classmethod
    def dump_entitylistdiff2 (cls, eld, justbody=False):
        string = '<h2>%s</h2>' % eld.id
        string += '<table>'
        string += '<tr><th>Type</th><th>ID</th>'
        for i in range(0,eld.count):
            string += '<th>locale%s</th>' % (i+1)
        string += '</tr>'
        added = eld.entities('added')
        if len(added):
            string += '<tr><td>Added</td><td colspan="%s">&nbsp;</td></tr>' % (eld.count+2)
            for entity in added.values():
                string += '<tr><td>&nbsp;</td><td colspan="%s">%s</td></tr>' % (eld.count+2,entity.id)
        removed = eld.entities('removed')
        if len(removed):
            string += '<tr><td>Removed</td><td colspan="%s">&nbsp;</td></tr>'  % (eld.count+2)
            for entity in removed.values():
                string += '<tr><td>&nbsp;</td><td colspan="%s">%s</td></tr>' % (eld.count+2,entity.id)
        modified = eld.entities('modified')
        if len(modified):
            string += '<tr><td>Modified</td><td colspan="%s">&nbsp;</td></tr>'  % (eld.count+2)
            for entitydiff in modified.values():
                values = entitydiff.value
                string += '<tr><td>&nbsp;</td><td>%s</td>' % entitydiff.id
                for i in range(0,eld.count):
                    string += '<td>%s</td>' % (cgi.escape(values[i]) if values[i] else 'None')
                string += '</tr>' 
        string += '</table>'
        if justbody:
            return string
        else:
            return header % ('EntityListDiff: %s' % eld.id, css, string)

    @classmethod
    def dump_packagediff (cls, l10npackagediff, indent=0):
        string = u''
        added = l10npackagediff.structures('added')
        if len(added):
            string += 'Added'
            for object in added:
                string += os.path.join('.', object.id) + u'<br/>'
        removed = l10npackagediff.structures('removed')
        if len(removed):
            string += 'Removed'
            for object in removed:
                string += os.path.join('.', object.id) + u'<br/>'
        modified = l10npackagediff.structures('modified')
        if len(modified):
            for object in modified:
                if isinstance(object, EntityListDiff):
                    string += cls.dump_entitylistdiff(l10npackagediff._structures[object.id]['struct'], indent+2)

        added = l10npackagediff.packages('added')
        if len(added):
            string += 'Added'
            for package in added:
                string += os.path.join('.',package.id) + u'<br/>'
        removed = l10npackagediff.packages('removed')
        if len(removed):
            string += 'Removed'
            for package in removed:
                string += os.path.join('.',package.id) + u'<br/>'
        modified = l10npackagediff.packages('modified')
        if len(modified):
            string += 'Modified'
            for package in modified:
                string += os.path.join('.',package.id) + u'<br/>'
                string += cls.dump_packagediff(l10npackagediff._packages[package.id]['package'], indent+2)
        if not len(string):
            string += u'<h1>The packages are identical</h1>'
        return header % ('PackageDiff: %s' % l10npackagediff.id, css, string)

header = "<html><head><title>%s</title><style type='text/css'>%s</style></head><body>%s</body></html>"
css = 'table { border: 1px solid black; border-collapse: collapse;} td,th { border: 1px solid #ccc; padding: 0 10px 0 10px;} th {background-color: #eee;}'