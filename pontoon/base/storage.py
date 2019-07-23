from __future__ import absolute_import

from pipeline.storage import PipelineMixin
from whitenoise.storage import CompressedManifestStaticFilesStorage


class CompressedManifestPipelineStorage(PipelineMixin, CompressedManifestStaticFilesStorage):
    pass
