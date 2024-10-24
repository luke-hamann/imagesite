from datetime import datetime
import io
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
import PIL.Image
from .models import Image, Tag
from .forms import ImageForm

def image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    format = request.GET.get('format', 'original')

    im = PIL.Image.open(image.file)

    content_type = im.get_format_mimetype()
    file_extension = content_type.split("/")[1]

    buffer = io.BytesIO()

    match format:
        case 'thumbnail':
            im.thumbnail((128, 128))
        case 'theater':
            im.thumbnail((1920, 1920))

    im.save(buffer, file_extension)
    content = buffer.getvalue()

    return HttpResponse(content, content_type=content_type)

def detail(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    return render(request, 'detail.html', {'image': image})

def tags(request):
    all_tags = Tag.objects.all().order_by('name')
    paginator = Paginator(all_tags, 10)

    try:
        page_number = int(request.GET.get('p', 1))
    except:
        page_number = 1
    
    page = paginator.get_page(page_number)
    tags = page.object_list

    context = {
        'tags': tags,
        'page': page
    }

    return render(request, 'tags.html', context)

def upload(request):
    if (request.method == "POST"):
        form = ImageForm(request.POST, request.FILES)

        if (form.is_valid()):
            image = form.save()
            return HttpResponseRedirect(f'/detail/{image.id}/')
    else:
        form = ImageForm()

    return render(request, 'upload.html', {'form': form})

def delete(request, image_id):
    image = get_object_or_404(Image, pk=image_id)

    if (request.method == "POST"):
        image.delete()
        return HttpResponseRedirect(f'/search/')
    else:
        context = {'image': image}
        return render(request, 'delete.html', context)

def search(request):
    query = request.GET.get('q', '')
    images = Image.objects.all()

    context = {
        'query': query,
        'images': images
    }

    return render(request, 'search.html', context)
