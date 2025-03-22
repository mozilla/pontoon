#
# Copyright 2002-2006 Zuza Software Foundation
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
Convert Gettext PO localization files to iCalendar files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/ical2po.html
for examples and usage instructions.
"""

from translate.convert import convert
from translate.storage import ical, po


class po2ical:
    """Convert a PO file and a template iCalendar file to a iCalendar file."""

    SourceStoreClass = po.pofile
    TargetStoreClass = ical.icalfile
    TargetUnitClass = ical.icalunit
    MissingTemplateMessage = "A template iCalendar file must be provided."

    def __init__(
        self,
        input_file,
        output_file,
        template_file=None,
        include_fuzzy=False,
        output_threshold=None,
    ):
        """Initialize the converter."""
        if template_file is None:
            raise ValueError(self.MissingTemplateMessage)

        self.source_store = self.SourceStoreClass(input_file)

        self.should_output_store = convert.should_output_store(
            self.source_store, output_threshold
        )
        if self.should_output_store:
            self.include_fuzzy = include_fuzzy

            self.output_file = output_file
            self.template_store = self.TargetStoreClass(template_file)
            self.output_store = self.TargetStoreClass()

            self.source_store.makeindex()

    def merge_stores(self):
        """
        Convert a source file to a target file using a template file.

        Source file is in source format, while target and template files use
        target format.
        """
        for template_unit in self.template_store.units:
            for location in template_unit.getlocations():
                if location in self.source_store.locationindex:
                    source_unit = self.source_store.locationindex[location]
                    if source_unit.isfuzzy() and not self.include_fuzzy:
                        template_unit.target = template_unit.source
                    else:
                        template_unit.target = source_unit.target
                else:
                    template_unit.target = template_unit.source

    def run(self):
        """Run the converter."""
        if not self.should_output_store:
            return 0

        self.merge_stores()
        self.template_store.serialize(self.output_file)
        return 1


def run_converter(
    inputfile, outputfile, templatefile=None, includefuzzy=False, outputthreshold=None
):
    """Wrapper around converter."""
    return po2ical(
        inputfile, outputfile, templatefile, includefuzzy, outputthreshold
    ).run()


formats = {("po", "ics"): ("ics", run_converter)}


def main(argv=None):
    parser = convert.ConvertOptionParser(
        formats, usetemplates=True, description=__doc__
    )
    parser.add_threshold_option()
    parser.add_fuzzy_option()
    parser.run(argv)


if __name__ == "__main__":
    main()
