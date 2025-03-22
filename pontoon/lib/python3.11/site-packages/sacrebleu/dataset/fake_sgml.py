import os
import re

from ..utils import smart_open
from .base import Dataset


class FakeSGMLDataset(Dataset):
    """
    The fake SGML format used by WMT prior to 2021. Can't be properly parsed.
    Source and reference(s) in separate files.
    """

    def _convert_format(self, input_file_path, output_filep_path):
        """
        Extract data from raw file and convert to raw txt format.
        """
        with smart_open(input_file_path) as fin, smart_open(
            output_filep_path, "wt"
        ) as fout:
            for line in fin:
                if line.startswith("<seg "):
                    line = self._clean(re.sub(r"<seg.*?>(.*)</seg>.*?", "\\1", line))
                    print(line, file=fout)

    def _convert_meta(self, input_file_path, field, output_filep_path):
        """
        Extract metadata from document tags, projects across segments.
        """
        with smart_open(input_file_path) as fin, smart_open(
            output_filep_path, "wt"
        ) as fout:
            value = ""
            for line in fin:
                if line.startswith("<doc "):
                    match = re.search(rf'{field}="(.*?)"', line)
                    if match is not None:
                        value = match.group(1)

                elif line.startswith("<seg "):
                    # print the current value once for each field
                    print(value, file=fout)

    def process_to_text(self, langpair=None):
        """Processes raw files to plain text files.

        :param langpair: The language pair to process. e.g. "en-de". If None, all files will be processed.
        """
        # ensure that the dataset is downloaded
        self.maybe_download()
        langpairs = self._get_langpair_metadata(langpair)

        for langpair in langpairs:
            fieldnames = self.fieldnames(langpair)
            origin_files = [
                os.path.join(self._rawdir, path) for path in langpairs[langpair]
            ]

            # Add the source file three more times for docid, genre, origlang
            origin_files += [
                os.path.join(self._rawdir, langpairs[langpair][0]) for _ in range(3)
            ]

            for field, origin_file in zip(fieldnames, origin_files):

                origin_file = os.path.join(self._rawdir, origin_file)
                output_file = self._get_txt_file_path(langpair, field)

                if field.startswith("src") or field.startswith("ref"):
                    self._convert_format(origin_file, output_file)
                else:
                    # document metadata keys
                    self._convert_meta(origin_file, field, output_file)

    def fieldnames(self, langpair):
        """
        Return a list of all the field names. For most source, this is just
        the source and the reference. For others, it might include the document
        ID for each line, or the original language (origLang).

        get_files() should return the same number of items as this.
        """
        meta = self._get_langpair_metadata(langpair)
        length = len(meta[langpair])

        assert (
            length >= 2
        ), f"Each language pair in {self.name} must have at least 2 fields."

        fields = ["src"]

        if length == 2:
            fields.append("ref")
        else:
            for i, _ in enumerate(meta[langpair][1:]):
                fields.append(f"ref:{i}")

        if not self.name.startswith("wmt08"):
            fields += ["docid", "genre", "origlang"]

        return fields


class WMTAdditionDataset(FakeSGMLDataset):
    """
    Handle special case of WMT Google addition dataset.
    """

    def _convert_format(self, input_file_path, output_filep_path):
        if input_file_path.endswith(".sgm"):
            return super()._convert_format(input_file_path, output_filep_path)
        else:
            with smart_open(input_file_path) as fin:
                with smart_open(output_filep_path, "wt") as fout:
                    for line in fin:
                        print(line.rstrip(), file=fout)
