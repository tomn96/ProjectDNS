from django import forms


class SingleUrlForm(forms.Form):
    url = forms.CharField(required=True, max_length=512, label="URL")


class UploadFileForm(forms.Form):
    file = forms.FileField()
