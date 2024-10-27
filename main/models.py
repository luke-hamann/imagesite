from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name="unique_name")]
        ordering = ['name']

    def __str__(self):
        return self.name


class Image(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1023)
    date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    file = models.ImageField(upload_to='images')

    def slug(self):
        return self.title.strip().lower().replace(' ', '-')

    def tagString(self):
        return ' '.join([tag.name for tag in self.tags.all()])

    def __str__(self):
        return self.title
