"""
The base class for all types of datasets.
"""
import os
import re
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional

from ..utils import SACREBLEU_DIR, download_file, smart_open


class Dataset(metaclass=ABCMeta):
    def __init__(
        self,
        name: str,
        data: Optional[List[str]] = None,
        description: Optional[str] = None,
        citation: Optional[str] = None,
        md5: Optional[List[str]] = None,
        langpairs=Dict[str, List[str]],
        **kwargs,
    ):
        """
        Params come from the values in DATASETS.

        :param name: Name of the dataset.
        :param data: URL of the raw data of the dataset.
        :param description: Description of the dataset.
        :param citation: Citation for the dataset.
        :param md5: MD5 checksum of the dataset.
        :param langpairs: List of available language pairs.
        """
        self.name = name
        self.data = data
        self.description = description
        self.citation = citation
        self.md5 = md5
        self.langpairs = langpairs
        self.kwargs = kwargs

        # Don't do any downloading or further processing now.
        # Only do that lazily, when asked.

        # where to store the dataset
        self._outdir = os.path.join(SACREBLEU_DIR, self.name)
        self._rawdir = os.path.join(self._outdir, "raw")

    def maybe_download(self):
        """
        If the dataset isn't downloaded, use utils/download_file()
        This can be implemented here in the base class. It should write
        to ~/.sacreleu/DATASET/raw exactly as it does now.
        """
        os.makedirs(self._rawdir, exist_ok=True)

        expected_checksums = self.md5 if self.md5 else [None] * len(self.data)

        for url, expected_md5 in zip(self.data, expected_checksums):
            tarball = os.path.join(self._rawdir, self._get_tarball_filename(url))

            download_file(
                url, tarball, extract_to=self._rawdir, expected_md5=expected_md5
            )

    @staticmethod
    def _clean(s):
        """
        Removes trailing and leading spaces and collapses multiple consecutive internal spaces to a single one.

        :param s: The string.
        :return: A cleaned-up string.
        """
        return re.sub(r"\s+", " ", s.strip())

    def _get_tarball_filename(self, url):
        """
        Produces a local filename for tarball.
        :param url: The url to download.
        :return: A name produced from the dataset identifier and the URL basename.
        """
        return self.name.replace("/", "_") + "." + os.path.basename(url)

    def _get_txt_file_path(self, langpair, fieldname):
        """
        Given the language pair and fieldname, return the path to the text file.
        The format is: ~/.sacrebleu/DATASET/DATASET.LANGPAIR.FIELDNAME

        :param langpair: The language pair.
        :param fieldname: The fieldname.
        :return: The path to the text file.
        """
        # handle the special case of subsets. e.g. "wmt21/dev" > "wmt21_dev"
        name = self.name.replace("/", "_")
        # Colons are used to distinguish multiple references, but are not supported in Windows filenames
        fieldname = fieldname.replace(":", "-")
        return os.path.join(self._outdir, f"{name}.{langpair}.{fieldname}")

    def _get_langpair_metadata(self, langpair):
        """
        Given a language pair, return the metadata for that language pair.
        Deal with errors if the language pair is not available.

        :param langpair: The language pair. e.g. "en-de"
        :return: Dict format which is same as self.langpairs.
        """
        if langpair is None:
            langpairs = self.langpairs
        elif langpair not in self.langpairs:
            raise Exception(f"No such language pair {self.name}/{langpair}")
        else:
            langpairs = {langpair: self.langpairs[langpair]}

        return langpairs

    @abstractmethod
    def process_to_text(self, langpair=None) -> None:
        """Processes raw files to plain text files.

        :param langpair: The language pair to process. e.g. "en-de". If None, all files will be processed.
        """
        pass

    def fieldnames(self, langpair) -> List[str]:
        """
        Return a list of all the field names. For most source, this is just
        the source and the reference. For others, it might include the document
        ID for each line, or the original language (origLang).

        get_files() should return the same number of items as this.

        :param langpair: The language pair (e.g., "de-en")
        :return: a list of field names
        """
        return ["src", "ref"]

    def __iter__(self, langpair):
        """
        Iterates over all fields (source, references, and other metadata) defined
        by the dataset.
        """
        all_files = self.get_files(langpair)
        all_fins = [smart_open(f) for f in all_files]

        for item in zip(*all_fins):
            yield item

    def source(self, langpair):
        """
        Return an iterable over the source lines.
        """
        source_file = self.get_source_file(langpair)
        with smart_open(source_file) as fin:
            for line in fin:
                yield line.strip()

    def references(self, langpair):
        """
        Return an iterable over the references.
        """
        ref_files = self.get_reference_files(langpair)
        ref_fins = [smart_open(f) for f in ref_files]

        for item in zip(*ref_fins):
            yield item

    def get_source_file(self, langpair):
        all_files = self.get_files(langpair)
        all_fields = self.fieldnames(langpair)
        index = all_fields.index("src")
        return all_files[index]

    def get_reference_files(self, langpair):
        all_files = self.get_files(langpair)
        all_fields = self.fieldnames(langpair)
        ref_files = [
            f for f, field in zip(all_files, all_fields) if field.startswith("ref")
        ]
        return ref_files

    def get_files(self, langpair):
        """
        Returns the path of the source file and all reference files for
        the provided test set / language pair.
        Downloads the references first if they are not already local.

        :param langpair: The language pair (e.g., "de-en")
        :return: a list of the source file and all reference files
        """
        fields = self.fieldnames(langpair)
        files = [self._get_txt_file_path(langpair, field) for field in fields]

        for file in files:
            if not os.path.exists(file):
                self.process_to_text(langpair)
        return files
