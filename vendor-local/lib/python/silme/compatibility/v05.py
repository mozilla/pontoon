import silme.core
import silme.diff
import silme.io.clients
import silme.io.jar
import silme.io.file

#silme.core.object = silme.core.structure
silme.core.L10nObject = silme.core.Structure
silme.core.L10nPackage = silme.core.Package
silme.diff.entitylist = silme.diff.list
silme.diff.l10nobject = silme.diff.structure
silme.diff.l10nobject.L10nObjectDiff = silme.diff.StructureDiff
silme.diff.L10nPackageDiff = silme.diff.PackageDiff
silme.diff.package.L10nPackageDiff = silme.diff.PackageDiff
silme.diff.L10nPackageDiff = silme.diff.PackageDiff

def cusinit(self, id=None):

    class Packages:
        def __init__(self, pack):
            self.packages = pack

        def __getitem__(self, item):
            return self.packages[item]
    
        def __setitem__(self, item, val):
            self.packages[item] = val
    
        def __call__(self, names=False):
            if names == True:
                return self.packages.keys()
            else:
                return self.packages.values()

    class Objects:
        def __init__(self, obj):
            self.obj = obj

        def __getitem__(self, item):
            return self.obj[item]
    
        def __setitem__(self, item, val):
            self.obj[item] = val
    
        def __call__(self, type='all', names=False):
            if type == 'all':
                if names == True:
                    return self.obj.keys()
                else:
                    return self.obj.values()
            else:
                l10n_structures = {}
                if type == 'entitylist':
                    type = EntityList
                elif type == 'l10nstructure':
                    type = L10nStructure
                elif type == 'blob':
                    type = Blob
                for struct in self._structures:
                    if isinstance(self.obj[struct], type):
                        l10n_structures[struct] = self.obj[struct] 
                if names == True:
                    return l10n_structures.keys()
                else:
                    return l10n_structures.values()

    self._structures = {}
    self._packages = {}
    self.packages = Packages(self._packages)
    self.objects = Objects(self._structures)
    self.id = id

silme.core.L10nPackage.__init__ = cusinit

silme.core.EntityList.get_entity_ids = silme.core.EntityList.ids
silme.diff.PackageDiff.get_package = silme.diff.PackageDiff.package
silme.diff.PackageDiff.get_packages = silme.diff.PackageDiff.packages
silme.diff.PackageDiff.get_object_type = silme.diff.PackageDiff.structure_type
silme.diff.PackageDiff.get_package_type = silme.diff.PackageDiff.package_type
silme.diff.PackageDiff.has_object = silme.diff.PackageDiff.has_structure
silme.core.Package.has_object = silme.core.Package.has_structure
silme.diff.PackageDiff.get_objects = silme.diff.PackageDiff.structures
silme.core.Package.get_package = silme.core.Package.package
silme.core.Package.get_packages = silme.core.Package.packages
silme.core.Package.get_objects = silme.core.Package.structures
silme.diff.EntityListDiff.get_entities = silme.diff.EntityListDiff.entities
silme.core.Package.get_object = silme.core.Package.structure
silme.core.EntityList.get_entities = silme.core.EntityList.entities
silme.io.clients.IOClient.get_l10npackage = silme.io.clients.IOClient.get_package
silme.io.jar.JarClient.get_l10npackage = silme.io.jar.JarClient.get_package
silme.io.file.FileClient.get_l10npackage = silme.io.file.FileClient.get_package
silme.io.file.FileClient.get_l10nobject = silme.io.file.FileClient.get_structure
