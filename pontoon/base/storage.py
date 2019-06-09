from __future__ import absolute_import

from pipeline.storage import PipelineMixin
from whitenoise.django import GzipManifestStaticFilesStorage


class GzipManifestPipelineStorage(PipelineMixin, GzipManifestStaticFilesStorage):
    pass
