from ..core.structure import Blob

class BlobDiff():
    def __init__(self):
        self.diff = None
        self.id = None
        self.uri = None
        
    def empty(self):
        return not bool(self.diff)

def blobdiffto (self, blob, flags=None, values=True):
    blob_diff = BlobDiff()
    blob_diff.id = self.id
    blob_diff.uri = (self.uri, blob.uri)
    if values == True:
        if self.source == blob.source:
            blob_diff.diff = None
        else:
            blob_diff.diff = True
    return blob_diff

Blob.diff = blobdiffto
