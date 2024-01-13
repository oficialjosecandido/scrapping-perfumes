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
    le_nez = models.CharField(max_length=3000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=3000, null=True, blank=True)
    top_notes = models.CharField(max_length=3000, null=True, blank=True)
    middle_notes = models.CharField(max_length=3000, null=True, blank=True)
    base_notes = models.CharField(max_length=3000, null=True, blank=True)
    olfactory_family = models.CharField(max_length=3000, null=True, blank=True)
    accords = models.TextField(null=True, blank=True)
    similar = models.TextField(null=True, blank=True)
    views = models.IntegerField(default=0)

    fragrantica_url = models.CharField(max_length=3000, null=True, blank=True)

    updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.model} from {self.brand} was updated at {self.updated.strftime('%Y-%m-%d %H:%M:%S')}"
    
class Brand(models.Model):
    name = models.CharField(max_length=3000, null=True, blank=True)
    logo = models.CharField(max_length=3000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    popular = models.BooleanField(default=False, null=True, blank=True)
    perfumes = models.IntegerField(default=0)
    fragrantica_url = models.CharField(max_length=3000, null=True, blank=True)
    updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} has {self.perfumes} perfumes was updated at {self.updated.strftime('%Y-%m-%d %H:%M:%S')}"
    

class PerfumeSize(models.Model):
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=100, null=True, blank=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    store_name = models.CharField(max_length=1000, null=True, blank=True)
    store_url = models.CharField(max_length=100, null=True, blank=True)
    ean = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.perfume.model} at {self.store_name} - Price: {self.price}, EAN: {self.ean}"