from django.db import models

class Image(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1023)
    date = models.DateTimeField()
    url = models.CharField(max_length=255)

class Tag(models.Model):
    name = models.CharField(max_length=80)

class ImageTag(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
