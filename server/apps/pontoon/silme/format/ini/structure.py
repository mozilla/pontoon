from silme.core.structure import Structure as BaseStructure, Comment
from silme.core.entity import is_string, is_entity

class Structure(BaseStructure):
    def __init__(self, id):
        BaseStructure.__init__(self, id)
        self.first_section = False     # did we encounter sections?

    def add(self, item, pos=None):
        """adds an element (string, entity or comment) to the Structure
        pos - if given addes an element at given position

        returns a number representing how many new elements have been added
          Usually one, but if a new string gets added and is concatanated
          to previous/next one the value will be 0.
        """
        if is_string(item):  # string
            return self.add_string(item, pos)
        elif isinstance(item, Section):  # Section
            return self.add_section(item, pos)
        elif is_entity(item):  # Entity
            return self.add_entity(item, pos)
        elif isinstance(item, Comment):  # Comment
            return self.add_comment(item, pos)
        elif item is None:
            return 0
        else:
            raise Exception('Cannot add element of type "' +
                            type(item).__name__ +
                            '" to the Structure')

    def add_section(self, section, pos=None):
        pos = self._get_pos(pos)
        if pos is None:
            self.first_section = len(self)
        elif self.first_section is False or self.first_section < pos:
            self.first_section = pos      
        self.add_at_pos(section, pos)
        return 1

    def add_entity(self, entity, pos=None):
        """adds an entity to the Structure
        pos - if given, allows decide where the entity will be added
           pos may be in form of an integer or a relative pointer like
           ('before', 'entity.id'), ('after', 'entity.id')
        """
        pos = self._get_pos(pos)
        if self.first_section is not False and \
           (pos is None or pos > self.first_section):
            raise Exception("Cannot add entity after section")
        self.add_at_pos(entity, pos)
        return 1

    def __getitem__(self, key):
        if type(key) == int:
            return list.__getitem__(self, key)
        else:
            try:
                return self.entity(key)
            except KeyError:
                pass
            try:
                return self.section(key)
            except KeyError:
                raise KeyError("No such entity or section")

    def __contains__(self, id):
        """returns True if an entity with given id exists
        """
        for item in self:
            if is_entity(item) and item.id == id:
                return True
            if isinstance(item, Section) and item.id == id:
                return True
        return False

    def section(self, key):
        """returns a section for a given id
        """
        for item in self:
            if isinstance(item, Section) and item.id == key:
                return item
        raise KeyError('No such section')


class Section(Structure):
    def add(self, item, pos=None):
        """adds an element (string, entity or comment) to the Structure
        pos - if given addes an element at given position

        returns a number representing how many new elements have been added
          Usually one, but if a new string gets added and is concatanated
          to previous/next one the value will be 0.
        """
        if is_string(item):  # string
            return self.add_string(item, pos)
        elif isinstance(item, Section):  # Section
            return self.add_section(item, pos)
        elif is_entity(item):  # Entity
            return self.add_entity(item, pos)
        elif isinstance(item, Comment):  # Comment
            return self.add_comment(item, pos)
        elif item is None:
            return 0
        else:
            raise Exception('Cannot add element of type "' +
                            type(item).__name__ +
                            '" to the Structure')

