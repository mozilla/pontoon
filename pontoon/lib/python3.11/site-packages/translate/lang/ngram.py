#
# Copyright (c) 2006 Thomas Mangin
# Copyright (c) 2009-2010 Zuza Software Foundation
#
# This program is distributed under Gnu General Public License
# (cf. the file COPYING in distribution). Alternatively, you can use
# the program under the conditions of the Artistic License (as Perl).
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

"""
Ngram models for language guessing.

.. note:: Orignal code from http://thomas.mangin.me.uk/data/source/ngram.py
"""

import glob
import re
import sys
from os import path

nb_ngrams = 400
white_space_re = re.compile(r"\s+")


class _NGram:
    def __init__(self, arg=None):
        if isinstance(arg, str):
            self.addText(arg)
            self.normalise()
        elif isinstance(arg, dict):
            # This must already be normalised!
            self.ngrams = arg
        else:
            self.ngrams = {}

    def addText(self, text):
        ngrams = {}

        for word in white_space_re.split(text):
            word = f"_{word}_"
            size = len(word)
            for i in range(size - 1):
                for s in (1, 2, 3, 4):
                    end = i + s
                    if end >= size:
                        break
                    sub = word[i:end]

                    if sub not in ngrams:
                        ngrams[sub] = 0
                    ngrams[sub] += 1

        self.ngrams = ngrams
        return self

    def sorted_by_score(self):
        sorted = [(self.ngrams[k], k) for k in self.ngrams]
        sorted.sort()
        sorted.reverse()
        return sorted[:nb_ngrams]

    def normalise(self):
        ngrams = {}
        for count, (v, k) in enumerate(self.sorted_by_score()):
            ngrams[k] = count

        self.ngrams = ngrams
        return self

    def addValues(self, key, value):
        self.ngrams[key] = value
        return self

    def compare(self, ngram):
        d = 0
        ngrams = ngram.ngrams
        for k in self.ngrams:
            if k in ngrams:
                d += abs(ngrams[k] - self.ngrams[k])
            else:
                d += nb_ngrams
        return d


class NGram:
    def __init__(self, folder, ext=".lm"):
        self.ngrams = {}
        folder = path.join(folder, "*" + ext)
        size = len(ext)

        for fname in glob.glob(path.normcase(folder)):
            lang = path.split(fname)[-1][:-size]
            ngrams = {}
            try:
                with open(fname, encoding="utf-8") as fp:
                    for i, line in enumerate(fp):
                        ngram, _t, _f = line.partition("\t")
                        ngrams[ngram] = i
            except UnicodeDecodeError:
                continue

            if ngrams:
                self.ngrams[lang] = _NGram(ngrams)

        if not self.ngrams:
            raise ValueError("no language files found")

    def classify(self, text):
        ngram = _NGram(text)
        r = "guess"

        min = sys.maxsize

        for lang in self.ngrams:
            d = self.ngrams[lang].compare(ngram)
            if d < min:
                min = d
                r = lang

        if min > 0.8 * (nb_ngrams**2):
            r = ""
        return r


class Generate:
    def __init__(self, folder, ext=".txt"):
        self.ngrams = {}
        folder = path.join(folder, "*" + ext)
        size = len(ext)

        for fname in glob.glob(path.normcase(folder)):
            lang = path.split(fname)[-1][:-size]
            n = _NGram()

            with open(fname, encoding="utf-8") as fp:
                for line in fp:
                    n.addText(line)

            n.normalise()
            self.ngrams[lang] = n

    def save(self, folder, ext=".lm"):
        for lang in self.ngrams:
            fname = path.join(folder, lang + ext)
            with open(fname, mode="w", encoding="utf-8") as fp:
                for v, k in self.ngrams[lang].sorted_by_score():
                    fp.write("%s\t %d\n" % (k, v))


if __name__ == "__main__":
    # Should you want to generate your own .lm files
    # conf = Generate('/tmp')
    # conf.save('/tmp')

    text = sys.stdin.readline()
    from translate.misc.file_discovery import get_abs_data_filename

    lm = NGram(get_abs_data_filename("langmodels"))
    print(lm.classify(text))  # noqa: T201
