#
# Copyright 2022 Michal Čihař
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Module for handling ReosurceDictionary files."""

from translate.storage import flatxml


class ResourceDictionaryUnit(flatxml.FlatXMLUnit):
    """A single term in the ResourceDictionary file."""

    DEFAULT_ELEMENT_NAME = "{clr-namespace:System;assembly=mscorlib}String"
    DEFAULT_ATTRIBUTE_NAME = "{http://schemas.microsoft.com/winfx/2006/xaml}Key"


class ResourceDictionaryFile(flatxml.FlatXMLFile):
    """Class representing a ResourceDictionary file store."""

    UnitClass = ResourceDictionaryUnit
    Name = "ResourceDictionary File"
    Mimetypes = ["application/xaml+xml"]
    Extensions = ["xaml"]

    DEFAULT_ROOT_NAME = (
        "{http://schemas.microsoft.com/winfx/2006/xaml/presentation}ResourceDictionary"
    )
    DEFAULT_VALUE_NAME = "{clr-namespace:System;assembly=mscorlib}String"
    DEFAULT_KEY_NAME = "{http://schemas.microsoft.com/winfx/2006/xaml}Key"
    DEFAULT_INDENT_CHARS = "    "
    XML_DECLARATION = False
