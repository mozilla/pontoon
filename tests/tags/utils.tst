/* -*- Mode: rst -*- */

>>> getfixture('db_doctest')

Lets add some Pontoon objects to play with.

>>> from pontoon.base.models import Locale, Project, Resource, TranslatedResource

>>> project1 = Project.objects.create(slug='tag-project-1', name='Proj 1')
>>> project2 = Project.objects.create(slug='tag-project-2', name='Proj 2')
>>> locale1 = Locale.objects.create(code='tag-locale-1', name='Locale 1')
>>> locale2 = Locale.objects.create(code='tag-locale-2', name='Locale 2')
>>> resource1 = Resource.objects.create(path='/path/to/resour.ce1', project=project1, total_strings=200)
>>> resource2 = Resource.objects.create(path='/path/to/resour.ce2', project=project2, total_strings=200)
>>> translated_resource1 = TranslatedResource.objects.create(
...     resource=resource1,
...     locale=locale1,
...     approved_strings=25,
...     translated_strings=50,
...     fuzzy_strings=100)
>>> translated_resource2 = TranslatedResource.objects.create(
...     resource=resource2,
...     locale=locale2,
...     approved_strings=25,
...     translated_strings=50,
...     fuzzy_strings=100)


Create a TagsTool
-----------------

The ``TagsTool`` provides the api for retrieving or saving information around
tags. It has a number of associated tools that provide more specific apis.

Most simply you can call

>>> from pontoon.tags.utils import TagsTool

>>> tool = TagsTool()
>>> tool
<pontoon.tags.utils.TagsTool object at ...>

This will provide you with an iterable object, the items of which will be of
type ``TagTool`` (singular), which can provide further information/stats
about a specific tag

There are no tags yet.

>>> print(list(tool))
[]


Cloning the TagsTool
--------------------

Calling an instance of the tool will clone it.

This can be useful if you have made changes and want to see these
reflected, or if you want to filter a tool further than the initially
provided arguments.

>>> newtool = tool()
>>> newtool
<pontoon.tags.utils.TagsTool object ...>

You can filter the tool by passing kwargs - eg projects, locales (which should
be lists or querysets of objects). Cloning carries these kwargs.

>>> print(newtool.projects)
None
>>> print(newtool.locales)
None

>>> newtool = newtool(projects=[project1])
>>> newtool.projects
[<Project: Proj 1>]
>>> print(newtool.locales)
None

>>> newtool = newtool(locales=[locale1])
>>> newtool.projects
[<Project: Proj 1>]
>>> newtool.locales
[<Locale: Locale 1>]


Creating tags
-------------

You can use the Django object manager to create tags for example

>>> from pontoon.tags.models import Tag

>>> Tag.objects.create(slug='foo')
<Tag: Tag object>
>>> list(Tag.objects.values_list('slug', flat=True))
[u'foo']

The tags tool also has a convenience method for creating tags, which returns
a ``TagTool`` for the new tag.

>>> tool.create('bar')
<pontoon.tags.utils.TagTool object ...>

>>> list(Tag.objects.values_list('slug', flat=True))
[u'foo', u'bar']
>>> Tag.objects.get(slug='bar').name
u'Bar'

>>> tool.create('baz', "Something else").name
'Something else'


Retrieving a ``TagTool`` object
-------------------------------

``TagTool`` provides an API for working with an individual tag.

This API should not be instantiated directly, but be derived by iterating
``TagsTool``.

You can iterate the tool itself. Only tags with associated resources are retrieved in
this way.

>>> list(tool)
[]

You can still access the other tags - the "empty" tags - by iterating the ``empty_tags`` property

>>> list(tool.empty_tags)
[<pontoon.tags.utils.TagTool object ...>, <pontoon.tags.utils.TagTool object ...>, <pontoon.tags.utils.TagTool object ...>]

You can also get a TagTool for a tag (empty or otherwise) directly by calling ``get``

>>> tag = tool.get('baz')
>>> tag
<pontoon.tags.utils.TagTool object ...>


Getting basic information about a tag
-------------------------------------

The API provides access to the tag's attributes etc

>>> tag.name
u'Something else'
>>> tag.slug
u'baz'
>>> print(tag.priority)
None
>>> print(tag.project)
None

The tag model object can also be retrieved for introspection

>>> tag.get_object()
<Tag: Tag object>


Associating resources with a tag
--------------------------------

You can see the currently associated resources by iterating the tag's
``resources`` property.

>>> list(tag.resources)
[]

You can see the resources that could be added by iterating ``addable_resources``

>>> list(tag.addable_resources)
[{'project': ..., 'path': u'/path/to/resour.ce1'}, {'project': ..., 'path': u'/path/to/resour.ce2'}]


Now we can add resources to the tag

>>> tag.add_resources(tag.addable_resources[:1])

Which we can iterate with the resources property

>>> list(tag.resources)
[<Resource: Proj 1: /path/to/resour.ce1>]

>>> list(tag.addable_resources)
[{'project': ..., 'path': u'/path/to/resour.ce2'}]

Now, the tag is no longer regarded as empty and can be seen when iterating ``TagsTool``

>>> list(tag.slug for tag in tool())
[u'baz']

And is no longer listed in empty_tags

>>> sorted(list(tag.slug for tag in tool().empty_tags))
[u'bar', u'foo']


Filtering tags by slug
----------------------

You can filter by glob-matched slug, which will again return a cloned and
filtered copy of the tool

>>> tool()[tag.slug]
<pontoon.tags.utils.TagsTool object ...>

>>> list(tag.slug for tag in tool()[tag.slug])
[u'baz']

>>> list(tool()['DOESNOTEXIST'])
[]

You can access a wrapped tag without iterating the tool by calling
get on a filtered tool.

>>> tool()['baz'].get()
<pontoon.tags.utils.TagTool object ...>

This returns the first result for the given selector and will raise
an IndexError if there are none

>>> try:
...     tool()['DOESNOTEXIST'].get()
... except IndexError:
...     print 'no such tag!'
no such tag!

Lets add some resources to another tag

>>> other_tag = list(tool()['foo'].empty_tags)[0]
>>> other_tag.add_resources(other_tag.addable_resources)

Both tags should now be available

>>> sorted(list(tag.slug for tag in tool()))
[u'baz', u'foo']


We can filter the tags using glob matching

>>> sorted(list(t.slug for t in tool()['*']))
[u'baz', u'foo']

>>> [t.slug for t in tool()['fo*']]
[u'foo']

>>> [t.slug for t in tool()['ba*']]
[u'baz']


Iterating a tag's projects
--------------------------

We can view the currently active projects for a tag

>>> tag.projects
<QuerySet [<Project: Proj 1>]>

Lets add the other resource to the tag

>>> tag.add_resources(tag.addable_resources)

And now the other project is also available

>>> tag.projects.order_by('slug')
<QuerySet [<Project: Proj 1>, <Project: Proj 2>]>

To get a breakdown of tag stats for projects we can use the ``iter_projects`` method

>>> list(tag.iter_projects())
[<pontoon.tags.utils.TaggedProject object ...>, <pontoon.tags.utils.TaggedProject object ...>]

>>> tagged_project = list(tag.iter_projects())[0]
>>> tagged_project.slug
u'tag-project-1'
>>> tagged_project.name
u'Proj 1'
>>> tagged_project.tag
u'baz'
>>> tagged_project.latest_translation
>>> tagged_project.latest_activity

We can also generate data for a progress chart about this tagged project

>>> chart = tagged_project.chart
>>> chart
<pontoon.tags.utils.TagChart object ...>
>>> chart.total_strings
200
>>> chart.approved_share
13.0
>>> chart.fuzzy_share
50.0
>>> chart.translated_share
25.0

Lets add another ``TranslatedResource`` for this ``Resource`` in a different
``Locale``

>>> translated_resource1a = TranslatedResource.objects.create(
...     resource=resource1,
...     locale=locale2,
...     approved_strings=10,
...     translated_strings=20,
...     fuzzy_strings=100)

And re-create our ``TaggedProject`` chart

>>> tag = tool()[tag.slug].get()
>>> chart = list(tag.iter_projects())[0].chart
>>> chart.total_strings
400
>>> chart.approved_share
9.0
>>> chart.fuzzy_share
50.0
>>> chart.translated_share
18.0

If we filter on `Locales`, the tag information is filtered.

>>> locale_tag = tool(locales=[locale1])[tag.slug].get()
>>> chart = list(locale_tag.iter_projects())[0].chart
>>> chart.total_strings
200
>>> chart.approved_share
13.0
>>> chart.fuzzy_share
50.0
>>> chart.translated_share
25.0


Iterating a tag's locales
-------------------------

We can view the currently active locales for a tag

>>> tag = tool()[tag.slug].get()
>>> tag.locales.order_by('code')
<QuerySet [<Locale: Locale 1>, <Locale: Locale 2>]>

>>> list(tag.iter_locales())
[<pontoon.tags.utils.TaggedLocale object ...>, <pontoon.tags.utils.TaggedLocale object ...>]

>>> tagged_locale = list(tag.iter_locales())[0]
>>> tagged_locale.code
u'tag-locale-1'
>>> tagged_locale.name
u'Locale 1'
>>> tagged_locale.tag
u'baz'
>>> tagged_locale.latest_translation
>>> tagged_locale.latest_activity

We can also generate data for a progress chart about this tagged locale

>>> chart = tagged_locale.chart
>>> chart.total_strings
200
>>> chart.approved_share
13.0
>>> chart.fuzzy_share
50.0
>>> chart.translated_share
25.0

And we can filter the information carried in the tag, eg by `Projects`

In this example "project1" has associated resources in both Locales

>>> project1_locales = list(tool(projects=[project1])[tag.slug].get().iter_locales())
>>> len(project1_locales)
2
>>> project1_locales[0].code
u'tag-locale-1'
>>> project1_locales[0].chart.total_strings
200
>>> project1_locales[1].code
u'tag-locale-2'
>>> project1_locales[1].chart.total_strings
200

Whereas "project2" only has tagged resources in one Locale

>>> project2_locales = list(tool(projects=[project2])[tag.slug].get().iter_locales())
>>> len(project2_locales)
1
>>> project2_locales[0].code
u'tag-locale-2'
>>> project2_locales[0].chart.total_strings
200


Iterating a tag's resources
---------------------------

We can view the currently active locales for a tag

>>> tag.resources.order_by('path')
<QuerySet [<Resource: Proj 1: /path/to/resour.ce1>, <Resource: Proj 2: /path/to/resour.ce2>]>

>>> list(tag.iter_resources())
[<pontoon.tags.utils.TaggedResource object ...>, <pontoon.tags.utils.TaggedResource object ...>]

>>> tagged_resource = list(tag.iter_resources())[0]
>>> tagged_resource.path
u'/path/to/resour.ce1'
>>> tagged_resource.tag
u'baz'
>>> tagged_resource.latest_translation
>>> tagged_resource.latest_activity

We can also generate data for a progress chart about this tagged resource

>>> chart = tagged_resource.chart
>>> chart
<pontoon.tags.utils.TagChart object ...>
>>> chart.total_strings
400
>>> chart.approved_share
9.0
>>> chart.fuzzy_share
50.0
>>> chart.translated_share
18.0


Restricting a tag to a `Project`
--------------------------------

A tag can be associated with a specific project.

>>> tool = TagsTool()

Adding `Resources` will then be restricted to that project.

>>> project1_tag = tool.create('project1-tag', project=project1)
>>> list(project1_tag.addable_resources)
[{'project': ..., 'path': u'/path/to/resour.ce1'}]

>>> project2_tag = tool.create('project2-tag', project=project2)
>>> list(project2_tag.addable_resources)
[{'project': ..., 'path': u'/path/to/resour.ce2'}]

And trying to add resources from another Project raises an
``InvalidProjectError``

>>> from pontoon.tags.exceptions import InvalidProjectError
>>> try:
...     project1_tag.add_resources(project2_tag.addable_resources)
... except InvalidProjectError as e:
...     print e
Cannot add Resource from Project (...) to Tag (project1-tag)
