from django import forms

class ImageForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput)
    file = forms.ImageField()
    title = forms.CharField()
    tags = forms.CharField(max_length=1000, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
