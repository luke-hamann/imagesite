from django.forms import Form, ModelForm
from .models import Image

class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'description', 'tags', 'file']
