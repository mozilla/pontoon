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
    def dump_entitylistdiff (cls, entitylistdiff, justbody=False):
        string = '<h2>%s</h2>' % entitylistdiff.id
        string += '<table>'
        string += '<tr><th>Type</th><th>ID</th><th>locale1</th><th>locale2</th></tr>'
        added = entitylistdiff.entities('added')
        if len(added):
            string += '<tr><td>Added</td><td colspan="3">&nbsp;</td></tr>'
            for entity in added.values():
                string += '<tr><td>&nbsp;</td><td colspan="3">%s</td></tr>' % entity.id
        removed = entitylistdiff.entities('removed')
        if len(removed):
            string += '<tr><td>Removed</td><td colspan="3">&nbsp;</td></tr>' 
            for entity in removed.values():
                string += '<tr><td>&nbsp;</td><td colspan="3">%s</td></tr>' % entity.id
        modified = entitylistdiff.entities('modified')
        if len(modified):
            string += '<tr><td>Modified</td><td colspan="3">&nbsp;</td></tr>'
            for entitydiff in modified.values():
                string += '<tr><td>&nbsp;</td><td>%s</td><td>%s</td></td><td>%s</td></tr>' % (entitydiff.id,entitydiff.value()[0],entitydiff.value()[1])
        string += '</table>'
        if justbody:
            return string
        else:
            return header % ('EntityListDiff: %s' % entitylistdiff.id, css, string)

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
        return string

header = "<html><head><title>%s</title><style type='text/css'>%s</style></head><body>%s</body></html>"
css = 'table { border: 1px solid black; border-collapse: collapse;} td,th { border: 1px solid #ccc; padding: 0 10px 0 10px;} th {background-color: #eee;}'