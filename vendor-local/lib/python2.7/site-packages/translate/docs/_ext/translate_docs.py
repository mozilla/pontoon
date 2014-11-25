#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
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

"""Sphinx extension with custom stuff for Translate Toolkit docs."""

import docutils


def setup(app):
    # :opt: to mark options -P --pot and options values --progress=dots
    app.add_generic_role(
        name="opt",
        nodeclass=docutils.nodes.literal
    )
