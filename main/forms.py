from django import forms

class ImageForm(forms.Form):
    file = forms.ImageField()
    title = forms.CharField(max_length=100)
    tags = forms.CharField(max_length=1000)
    description = forms.CharField(max_length=1000, widget=forms.Textarea,
                                  required=False)
