from .fake_sgml import FakeSGMLDataset


class IWSLTXMLDataset(FakeSGMLDataset):
    """IWSLT dataset format. Can be parsed with the lxml parser."""

    # Same as FakeSGMLDataset. Nothing to do here.
    pass
