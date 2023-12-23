from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    role = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        permissions = []


class Perfume(models.Model):
    identifier = models.CharField(max_length=300)
    brand = models.CharField(max_length=300)
    model = models.CharField(max_length=300)
    year = models.CharField(max_length=4)
    top_notes = models.TextField(null=True, blank=True)
    middle_notes = models.TextField(null=True, blank=True)
    base_notes = models.TextField(null=True, blank=True)
    olfactory_family = models.TextField(null=True, blank=True)
    accords = models.TextField(null=True, blank=True)

    love = models.IntegerField(default=0)
    like = models.IntegerField(default=0)
    ok = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    hate = models.IntegerField(default=0)

    winter = models.IntegerField(default=0)
    spring = models.IntegerField(default=0)
    summer = models.IntegerField(default=0)
    fall = models.IntegerField(default=0)

    day = models.IntegerField(default=0)
    night = models.IntegerField(default=0)

    rating = models.IntegerField(default=0)
    rating_votes = models.IntegerField(default=0)

    views = models.IntegerField(default=0)

    EAN = models.IntegerField(default=0)

    fragrantica_url = models.TextField(null=True, blank=True)
    sephora_uk_url = models.TextField(null=True, blank=True)
    perfumesclub_uk_url = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.model} de {self.brand} tem {self.views} views"
    

class Brand(models.Model):
    name = models.CharField(max_length=3000, null=True, blank=True)
    logo = models.CharField(max_length=3000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    fragrantica_url = models.CharField(max_length=3000, null=True, blank=True)
    updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} was updated at {self.updated.strftime('%Y-%m-%d %H:%M:%S')}"