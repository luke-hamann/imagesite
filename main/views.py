import io, json

from django.core.paginator import Paginator
from django.db.models import Case, CharField, Q, Value, When
from django.db.models.functions import Lower, Substr
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render

import PIL.Image

import torch
from ram.models import ram_plus
from ram import inference_ram, get_transform

from .models import Image, Tag
from .forms import ImageForm

ENABLE_AUTOTAGGING = False
SEARCH_RESULTS_PER_PAGE = 5


if ENABLE_AUTOTAGGING:
    IMAGE_SIZE = 384
    device = torch.device('cpu')
    transform = get_transform(image_size=IMAGE_SIZE)
    model = ram_plus(pretrained='pretrained/ram_plus_swin_large_14m.pth',
        image_size=IMAGE_SIZE, vit='swin_l')
    model.eval()
    model = model.to(device)


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
        case 'search':
            im.thumbnail((256, 256))
        case 'theater':
            im.thumbnail((1080, 1080))

    im.save(buffer, file_extension)
    content = buffer.getvalue()

    return HttpResponse(content, content_type=content_type)


def autocomplete(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '')

    if (query == ''):
        suggestions = []
    else:
        tokens = query.split(' ')

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


def autotag(request: HttpRequest):
    if (request.method == 'POST'):
        if (ENABLE_AUTOTAGGING):
            file = request.FILES['file']
            image = transform(PIL.Image.open(file)).unsqueeze(0).to(device)
            result = inference_ram(image, model)
            tags = [tag.strip().replace(' ', '-') for tag in result[0].split('|')]
        else:
            tags = []
        content = json.dumps(tags)

        return HttpResponse(content, content_type='application/json')
    else:
        return Http404()


def detail(request: HttpRequest, image_id: int, slug: str = '') -> HttpResponse:
    """Render the detail page for an individual image"""
    image = get_object_or_404(Image, pk=image_id)

    if (slug != image.slug()):
        return HttpResponseRedirect(f'/detail/{image_id}/{image.slug()}/')

    return render(request, 'detail.html', {'image': image})


def tags(request):
    """Display a page listing all tags"""
    tags = Tag.objects.all().order_by('name')
    context = {'tags': tags}
    return render(request, 'tags.html', context)


def clearTags(image: Image):
    """Remove all tags from a given image"""
    for tag in image.tags.all():
        count = Image.objects.filter(tags__id=tag.id).count()
        if count == 1:
            tag.delete()


def addTags(image: Image, tagNames: list[str]):
    """Add tags to a given image"""
    clearTags(image)

    for tagName in tagNames:
        tag = Tag.objects.filter(name=tagName).first()
        if (tag == None):
            tag = Tag(name=tagName)
            tag.save()
        image.tags.add(tag.id)


def upload(request):
    """Render the form for uploading images or accept an upload request"""

    if (request.method == "POST"):
        form = ImageForm(request.POST, request.FILES)

        if (form.is_valid()):
            id: int = int(form.cleaned_data['id'])
            file = request.FILES['file']
            title: str = form.cleaned_data['title']
            tagsString: str = form.cleaned_data['tags']
            tagNames: set[str] = set(tagsString.split())
            description: str = form.cleaned_data['description']

            if (id == 0):
                image = Image(title=title, file=file, description=description)
                image.save()
            else:
                image = get_object_or_404(Image, pk=id)
                image.title = title
                image.file = file
                image.description = description
                image.tags.clear()

            for tagName in tagNames:
                tag = Tag.objects.filter(name=tagName).first()
                if (tag == None):
                    tag = Tag(name=tagName)
                    tag.save()
                image.tags.add(tag.id)
            
            image.save()

            return HttpResponseRedirect(f'/detail/{image.id}/{image.slug()}/')
    else:
        form = ImageForm()
        form.initial['id'] = 0

    context = {
        'form': form
    }

    return render(request, 'upload.html', context)


def edit(request: HttpRequest, image_id: int, slug: str):
    """Render a form for editing an existing image"""

    if (request.method == 'POST'):
        id = request.POST.get('id')
        title = request.POST.get('title')
        tags = request.POST.get('tags').split()
        description = request.POST.get('description')
        file = request.FILES.get('file')

        image = get_object_or_404(Image, pk=id)

        image.title = title
        addTags(image, tags)
        image.description = description

        if (file != None):
            image.file = file

        image.save()

        return HttpResponseRedirect(f'/detail/{image.id}/{image.slug()}/')

    image = get_object_or_404(Image, pk=image_id)

    if (slug != image.slug()):
        return HttpResponseRedirect(f'/detail/{image.id}/{image.slug()}/edit/')

    data = {
        'id': image.id,
        'file': image.file,
        'title': image.title,
        'tags': ''.join([tag.name for tag in image.tags.all()]),
        'description': image.description
    }

    form = ImageForm(data)

    context = {
        'image': image,
        'form': form
    }

    return render(request, 'edit.html', context)


def delete(request: HttpRequest, slug: str, image_id: int):
    """Confirm the deletion of an image"""
    image = get_object_or_404(Image, pk=image_id)

    if (request.method == "POST"):
        clearTags(image)
        image.delete()
        return HttpResponseRedirect('/')
    else:
        context = {'image': image}
        return render(request, 'delete.html', context)


def search(request):

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
        if (include_tags):
            databaseQuery |= Q(tags__name=token)
        if (include_titles):
            databaseQuery |= Q(title__icontains=token)
        if (include_descriptions):
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
        """
        SELECT *,
            CASE
                WHEN LOWER(title) LIKE 'a %' THEN SUBSTRING(LOWER(title), 3)
                WHEN LOWER(title) LIKE 'an %' THEN SUBSTRING(LOWER(title), 4)
                WHEN LOWER(title) LIKE 'the %' THEN SUBSTRING(LOWER(title), 5)
                ELSE LOWER(title)
            END title_normalized
        FROM public.main_image
        ORDER BY title_normalized
        """

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
