#!/bin/bash
#
# Copyright 2010 Zuza Software Foundation
#
# This file is part of The Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

files=$*

# local variables
message=""
body=""
failures=0
successes=0

function failure {
	pofile=$1
	body=$(echo $body; echo "<testcase classname=\"$pofile\" name=\"msgfmt\" time=\"\">\n"; echo "<failure message=\"msgfmt failure\">$message</failure>\n</testcase>\n")
	message=""
	failures=$(($failures + 1))
}

function success {
	pofile=$1
	body=$(echo $body; echo "<testcase classname=\"$pofile\" name=\"msgfmt\" time=\"\"></testcase>\n")
	message=""
	successes=$(($successes + 1))
}

function run_msgfmt {
	pofile=$1
	exit_status=$(msgfmt -cv -o /dev/null $pofile 2>/dev/null > /dev/null; echo $?)
	message=$(msgfmt -cv -o /dev/null $pofile 2>/dev/stdout | while read i; do echo "$i\n" ; done)
	return $exit_status
}

function print_header {
        echo "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
	echo "<testsuite name=\"\" errors=\"0\" failures=\"$failures\" skips=\"0\" tests=\"$((failures + successes))\" time=\"\" >"
}

function print_body {
	cat -
	echo -e $body
}

function print_footer {
	cat -
	echo "</testsuite>"
}

for pofile in $files
do
	run_msgfmt $pofile && success $pofile || failure $pofile
done

print_header |
print_body |
print_footer
