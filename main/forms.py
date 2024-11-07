from django import forms

class ImageForm(forms.Form):
    file = forms.ImageField()
    title = forms.CharField()
    tags = forms.CharField(widget=forms.Textarea, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
