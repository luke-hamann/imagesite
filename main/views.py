import io, json

from django.core.paginator import Paginator
from django.db.models import Case, Q, When
from django.db.models.functions import Lower, Substr
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import PIL.Image

import torch
from ram.models import ram_plus
from ram import inference_ram, get_transform

from .models import Image, Tag
from .forms import ImageUploadForm


ENABLE_AUTOTAGGING = True
SEARCH_RESULTS_PER_PAGE = 10


if (ENABLE_AUTOTAGGING):
    """Initialize the image tagging model"""
    IMAGE_SIZE = 384
    device = torch.device('cpu')
    transform = get_transform(image_size=IMAGE_SIZE)
    model = ram_plus(pretrained='pretrained/ram_plus_swin_large_14m.pth',
        image_size=IMAGE_SIZE, vit='swin_l')
    model.eval()
    model = model.to(device)


def image(request: HttpRequest, image_id: int) -> HttpResponse:
    """Return the image file associated with an id, resizing it if specified"""

    image = get_object_or_404(Image, pk=image_id)
    format = request.GET.get('format', 'original')

    im = PIL.Image.open(image.file)

    match format:
        case 'thumbnail':
            im.thumbnail((128, 128))
        case 'search':
            im.thumbnail((512, 512))
        case 'theater':
            im.thumbnail((1080, 1080))

    buffer = io.BytesIO()
    content_type = im.get_format_mimetype()
    file_extension = content_type.split("/")[1]

    im.save(buffer, file_extension)
    im.close()

    return HttpResponse(buffer.getvalue(), content_type=content_type)


def autocomplete(request: HttpRequest) -> HttpResponse:
    """Provide search suggestions based on a query and existing tags"""
    query = request.GET.get('q', '')

    if (query == ''):
        suggestions = []
    else:
        tokens = query.split()

        last_token = tokens[-1]
        if (last_token.startswith('-')):
            last_token = last_token[1:]

        tags = Tag.objects.all()
        tags = tags.filter(~Q(name__in=tokens))
        tags = tags.filter(name__startswith=last_token)
        tags = tags[:7]

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


def autotag(request: HttpRequest) -> HttpResponse:
    """Generate tags for an image"""

    if (request.method != 'POST'):
        return Http404()
    
    if (not ENABLE_AUTOTAGGING):
        tags = []
    else:
        file = request.FILES.get('file', None)
        if (file == None):
            return Http404()
        
        try:
            image = transform(PIL.Image.open(file)).unsqueeze(0).to(device)
        except:
            return Http404()
        
        result = inference_ram(image, model)
        tokens = result[0].split('|')
        tags = []
        for token in tokens:
            tag = token.strip().replace(' ', '-')
            tags.append(tag)

    return HttpResponse(json.dumps(tags), content_type='application/json')


def detail(request: HttpRequest, image_id: int, slug: str = '') -> HttpResponse:
    """Render the detail page for an individual image"""
    image = get_object_or_404(Image, pk=image_id)

    if (slug != image.slug()):
        return HttpResponseRedirect(reverse('detail', kwargs={
            'image_id': image_id, 'slug': image.slug()
        }))

    return render(request, 'detail.html', {'image': image})


def tags(request: HttpRequest) -> HttpResponse:
    """Display a page listing all tags"""
    return render(request, 'tags.html', {'tags': Tag.objects.all()})


def setTags(image: Image, tagNames: list[str]) -> None:
    """Set the tags for a given image"""

    for tag in image.tags.all():
        count = Image.objects.filter(tags__id=tag.id).count()
        if count == 1:
            tag.delete()
    
    image.tags.clear()
    
    for tagName in tagNames:
        tag = Tag.objects.filter(name=tagName).first()
        if (tag == None):
            tag = Tag(name=tagName)
            tag.save()
        image.tags.add(tag.id)
    
    image.save()


def upload(request: HttpRequest) -> HttpResponse:
    """Render the form for uploading images or accept an upload request"""

    if (request.method == 'POST'):
        form = ImageUploadForm(request.POST, request.FILES)

        if (form.is_valid()):
            file = request.FILES['file']
            title: str = form.cleaned_data['title']
            tagsString: str = form.cleaned_data['tags']
            tagNames: set[str] = set(tagsString.split())
            description: str = form.cleaned_data['description']

            image = Image(file=file, title=title, description=description)
            image.save()
            setTags(image, tagNames)

            return HttpResponseRedirect(reverse('detail', kwargs={
                'image_id': image.id, 'slug': image.slug()
            }))
    else:
        form = ImageUploadForm()

    return render(request, 'upload.html', {'form': form})


def edit(request: HttpRequest, image_id: int, slug: str) -> HttpResponse:
    """Render a form for editing an image or accept an edit request"""

    image = get_object_or_404(Image, pk=image_id)

    if (request.method == 'POST'):
        title = request.POST.get('title')
        tags = request.POST.get('tags').split()
        description = request.POST.get('description')
        file = request.FILES.get('file')

        image.title = title
        setTags(image, tags)
        image.description = description

        if (file != None):
            image.file = file

        image.save()

        return HttpResponseRedirect(reverse('detail', kwargs={
            'image_id': image.id, 'slug': image.slug()
        }))

    if (slug != image.slug()):
        return HttpResponseRedirect(reverse('edit', kwargs={
            'image_id': image.id, 'slug': image.slug()
        }))

    return render(request, 'edit.html', {'image': image})


def delete(request: HttpRequest, image_id: int, slug: str) -> HttpResponse:
    """Confirm or accept the deletion of an image"""

    image = get_object_or_404(Image, pk=image_id)

    if (slug != image.slug()):
        return HttpResponseRedirect(reverse('delete', kwargs={
            'image_id': image.id, 'slug': image.slug()
        }))

    if (request.method == "POST"):
        setTags(image, [])
        image.delete()
        return HttpResponseRedirect(reverse('home'))
    else:
        return render(request, 'delete.html', {'image': image})


def search(request: HttpRequest) -> HttpResponse:
    """Process a search query and render the results"""

    # Get the search parameters
    query: str = request.GET.get('q', '')
    include_tags: str = request.GET.get('include_tags', 'on')
    include_titles: str = request.GET.get('include_titles', 'on')
    include_descriptions: str = request.GET.get('include_descriptions', 'on')
    sort_by: str = request.GET.get('sort_by', 'date')
    reverse_sort: str = request.GET.get('reverse_sort', 'on')

    try:
        page_number = int(request.GET.get('p', 1))
    except:
        page_number = 1

    tokens = query.split()

    positiveFilter = lambda token: not token.startswith('-')
    negativeFilter = lambda token: token.startswith('-')

    positiveTokens = filter(positiveFilter, tokens)
    negativeTokens = filter(negativeFilter, tokens)
    negativeTokens = map(lambda token: token[1:], negativeTokens)

    # Build the result set
    images = Image.objects.all()

    # Add positive filters
    for token in positiveTokens:
        databaseQuery = Q()
        if (include_tags == 'on'):
            databaseQuery |= Q(tags__name=token)
        if (include_titles == 'on'):
            databaseQuery |= Q(title__icontains=token)
        if (include_descriptions == 'on'):
            databaseQuery |= Q(description__icontains=token)
        images = images.filter(databaseQuery)
    
    # Add negative filters
    for token in negativeTokens:
        databaseQuery = Q()
        if (include_tags == 'on'):
            databaseQuery |= Q(tags__name=token)
        if (include_titles == 'on'):
            databaseQuery |= Q(title__icontains=token)
        if (include_descriptions == 'on'):
            databaseQuery |= Q(description__icontains=token)
        images = images.exclude(databaseQuery)

    images = images.distinct()

    # Add sorting
    if (sort_by == 'title'):
        images = images.annotate(
            title_normalized=Case(
                When(title__istartswith='a ',
                     then=Lower(Substr('title', 3))),
                When(title__istartswith='an ',
                     then=Lower(Substr('title', 4))),
                When(title__istartswith='the ',
                     then=Lower(Substr('title', 5))),
                default=Lower('title')
            )
        )
        images = images.order_by('title_normalized')
    elif (sort_by == 'date'):
        images = images.order_by('date')

    # Reverse sort
    if (reverse_sort == 'on'):
        images = images.reverse()

    # Paginate the data
    paginator = Paginator(images, SEARCH_RESULTS_PER_PAGE)
    page = paginator.get_page(page_number)

    context = {
        'query': query,
        'include_tags': include_tags,
        'include_titles': include_titles,
        'include_descriptions': include_descriptions,
        'sort_by': sort_by,
        'reverse_sort': reverse_sort,
        'page': page
    }

    return render(request, 'search.html', context)
