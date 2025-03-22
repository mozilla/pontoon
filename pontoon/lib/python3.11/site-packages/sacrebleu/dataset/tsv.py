import os

from ..utils import smart_open
from .base import Dataset


class TSVDataset(Dataset):
    """
    The format used by the MTNT datasets. Data is in a single TSV file.
    """

    @staticmethod
    def _split_index_and_filename(meta, field):
        """
        Splits the index and filename from a metadata string.

        e.g. meta="3:en-de.tsv", filed=[Any value] -> (3, "en-de.tsv")
             "en-de.tsv", filed="src" -> (1, "en-de.tsv")
             "en-de.tsv", filed="tgt" -> (2, "en-de.tsv")
        """
        arr = meta.split(":")
        if len(arr) == 2:
            try:
                index = int(arr[0])
            except ValueError:
                raise Exception(f"Invalid meta for TSVDataset: {meta}")
            return index, arr[1]

        else:
            index = 0 if field == "src" else 1
            return index, meta

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

            for field, origin_file, meta in zip(
                fieldnames, origin_files, langpairs[langpair]
            ):
                index, origin_file = self._split_index_and_filename(meta, field)

                origin_file = os.path.join(self._rawdir, origin_file)
                output_file = self._get_txt_file_path(langpair, field)

                with smart_open(origin_file) as fin:
                    with smart_open(output_file, "wt") as fout:
                        for line in fin:
                            # be careful with empty source or reference lines
                            # MTNT2019/ja-en.final.tsv:632 `'1033\t718\t\t\n'`
                            print(line.rstrip("\n").split("\t")[index], file=fout)
