from ..core import Blob, Structure, Comment, Package

def intersect(a, b):
    return list(set(a) & set(b))

class PackageDiff(object):
    def __init__(self):
        self._packages = {}
        self._structures = {}
        self.id = None
        self.uri = None

    def __len__(self):
        return len(self._packages)+len(self._structures)

    def __iter__(self):
        for i in self._packages.items():
            yield i+('package',)
        for i in self._structures.items():
            yield i+('structure',)
        raise StopIteration
    
    def __contains__(self, item):
        return item in self._packages or item in self._structures

    def empty(self):
        return not len(self)

    def add_package(self, l10npack_diff, path=None, type='modified'):
        if path == None or path=='':
            self._packages[l10npack_diff.id] = {'package':l10npack_diff, 'type': type}
        else:
            path = path.split('/')
            if path[0] in self._packages:
                self._packages[path[0]]['package'].add_package(l10npack_diff, '/'.join(path[1:]), type)
            else:
                sub_l10npack_diff = PackageDiff()
                sub_l10npack_diff.id = path[0]
                self._packages[path[0]] = {'package':sub_l10npack_diff, 'type':'modified'}
                return sub_l10npack_diff.add_package(l10npack_diff,'/'.join(path[1:]), type)
        return True

    def add_structure(self, l10nobject_diff, path=None, type='modified'):
        if path == None or path == '':
            self._structures[l10nobject_diff.id] = {'struct':l10nobject_diff, 'type': type}
        else:
            path = path.split('/')
            if path[0] in self._packages:
                self._packages[path[0]]['package'].add_structure(l10nobject_diff, '/'.join(path[1:]))
            else:
                sub_l10npack_diff = PackageDiff()
                sub_l10npack_diff.id = path[0]
                self._packages[path[0]] = {'package': sub_l10npack_diff, 'type': 'modified'}
                return sub_l10npack_diff.add_structure(l10nobject_diff, '/'.join(path[1:]), type)
        return True

    def remove_package(self,path):
        path = path.split('/')
        if len(path)==1:
            if path[0] in self._packages:
                del self._packages[path[0]]
                return True
        else:
            if path[0] in self._packages:
                return self._packages[path[0]]['package'].remove_package('/'.join(path[1:]))
        return False

    def remove_structure(self,path):
        path = path.split('/')
        if len(path)==1:
            if path[0] in self._structures:
                del self._structures[path[0]]
                return True
        else:
            if path[0] in self._packages:
                return self._packages[path[0]]['package'].remove_structure('/'.join(path[1:]))
        return False

    def get(self, path):
        if not path:
            return self
        elem = None
        elems = path.split('/')
        if len(elems) == 0:
            return self

        if len(elems) == 1:
            if elems[0] in self._packages:
                elem = self._packages[elems[0]]['package']
            else:
                if elems[0] in self._structures:
                    elem = self._structures[elems[0]]['struct']
            return elem
        else:
            if elems[0] in self._packages:
                return self._packages[elems[0]]['package'].get('/'.join(elems[1:]))
            else:
                return None

    def packages(self, type='all'):
        if type is 'all':
            return [self._packages[package]['package'] for package in self._packages]
        elif isinstance(type,tuple):
            return [self._packages[package]['package'] for package in self._packages if self._packages[package]['type'] in type]
        else:
            return [self._packages[package]['package'] for package in self._packages if self._packages[package]['type']==type]
    
    def structures(self, type='all', recursive=False):
        if type is 'all':
            elems = [self._structures[object]['struct'] for object in self._structures]
        elif isinstance(type,tuple):
            elems = [self._structures[object]['struct'] for object in self._structures if self._structures[object]['type'] in type]
        else:
            elems = [self._structures[object]['struct'] for object in self._structures if self._structures[object]['type']==type]
        if recursive:
            for i in self._packages:
                elems.extend(self._packages[i]['package'].structures(type=type, recursive=recursive))
        return elems

    def has_structure(self, id, type='all'):
        if id in self._structures:
            if type is 'all' or self._structures[id]['type'] is type:
                return True
        return False

    def has_package(self, id, type='all'):
        if id in self._packages:
            if type is 'all' or self._packages[id]['type'] is type:
                return True
        return False

    def structure(self, id, type='all'):
        if id in self._structures:
            if type is 'all' or self._structures[id]['type'] is type:
                return self._structures[id]['struct']
        raise KeyError('No such object: '+id)

    def package(self, id, type='all'):
        if id in self._packages:
            if type is 'all' or self._packages[id]['type'] is type:
                return self._packages[id]['package']
        raise KeyError('No such package: '+id)

    def structure_type(self, id):
        if id in self._structures:
                return self._structures[id]['type']
        return False

    def package_type(self, id):
        if id in self._packages:
                return self._packages[id]['type']
        return False

def l10npackage_diff (self, l10npack, flags=None, values=True):
    if flags == None:
        flags = ('added','removed','modified')
    l10npackage_diff = PackageDiff()
    l10npackage_diff.id = self.id
    l10npackage_diff.uri = (self.uri, l10npack.uri)
    packages1 = self.packages(names=True)
    packages2 = l10npack.packages(names=True)
    object_list1 = self.structures(names=True)
    object_list2 = l10npack.structures(names=True)

    isect = intersect(packages1, packages2)
    if 'removed' in flags:
        for item in packages1:
            if item not in isect:
                l10npackage_diff.add_package(self.package(item), type='removed')
    if 'added' in flags:
        for item in packages2:
            if item not in isect:
                l10npackage_diff.add_package(l10npack.package(item), type='added')
    if 'modified' in flags or 'unmodified' in flags:
        for item in isect:
            l10npackage_diff2 = self._packages[item].diff(l10npack._packages[item], flags=flags, values=values)
            if l10npackage_diff2:
                l10npackage_diff.add_package(l10npackage_diff2, type='modified')
    isect = intersect(object_list1, object_list2)
    if 'removed' in flags:
        for item in object_list1:
            if item not in isect:
                l10npackage_diff.add_structure(self.structure(item), type='removed')
    if 'added' in flags:
        for item in object_list2:
            if item not in isect:
                l10npackage_diff.add_structure(l10npack.structure(item), type='added')
    if 'modified' in flags or 'unmodified' in flags:
        for item in isect:
            l10nobject_diff = self._structures[item].diff(l10npack._structures[item], flags=flags, values=values)
            if l10nobject_diff:
                l10npackage_diff.add_structure(l10nobject_diff, type='modified')
    return l10npackage_diff

Package.diff = l10npackage_diff

def l10npackage_apply_diff (self, l10npackage_diff):
    for key, item in l10npackage_diff._packages.items():
        if item['type']=='added':
            self.add_package(item['package'])
        elif item['type']=='removed':
            self.remove_package(key)
        elif item['type']=='modified':
            package = self.package(key)
            package.apply_diff(item['package'])
    for key, item in l10npackage_diff._structures.items():
        if item['type']=='added':
            self.add_structure(item['struct'])
        elif item['type']=='removed':
            self.remove_structure(key)
        elif item['type']=='modified':
            object = self.structure(key)
            object.apply_diff(item['struct'])

Package.apply_diff = l10npackage_apply_diff
