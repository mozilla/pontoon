#
# Copyright 2007 Zuza Software Foundation
# 2013 F Wolff
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

"""An API to provide spell checking for use in checks or elsewhere."""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

available = False

try:
    # Enchant
    from enchant import Error as EnchantError
    from enchant import checker

    available = True
    checkers = {}

    def _get_checker(lang):
        if lang not in checkers:
            try:
                checkers[lang] = checker.SpellChecker(lang)
                # some versions only report an error when checking something
                checkers[lang].check("bla")
            except EnchantError:
                # sometimes this is raised instead of DictNotFoundError
                logger.exception("Dictionary not found")
                checkers[lang] = None

        return checkers[lang]

    def check(text, lang):
        spellchecker = _get_checker(lang)
        if not spellchecker:
            return
        spellchecker.set_text(str(text))
        for err in spellchecker:
            yield err.word, err.wordpos, err.suggest()

    @lru_cache(maxsize=1024)
    def simple_check(text, lang):
        spellchecker = _get_checker(lang)
        if not spellchecker:
            return []
        spellchecker.set_text(str(text))
        return [err.word for err in spellchecker]

except ImportError:

    def check(text, lang):
        return []

    def simple_check(text, lang):
        return []
