import io
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
import PIL.Image
from .models import Image, Tag
from .forms import ImageForm


def image(request: HttpRequest, image_id: int) -> HttpResponse:
    """Return a given image file, resizing it if specified"""

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


def autocomplete(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '')
    tokens = query.split(' ')

    last_token = tokens[-1]

    tags = Tag.objects
    tags = tags.filter(~Q(name__in=tokens))
    tags = tags.filter(name__startswith=last_token)
    tags = tags[:10]

    suggestions = []
    for tag in tags:
        name = tag.name
        diff = len(name) - len(last_token)
        if (diff > 0):
            suggestion = name[-diff:]
            suggestions.append(suggestion)

    context = {
        'query': query,
        'suggestions': suggestions
    }

    return render(request, 'autocomplete.html', context)


def detail(request: HttpRequest, image_id: int) -> HttpResponse:
    """Render the detail page for an individual image"""
    image = get_object_or_404(Image, pk=image_id)
    return render(request, 'detail.html', {'image': image})


def tags(request):
    all_tags = Tag.objects.all().order_by('name')
    paginator = Paginator(all_tags, 10)

    try:
        page_number = int(request.GET.get('p', 1))
    except:
        page_number = 1
    
    if (page_number < 1):
        return HttpResponseRedirect('?p=1')
    elif (page_number > paginator.num_pages):
        return HttpResponseRedirect('?p=' + str(paginator.num_pages))

    page = paginator.get_page(page_number)
    tags = page.object_list

    context = {
        'tags': tags,
        'page': page
    }

    return render(request, 'tags.html', context)


def upload(request):
    """Render the form for uploading images or accept an upload request"""

    if (request.method == "POST"):
        form = ImageForm(request.POST, request.FILES)

        if (form.is_valid()):
            image = form.save()
            return HttpResponseRedirect(f'/detail/{image.id}/')
    else:
        tags = Tag.objects.all()
        form = ImageForm()

    context = {
        'form': form,
        'tags': tags
    }

    return render(request, 'upload.html', context)


def edit(request: HttpRequest, image_id: int):
    """Render a form for editing an existing image"""

    image = get_object_or_404(Image, pk=image_id)
    form = ImageForm(instance=image)
    
    context = {
        'form': form,
        'editing': True
    }

    return render(request, 'upload.html', context)


def delete(request: HttpRequest, image_id: int):
    """Confirm the deletion of an image"""
    image = get_object_or_404(Image, pk=image_id)

    if (request.method == "POST"):
        image.delete()
        return HttpResponseRedirect(f'/search/')
    else:
        context = {'image': image}
        return render(request, 'delete.html', context)


def search(request):
    query = request.GET.get('q', '')

    try:
        page = int(request.GET.get('p', 1))
    except:
        page = 1

    tokens = query.split()
    positiveTokens = filter(lambda t : not t.startswith('-'), tokens)
    negativeTokens = filter(lambda t : t.startswith('-'), tokens)

    images = Image.objects.all()

    for token in positiveTokens:
        images = images.filter(tags__name=token)
    
    for token in negativeTokens:
        images = images.exclude(tags__name=token)

    context = {
        'query': query,
        'images': images,
    }

    return render(request, 'search.html', context)
