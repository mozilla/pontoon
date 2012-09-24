from .entity import Entity
from .list import EntityList 
from .structure import Blob, Structure

class Package(object):
    """
    L10nPackage is a container object that stores
    set of objects (L10nStructure or Blob) and sub-l10npackages.
    
    It's easiest to think of it as a filesystem directory that
    can store files and nested directories.
    It abstracts the package from the file system, so once you load
    L10nPackage into memory you can serialize it, send it, save as .zip file or
    simply diff.
    """
    uri = None

    def __init__(self, id=None):
        self._structures = {}
        self._packages = {}
        self.id = id

    def __len__(self):
        return len(self._packages)+len(self._structures)

    def __iter__(self):
        for i in self._packages.items():
            yield i
        for i in self._structures.items():
            yield i
        raise StopIteration

    def add_structure(self, struct, path=None):
        """
        Adds an object to L10nPackage.
        
        Optional parameter path allows to declare place
        inside the package where the object should be added.
        
        For example l10npack.add_structure(l10nstruct, 'pkg1/pkg2') is similar to
        l10npack.get_package('pkg1').get_package('pkg2').add_structure(l10nstruct)
        with the difference that it will create missing sub packages.
        """
        if path == None or path == '':
            self._structures[struct.id] = struct
        else:
            path = path.split('/')
            if path[0] in self._packages:
                self._packages[path[0]].add_structure(struct, '/'.join(path[1:]))
            else:
                sub_l10n_pack = Package()
                sub_l10n_pack.id = path[0]
                self.add_package(sub_l10n_pack)
                sub_l10n_pack.add_structure(struct, '/'.join(path[1:]))

    def add_package(self, l10npackage, path=None):
        """
        Adds a package to L10nPackage.
        
        Optional parameter path allows to declare place
        inside the package where the subpackage should be added.
        
        For example l10npack.add_package(subl10npack, 'pkg1/pkg2') is similar to
        l10npack.get_package('pkg1').get_package('pkg2').add_package(subl10npack)
        with the difference that it will create missing sub packages.
        """
        if path == None or path == '':
            self._packages[l10npackage.id] = l10npackage
        else:
            path = path.split('/')
            if path[0] in self._packages:
                self._packages[path[0]].add_package(l10npackage, '/'.join(path[1:]))
            else:
                sub_l10n_pack = Package()
                sub_l10n_pack.id = path[0]
                self._packages[path[0]] = sub_l10n_pack
                sub_l10n_pack.add_package(l10npackage,'/'.join(path[1:]))

    def packages(self, names=False):
        """
        Returns a list of packages inside L10nPackage.
        If parameter names is set to True list of
        names is returned instead of objects.
        """
        if names == True:
            return self._packages.keys()
        else:
            return self._packages.values()

    def structures(self, type='all', names=False):
        """
        Returns a list of structures inside L10nPackage.
        If parameter names is set to True list of
        names is returned instead of structures.
        """
        if type == 'all':
            if names == True:
                return self._structures.keys()
            else:
                return self._structures.values()
        else:
            l10n_structures = {}
            if type == 'entitylist':
                type = EntityList
            elif type == 'l10nstructure':
                type = L10nStructure
            elif type == 'blob':
                type = Blob
            for struct in self._structures:
                if isinstance(self._structures[struct], type):
                    l10n_structures[struct] = self._structures[struct] 
            if names == True:
                return l10n_structures.keys()
            else:
                return l10n_structures.values()

    def entities(self, recursive=True, path=False):
        """
        Returns a list of all entities inside the L10nPackage
        
        If optional parameter recursive is set to True it will
        return all packages from this package and its subpackages.
        """
        entities = []
        
        
        if path is True:
            spath = ''
        elif path is not False:
            spath='%s/%s' % (path, self.id) if path else self.id
        else:
            spath = path
        if recursive:
            for pack in self._packages.values():
                entities.extend(pack.entities(path=spath))
        for i in self._structures:
            if isinstance(self._structures[i], Structure) or isinstance(self._structures[i], EntityList):
                elist = self._structures[i].entities()
                spath2 = '%s/%s' % (spath, i) if spath else i
                entities.extend([(e, spath2) for e in elist])
        return entities

    def has_structure(self, id):
        return id in self._structures

    def has_package(self, id):
        return id in self._packages

    def structure(self, id):
        if id in self._structures:
            return self._structures[id]
        raise KeyError('No such structure')
        
    def package(self, id):
        if id in self._packages:
            return self._packages[id]
        raise KeyError('No such package: %s' % id)

    def element(self, path):
        """
        Returns an element from inside L10nPackage
        by its path.
        
        l10npack.element('pkg1/pkg2/structure.po') will return
        the same as
        l10npack.package('pkg1').get_package('pkg2').structure('structure.po')
        
        IF the path is empty the result will be None
        """
        if not path:
            return None
        elems = path.split('/')
        if len(elems) == 0:
            return None

        if len(elems) == 2 and elems[1] == '':
            elems = elems[:-1]

        if len(elems) == 1:
            if self.has_package(elems[0]):
                elem = self.package(elems[0])
            elif self.has_structure(elems[0]):
                elem = self.structure(elems[0])
            else:
                return None
            return elem
        else:
            if self._packages.has_key(elems[0]):
                return self._packages[elems[0]].element('/'.join(elems[1:]))
            else:
                return None

    def remove_structure(self, id):
        del self._structures[id]
        
    def remove_package(self, id):
        del self._packages[id]

    def value(self, path, entity):
        elem = self.get_element(path)
        return elem.get_value(entity)

    def merge(self, l10n_package):
        for id in l10n_package.structures:
            struct2 = l10n_package.structure(id)
            if self.has_structure(id):
                structure = self.structure(id)
                if type(structure) is not type(struct2):
                    raise Exception('Structure type mismatch! (' + id + ': ' +
                                    type(structure) + ',' + type(struct2) + ')')
                elif not isinstance(structure, EntityList):
                    self.add_structure(struct2)
                else:
                    structure.merge(struct2)
            else:
                self.add_structure(struct2)
        for id in l10n_package.packages:
            package = l10n_package.package(id)
            if self.has_package(id):
                self.get_package(id).merge(package)
            else:
                self.add_package(package)

    def get_locales(self, localelist):
        l10n_package = L10nPackage()
        l10n_package.id = self.id
        l10n_package.uri = self.uri
        for struct in self._structures.values():
            l10n_package.add_structure(struct.locales(localelist))
        for package in self._packages.values():
            l10nPackage.add_package(package.locales(localelist))
        return l10n_package
