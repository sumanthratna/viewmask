from django.db import models
from django.contrib.auth.models import User


class AnnotatedImage(models.Model):
    # SHA hash of (image object and current time):
    unique_id = models.CharField(max_length=255)

    # @sumanthratna: I haven't yet tested if Pillow works with SVS images
    # TODO: if it doesn't work, just switch to FileField
    # https://github.com/django/django/blob/a8473b4d348776d823b7a83c1795279279cf3ab5/django/forms/fields.py#L609-L665
    # https://stackoverflow.com/a/7901240/7127932
    # we could also automatically convert each SVS to a dzi, zarr, npy, etc.
    # but I'm not sure if Pillow will understand these image formats
    # we could write our own model field that verifies whatever format we use
    # Django also sometimes tries to load the image into memory when verifying
    # we're probably better off using FileField
    image = models.ImageField(upload_to='uploaded_images/')

    # TODO: do we need unique_id? we could just use annotated_image.image.name
    # https://docs.djangoproject.com/en/3.0/ref/files/file/#django.core.files.File.name
    # https://docs.djangoproject.com/en/3.0/topics/files/#using-files-in-models

    # https://docs.djangoproject.com/en/3.0/topics/db/examples/many_to_many/
    users = models.ManyToManyField(User)
