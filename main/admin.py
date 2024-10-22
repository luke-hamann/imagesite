from django.contrib import admin

from .models import Image, Tag, ImageTag

admin.site.register(Image)
admin.site.register(Tag)
admin.site.register(ImageTag)
