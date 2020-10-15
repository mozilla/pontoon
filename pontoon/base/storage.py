from pipeline.storage import PipelineMixin
from whitenoise.storage import CompressedManifestStaticFilesStorage


class CompressedManifestPipelineStorage(
    PipelineMixin, CompressedManifestStaticFilesStorage
):
    pass
