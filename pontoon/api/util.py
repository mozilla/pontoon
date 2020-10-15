from graphql.language.ast import FragmentSpread


def get_fields(info):
    """Return a list of composite field names.

    Parse a GraphQL query into a flat list of all paths and leaves.

    For example the following query:

        {
          projects {
            name
            slug
            ...stats
          }
        }

        fragment stats on Project {
          totalStrings
          missingStrings
        }

    Will result in an array:

        [
            'projects',
            'projects.name',
            'projects.slug',
            'projects.totalStrings',
            'projects.missingStrings'
        ]
    """

    def iterate_field_names(prefix, field):
        name = field.name.value

        if isinstance(field, FragmentSpread):
            results = []
            new_prefix = prefix
            sub_selection = info.fragments[name].selection_set.selections
        else:
            results = [prefix + name]
            new_prefix = prefix + name + "."
            if field.selection_set:
                sub_selection = field.selection_set.selections
            else:
                sub_selection = []

        for sub_field in sub_selection:
            results += iterate_field_names(new_prefix, sub_field)

        return results

    results = []
    for field_ast in info.field_asts:
        results.extend(iterate_field_names("", field_ast))

    return results
