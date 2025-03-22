#
# Copyright 2018 BhaaL
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

"""
Convert Gettext PO localization files to flat XML files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/flatxml2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import flatxml, po


class po2flatxml:
    """
    Convert to a single PO file to a single XML file, optionally
    applying modifications to a template file instead of creating
    one from scratch based on input parameters.
    """

    TargetStoreClass = flatxml.FlatXMLFile
    TargetUnitClass = flatxml.FlatXMLUnit

    def __init__(
        self,
        inputfile,
        outputfile,
        templatefile=None,
        root="root",
        value="str",
        key="key",
        ns=None,
        indent=2,
    ):
        """Initialize the converter."""
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.templatefile = templatefile

        self.value_name = value
        self.key_name = key
        self.namespace = ns

        indent_chars = None
        if indent > 0:
            indent_chars = " " * indent

        self.source_store = po.pofile(inputfile)
        self.target_store = self.TargetStoreClass(
            templatefile,
            root_name=root,
            value_name=value,
            key_name=key,
            namespace=ns,
            indent_chars=indent_chars,
        )

    def convert_unit(self, unit):
        """Convert a source format unit to a target format unit."""
        target_unit = self.TargetUnitClass(
            source=None,
            namespace=self.namespace,
            element_name=self.value_name,
            attribute_name=self.key_name,
        )
        target_unit.source = unit.source
        if unit.istranslated() or not bool(unit.source):
            target_unit.target = unit.target
        else:
            target_unit.target = unit.source
        return target_unit

    def convert_store(self):
        """Convert a single source file to a target format file."""
        for unit in self.source_store.units:
            key = unit.source
            if not key:
                continue
            target_unit = self.target_store.findid(key)
            if target_unit is None:
                target_unit = self.convert_unit(unit)
                self.target_store.addunit(target_unit)
            else:
                target_unit.target = unit.target

    def run(self):
        """Run the converter."""
        self.convert_store()

        if self.target_store.isempty():
            return 0

        self.target_store.serialize(self.outputfile)
        return 1


def run_converter(
    inputfile,
    outputfile,
    templatefile=None,
    root="root",
    value="str",
    key="key",
    ns=None,
    indent=2,
):
    """Wrapper around the converter."""
    return po2flatxml(
        inputfile, outputfile, templatefile, root, value, key, ns, indent
    ).run()


formats = {
    ("po"): ("xml", run_converter),
    ("po", "xml"): ("xml", run_converter),
}


def main(argv=None):
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )

    parser.add_option(
        "-r",
        "--root",
        action="store",
        dest="root",
        default="root",
        help='name of the XML root element (default: "root")',
    )
    parser.add_option(
        "-v",
        "--value",
        action="store",
        dest="value",
        default="str",
        help='name of the XML value element (default: "str")',
    )
    parser.add_option(
        "-k",
        "--key",
        action="store",
        dest="key",
        default="key",
        help='name of the XML key attribute (default: "key")',
    )
    parser.add_option(
        "-n",
        "--namespace",
        action="store",
        dest="ns",
        default=None,
        help="XML namespace uri (default: None)",
    )
    parser.add_option(
        "-w",
        "--indent",
        action="store",
        dest="indent",
        type="int",
        default=2,
        help="indent width in spaces, 0 for no indent (default: 2)",
    )

    parser.passthrough.append("root")
    parser.passthrough.append("value")
    parser.passthrough.append("key")
    parser.passthrough.append("ns")
    parser.passthrough.append("indent")

    parser.run(argv)


if __name__ == "__main__":
    main()
