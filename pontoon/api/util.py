from graphql.language.ast import FragmentSpread


def get_fields(info):
    """
    Parses a query info into a list of composite field names.
    For example the following query:
        {
          carts {
            edges {
              node {
                id
                name
                ...cartInfo
              }
            }
          }
        }
        fragment cartInfo on CartType { whatever }

    Will result in an array:
        [
            'carts',
            'carts.edges',
            'carts.edges.node',
            'carts.edges.node.id',
            'carts.edges.node.name',
            'carts.edges.node.whatever'
        ]
    """
    fragments = info.fragments

    def iterate_field_names(prefix, field):
        name = field.name.value

        if isinstance(field, FragmentSpread):
            results = []
            new_prefix = prefix
            sub_selection = fragments[field.name.value].selection_set.selections
        else:
            results = [prefix + name]
            new_prefix = prefix + name + "."
            sub_selection = field.selection_set.selections if field.selection_set else []

        for sub_field in sub_selection:
            results += iterate_field_names(new_prefix, sub_field)

        return results

    results = iterate_field_names('', info.field_asts[0])
    return results
