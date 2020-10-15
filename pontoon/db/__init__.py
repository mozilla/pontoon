from django.db.models import Func
from django.db.models.lookups import (
    Field,
    IContains,
)


class LevenshteinDistance(Func):
    """
    Calculate the Levenshtein distance between an expression and a string.
    """

    function = "levenshtein"
    arity = 5


class IContainsCollate(IContains):
    """
    Searching for translations may produce invalid results if you don't specify a correct
    database collation. This filter requires a tuple with search phrase and collation to apply.

    E.g. translation__string__icontains_collate=('search_phrase', 'tr_tr')

    **Warning** For the sake of security, collation shouldn't be provided from the unvalidated
    input data.

    Reference bug:
    https://bugzilla.mozilla.org/show_bug.cgi?id=1346180
    """

    def __init__(self, lhs, rhs):
        if len(rhs) == 2 and not isinstance(rhs, str):
            rhs, self.collation = rhs
        else:
            raise ValueError("You have to pass collation in order to use this lookup.")

        super(IContainsCollate, self).__init__(lhs, rhs)

    def process_lhs(self, qn, connection):
        lhs, params = super(IContainsCollate, self).process_lhs(qn, connection)
        if self.collation:
            lhs = lhs.replace("::text", '::text COLLATE "{}"'.format(self.collation))
            if "::text" not in lhs:
                lhs = lhs.replace(
                    '."{}"'.format(self.lhs.target.column),
                    '."{}"::text COLLATE "{}"'.format(
                        self.lhs.target.column, self.collation
                    ),
                )
        return lhs, params

    def get_rhs_op(self, connection, rhs):
        value = super(IContainsCollate, self).get_rhs_op(connection, rhs)
        if self.collation:
            return value.replace("%s", '%s COLLATE "{}"'.format(self.collation))
        return value


Field.register_lookup(IContainsCollate, lookup_name="icontains_collate")
