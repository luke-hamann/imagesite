# Generated by Django 5.1.2 on 2024-10-22 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remove_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='tags',
            field=models.ManyToManyField(to='main.tag'),
        ),
        migrations.DeleteModel(
            name='ImageTag',
        ),
    ]