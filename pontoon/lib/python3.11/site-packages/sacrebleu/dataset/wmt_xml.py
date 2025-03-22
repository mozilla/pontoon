import os

import lxml.etree as ET

from ..utils import smart_open
from .base import Dataset

from collections import defaultdict


def _get_field_by_translator(translator):
    if not translator:
        return "ref"
    else:
        return f"ref:{translator}"

class WMTXMLDataset(Dataset):
    """
    The 2021+ WMT dataset format. Everything is contained in a single file.
    Can be parsed with the lxml parser.
    """
    @staticmethod
    def _unwrap_wmt21_or_later(raw_file):
        """
        Unwraps the XML file from wmt21 or later.
        This script is adapted from https://github.com/wmt-conference/wmt-format-tools

        :param raw_file: The raw xml file to unwrap.
        :return: Dictionary which contains the following fields
            (each a list with values for each sentence):
            - `src`: The source sentences.
            - `docid`: ID indicating which document the sentences belong to.
            - `origlang`: The original language of the document.
            - `domain`: Domain of the document.
            - `ref:{translator}`: The references produced by each translator.
            - `ref`: An alias for the references from the first translator.
        """
        tree = ET.parse(raw_file)
        # Find and check the documents (src, ref, hyp)
        src_langs, ref_langs, translators = set(), set(), set()
        for src_doc in tree.getroot().findall(".//src"):
            src_langs.add(src_doc.get("lang"))

        for ref_doc in tree.getroot().findall(".//ref"):
            ref_langs.add(ref_doc.get("lang"))
            translator = ref_doc.get("translator")
            translators.add(translator)

        assert (
            len(src_langs) == 1
        ), f"Multiple source languages found in the file: {raw_file}"
        assert (
            len(ref_langs) == 1
        ), f"Found {len(ref_langs)} reference languages found in the file: {raw_file}"

        src = []
        docids = []
        orig_langs = []
        domains = []

        refs = { _get_field_by_translator(translator): [] for translator in translators }

        systems = defaultdict(list)

        src_sent_count, doc_count, seen_domain = 0, 0, False
        for doc in tree.getroot().findall(".//doc"):
            # Skip the testsuite
            if "testsuite" in doc.attrib:
                continue

            doc_count += 1
            src_sents = {
                int(seg.get("id")): seg.text for seg in doc.findall(".//src//seg")
            }

            def get_sents(doc):
                return {
                    int(seg.get("id")): seg.text if seg.text else ""
                    for seg in doc.findall(".//seg")
                }

            ref_docs = doc.findall(".//ref")

            trans_to_ref = {
                ref_doc.get("translator"): get_sents(ref_doc) for ref_doc in ref_docs
            }

            hyp_docs = doc.findall(".//hyp")
            hyps = {
                hyp_doc.get("system"): get_sents(hyp_doc) for hyp_doc in hyp_docs
            }

            for seg_id in sorted(src_sents.keys()):
                # no ref translation is available for this segment
                if not any([value.get(seg_id, "") for value in trans_to_ref.values()]):
                    continue
                for translator in translators:
                    refs[_get_field_by_translator(translator)].append(
                        trans_to_ref.get(translator, {translator: {}}).get(seg_id, "")
                    )
                src.append(src_sents[seg_id])
                for system_name in hyps.keys():
                    systems[system_name].append(hyps[system_name][seg_id])
                docids.append(doc.attrib["id"])
                orig_langs.append(doc.attrib["origlang"])
                # The "domain" attribute is missing in WMT21 and WMT22
                domains.append(doc.get("domain"))
                seen_domain = doc.get("domain") is not None
                src_sent_count += 1

        fields = {"src": src, **refs, "docid": docids, "origlang": orig_langs, **systems}
        if seen_domain:
            fields["domain"] = domains
        return fields

    def _get_langpair_path(self, langpair):
        """
        Returns the path for this language pair.
        This is useful because in WMT22, the language-pair data structure can be a dict,
        in order to allow for overriding which test set to use.
        """
        langpair_data = self._get_langpair_metadata(langpair)[langpair]
        rel_path = langpair_data["path"] if isinstance(langpair_data, dict) else langpair_data[0]
        return os.path.join(self._rawdir, rel_path)

    def process_to_text(self, langpair=None):
        """Processes raw files to plain text files.

        :param langpair: The language pair to process. e.g. "en-de". If None, all files will be processed.
        """
        # ensure that the dataset is downloaded
        self.maybe_download()

        for langpair in sorted(self._get_langpair_metadata(langpair).keys()):
            # The data type can be a list of paths, or a dict, containing the "path"
            # and an override on which labeled reference to use (key "refs")
            rawfile = self._get_langpair_path(langpair)

            with smart_open(rawfile) as fin:
                fields = self._unwrap_wmt21_or_later(fin)

            for fieldname in fields:
                textfile = self._get_txt_file_path(langpair, fieldname)

                # skip if the file already exists
                if os.path.exists(textfile) and os.path.getsize(textfile) > 0:
                    continue

                with smart_open(textfile, "w") as fout:
                    for line in fields[fieldname]:
                        print(self._clean(line), file=fout)

    def _get_langpair_allowed_refs(self, langpair):
        """
        Returns the preferred references for this language pair.
        This can be set in the language pair block (as in WMT22), and backs off to the
        test-set-level default, or nothing.

        There is one exception. In the metadata, sometimes there is no translator field
        listed (e.g., wmt22:liv-en). In this case, the reference is set to "", and the
        field "ref" is returned.
        """
        defaults = self.kwargs.get("refs", [])
        langpair_data = self._get_langpair_metadata(langpair)[langpair]
        if isinstance(langpair_data, dict):
            allowed_refs = langpair_data.get("refs", defaults)
        else:
            allowed_refs = defaults
        allowed_refs = [_get_field_by_translator(ref) for ref in allowed_refs]

        return allowed_refs

    def get_reference_files(self, langpair):
        """
        Returns the requested reference files.
        This is defined as a default at the test-set level, and can be overridden per language.
        """
        # Iterate through the (label, file path) pairs, looking for permitted labels
        allowed_refs = self._get_langpair_allowed_refs(langpair)
        all_files = self.get_files(langpair)
        all_fields = self.fieldnames(langpair)
        ref_files = [
            f for f, field in zip(all_files, all_fields) if field in allowed_refs
        ]
        return ref_files

    def fieldnames(self, langpair):
        """
        Return a list of all the field names. For most source, this is just
        the source and the reference. For others, it might include the document
        ID for each line, or the original language (origLang).

        get_files() should return the same number of items as this.

        :param langpair: The language pair (e.g., "de-en")
        :return: a list of field names
        """
        self.maybe_download()
        rawfile = self._get_langpair_path(langpair)

        with smart_open(rawfile) as fin:
            fields = self._unwrap_wmt21_or_later(fin)

        return list(fields.keys())
