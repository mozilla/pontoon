from silme.core.list import is_entitylist
from silme.core.structure import Blob, Structure
from silme.core.types import LazyDict

class Package(object):
    """
    Package is a container that stores
    set of data structures (Structures, EntityLists, Blobs) and sub-packages.
    
    It's easiest to think of it as a filesystem directory that
    can store files and nested directories.
    It abstracts the package from the file system, so once you load
    Package into memory you can serialize it, send it,
    save as .zip file or diff.

    If you load a directory into memory and then serialize it back to disk,
    the two directories should be identical minus any modifications you made.
    """
    uri = None

    def __init__(self, id, lazy=True):
        self._structures = LazyDict() if lazy else dict()
        self._packages = LazyDict() if lazy else dict()
        self.lazy = lazy
        self.id = id

    def __len__(self):
        return len(self._packages)+len(self._structures)

    def __iter__(self):
        for i in self._packages.items():
            yield i
        for i in self._structures.items():
            yield i
        raise StopIteration

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)

    def __contains__(self, id):
        if id in self._packages.keys():
            return True
        if id in self._structures.keys():
            return True
        return False

    def __getitem__(self, key):
        try:
            return self._packages[key]
        except KeyError:
            return self._structures[key]
        except KeyError:
            raise KeyError("No such package or structure: %s" % key)

    def add_package_stub(self, id, resolver, *args, **kwargs):
        """
        Adds a package stub that will be resolved when requested for the
        first time.
        """
        if not self.lazy:
            raise Exception("Package is not lazy")
        self._packages.set_stub(id, resolver, *args, **kwargs)

    def add_structure_stub(self, id, resolver, *args, **kwargs):
        """
        Adds a structure stub that will be resolved when requested for the
        first time.
        """
        if not self.lazy:
            raise Exception("Package is not lazy")
        self._structures.set_stub(id, resolver, *args, **kwargs)

    def add_structure(self, struct, path=None):
        """
        Adds a structure to the Package.
        
        Optional parameter path allows to define exact position
        inside the package where the structure should be added.
        
        For example l10npack.add_structure(l10nstruct, 'pkg1/pkg2') is equal to
        l10npack.get_package('pkg1').get_package('pkg2').add_structure(l10nstruct)
        with the difference that it will create missing sub packages if needed.
        """
        if not path:
            self._structures[struct.id] = struct
        else:
            path = path.split('/')
            if path[0] in self._packages:
                self._packages[path[0]].add_structure(struct,
                                                      '/'.join(path[1:]))
            else:
                sub_l10n_pack = Package(path[0])
                self.add_package(sub_l10n_pack)
                sub_l10n_pack.add_structure(struct, '/'.join(path[1:]))

    def add_package(self, package, path=None):
        """
        Adds a package to Package.
        
        Optional parameter path allows to declare place
        inside the package where the subpackage should be added.
        
        For example l10npack.add_package(subl10npack, 'pkg1/pkg2') is similar to
        l10npack.get_package('pkg1').get_package('pkg2').add_package(subl10npack)
        with the difference that it will create missing sub packages.
        """
        if not path:
            self._packages[package.id] = package
        else:
            path = path.split('/')
            if path[0] in self._packages:
                self._packages[path[0]].add_package(package,
                                                    '/'.join(path[1:]))
            else:
                sub_l10n_pack = Package(path[0])
                self._packages[path[0]] = sub_l10n_pack
                sub_l10n_pack.add_package(package, '/'.join(path[1:]))

    def packages(self, ids=False):
        """
        Returns a list of packages inside Package.
        If parameter ids is set to True, a list of packages
        names is returned instead of objects.
        """
        if ids:
            return list(self._packages.keys())
        else:
            return list(self._packages.values())

    def structures(self, type='all', ids=False):
        """
        Returns a list of structures inside Package.
        If parameter ids is set to True list of
        names is returned instead of structures.
        """
        if type == 'all':
            if ids:
                return list(self._structures.keys())
            else:
                return list(self._structures.values())
        else:
            l10n_structures = {}
            if type == 'list':
                type = is_entitylist
            elif type == 'structure':
                type = lambda x:isinstance(x, Structure)
            elif type == 'blob':
                type = lambda x:isinstance(x, Blob)
            for struct in self._structures:
                if type(self._structures[struct]):
                    l10n_structures[struct] = self._structures[struct] 
            if ids:
                return list(l10n_structures.keys())
            else:
                return list(l10n_structures.values())

    def entities(self, recursive=True, path=False):
        """
        Returns a list of all entities inside the Package
        
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
            if isinstance(self._structures[i], Structure) or is_entitylist(self._structures[i]):
                elist = self._structures[i].entities()
                spath2 = '%s/%s' % (spath, i) if spath else i
                entities.extend([(e, spath2) for e in elist])
        return entities

    def has_structure(self, id):
        return id in self._structures

    def has_package(self, id):
        return id in self._packages

    def structure(self, id):
        try:
            return self._structures[id]
        except KeyError:
            raise KeyError('No such structure: %s' % id)
        
    def package(self, id):
        try:
            return self._packages[id]
        except KeyError:
            raise KeyError('No such package: %s' % id)

    def element(self, path):
        """
        Returns an element from inside Package
        by its path.
        
        l10npack.element('pkg1/pkg2/structure.po') will return
        the same as
        l10npack.package('pkg1').get_package('pkg2').structure('structure.po')
        
        If the path is empty the result will be None
        """
        if not path:
            return None
        elems = path.split('/')
        if len(elems) == 0:
            return None

        if len(elems) == 2 and elems[1] == '':
            elems = elems[:-1]

        if len(elems) == 1:
            try:
                return self.package(elems[0])
            except KeyError:
                pass
            try:
                return self.structure(elems[0])
            except KeyError:
                pass
            return None
        else:
            try:
                return self._packages[elems[0]].element('/'.join(elems[1:]))
            except KeyError:
                raise

    def remove_structure(self, id):
        del self._structures[id]
        
    def remove_package(self, id):
        del self._packages[id]

    def value(self, path, entity):
        return self.element(path).value(entity)
