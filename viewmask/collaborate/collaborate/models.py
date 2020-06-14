from django.db import models
from django.contrib.auth.models import User


class AnnotatedImage(models.Model):
    # SHA hash of (image object and current time):
    unique_id = models.CharField(max_length=255)

    # https://docs.djangoproject.com/en/3.0/topics/db/examples/many_to_many/
    users = models.ManyToManyField(User)
