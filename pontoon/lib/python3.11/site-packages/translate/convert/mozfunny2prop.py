#
# Copyright 2005, 2006 Zuza Software Foundation
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

"""Converts additional Mozilla files to properties files."""

from io import BytesIO

from translate.convert import prop2po


def inc2prop(lines):
    """Convert a .inc file with #defines in it to a properties file."""
    yield "# converted from #defines file\n"
    for line in lines:
        line = line.decode("utf-8")
        if line.startswith("# "):
            commented = True
            line = line.replace("# ", "", 1)
        else:
            commented = False
        if not line.strip():
            yield line
        elif line.startswith("#define"):
            parts = line.replace("#define", "", 1).strip().split(None, 1)
            if not parts:
                continue
            if len(parts) == 1:
                key, value = parts[0], ""
            else:
                key, value = parts
            # special case: uncomment MOZ_LANGPACK_CONTRIBUTORS
            if key == "MOZ_LANGPACK_CONTRIBUTORS":
                commented = False
            if commented:
                yield "# "
            yield f"{key} = {value}\n"
        else:
            if commented:
                yield "# "
            yield line


def it2prop(lines, encoding="cp1252"):
    """Convert a pseudo-properties .it file to a conventional properties file."""
    yield "# converted from pseudo-properties .it file\n"
    # differences: ; instead of # for comments
    #              [section] titles that we replace with # section: comments
    for line in lines:
        line = line.decode(encoding)
        if not line.strip():
            yield line
        elif line.lstrip().startswith(";"):
            yield line.replace(";", "#", 1)
        elif line.lstrip().startswith("[") and line.rstrip().endswith("]"):
            yield "# section: " + line
        else:
            yield line


def funny2prop(lines, itencoding="cp1252"):
    hashstarts = len([line for line in lines if line.startswith("#")])
    if hashstarts:
        yield from inc2prop(lines)
    else:
        yield from it2prop(lines, encoding=itencoding)


def inc2po(
    inputfile,
    outputfile,
    templatefile,
    encoding=None,
    pot=False,
    duplicatestyle="msgctxt",
):
    """Wraps prop2po but converts input/template files to properties first."""
    inputlines = inputfile.readlines()
    inputproplines = list(inc2prop(inputlines))
    inputpropfile = BytesIO("".join(inputproplines).encode())
    if templatefile is not None:
        templatelines = templatefile.readlines()
        templateproplines = list(inc2prop(templatelines))
        templatepropfile = BytesIO("".join(templateproplines).encode())
    else:
        templatepropfile = None
    return prop2po.convertprop(
        inputpropfile,
        outputfile,
        templatepropfile,
        personality="mozilla",
        pot=pot,
        duplicatestyle=duplicatestyle,
    )


def it2po(
    inputfile,
    outputfile,
    templatefile,
    encoding="cp1252",
    pot=False,
    duplicatestyle="msgctxt",
):
    """Wraps prop2po but converts input/template files to properties first."""
    inputlines = inputfile.readlines()
    inputproplines = list(it2prop(inputlines, encoding=encoding))
    inputpropfile = BytesIO("".join(inputproplines).encode())
    if templatefile is not None:
        templatelines = templatefile.readlines()
        templateproplines = list(it2prop(templatelines, encoding=encoding))
        templatepropfile = BytesIO("".join(templateproplines).encode())
    else:
        templatepropfile = None
    return prop2po.convertprop(
        inputpropfile,
        outputfile,
        templatepropfile,
        personality="mozilla",
        pot=pot,
        duplicatestyle=duplicatestyle,
    )


def ini2po(
    inputfile,
    outputfile,
    templatefile,
    encoding="UTF-8",
    pot=False,
    duplicatestyle="msgctxt",
):
    return it2po(
        inputfile=inputfile,
        outputfile=outputfile,
        templatefile=templatefile,
        encoding=encoding,
        pot=pot,
        duplicatestyle=duplicatestyle,
    )


def main(argv=None):
    import sys

    lines = sys.stdin.readlines()
    for line in funny2prop(lines):
        sys.stdout.write(line)


if __name__ == "__main__":
    main()
