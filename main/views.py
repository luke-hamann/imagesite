from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

import PIL.Image

from .models import Image, Tag
from .forms import ImageForm

def detail(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    return render(request, 'detail.html', {'image': image})

def tags(request):
    tags = Tag.objects.all()
    return render(request, 'tags.html', {'tags': tags})

def upload(request):
    if (request.method == "POST"):
        form = ImageForm(request.POST, request.FILES)

        if (form.is_valid()):
            image = form.save()
            return HttpResponseRedirect(f'/view/{image.id}/')
    else:
        form = ImageForm()

    return render(request, 'upload.html', {'form': form})

def image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    format = request.GET.get('format', 'original')

    copy = PIL.Image.open(image.file).copy()
    with PIL.Image.open(image.file) as file:
        content_type = file.get_format_mimetype()
        
    return HttpResponse(image.file, content_type=content_type)

def search(request):
    images = Image.objects.all()

    return render(request, 'search.html', {'images': images})
