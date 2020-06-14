from django.db import models
from django.contrib.auth.models import User


class AnnotatedImage(models.Model):
    # SHA hash of (image object and current time):
    unique_id = models.CharField(max_length=255)

    # @sumanthratna: I haven't yet tested if Pillow works with SVS images
    # TODO: if it doesn't work, just switch to FileField
    # https://github.com/django/django/blob/a8473b4d348776d823b7a83c1795279279cf3ab5/django/forms/fields.py#L609-L665
    image = models.ImageField(upload_to='uploaded_images/')

    # https://docs.djangoproject.com/en/3.0/topics/db/examples/many_to_many/
    users = models.ManyToManyField(User)
