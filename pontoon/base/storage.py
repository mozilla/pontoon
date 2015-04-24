from pipeline.storage import PipelineMixin
from whitenoise.django import GzipManifestStaticFilesStorage


class GzipManifestPipelineStorage(PipelineMixin, GzipManifestStaticFilesStorage):
    pass
