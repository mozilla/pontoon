import os

from django import forms
from pontoon.sync.formats import SUPPORTED_FORMAT_PARSERS


class DownloadFileForm(forms.Form):
    slug = forms.CharField()
    code = forms.CharField()
    part = forms.CharField()


class UploadFileForm(DownloadFileForm):
    uploadfile = forms.FileField()

    def clean(self):
        cleaned_data = super(UploadFileForm, self).clean()
        part = cleaned_data.get("part")
        uploadfile = cleaned_data.get("uploadfile")

        if uploadfile:
            limit = 5000

            # File size validation
            if uploadfile.size > limit * 1000:
                current = round(uploadfile.size/1000)
                message = (
                    'Upload failed. Keep filesize under {limit} kB. Your upload: {current} kB.'
                    .format(limit=limit, current=current)
                )
                raise forms.ValidationError(message)

            # File format validation
            if part:
                file_extension = os.path.splitext(uploadfile.name)[1].lower()
                part_extension = os.path.splitext(part)[1].lower()

                # For now, skip if uploading file while using subpages
                if part_extension in SUPPORTED_FORMAT_PARSERS.keys() and part_extension != file_extension:
                    message = (
                        'Upload failed. File format not supported. Use {supported}.'
                        .format(supported=part_extension)
                    )
                    raise forms.ValidationError(message)
