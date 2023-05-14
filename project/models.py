from django.db import models
from django.forms import CharField
from django.utils import timezone

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='')
    password = models.CharField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    salt = models.CharField(max_length=1023)
    def __str__(self):
        return '%s - %s' % (self.username, self.email)
class Shelter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shelters", default='')
    name = models.CharField(max_length=60)
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='')
    address = models.CharField(max_length=60, unique=True)
    city = models.CharField(max_length=60, default='')
    additional_info = models.CharField(max_length=300, blank=True)
    def __str__(self):
        return f'{self.name}'
class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donations", default='')
    item = models.CharField(max_length=30)
    address = models.CharField(max_length=60)
    city = models.CharField(max_length=60, default='')
    time_range = models.CharField(max_length=60)
    condition = models.CharField(max_length=300)
    def __str__(self):
        return f'{self.item} - {self.condition}'

class Dog(models.Model):
    URGENCY = [
        (1, 'Urgent'),
        (2, 'Needs to be adopted soon'),
        (3, 'Not urgent')
    ]
    STATUS = [
        (1, 'Available'),
        (2, 'Adopted'),
        (3, 'Euthanized')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dogs", default='')
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name="dogs", default='')
    name = models.CharField(max_length=60)
    image = models.ImageField(upload_to='media')
    urgency = models.IntegerField(default=3, choices=URGENCY)
    description = models.CharField(max_length=10000)
    status = models.IntegerField(default=1, choices=STATUS)

    def __str__(self):
        return f'{self.name} - {self.shelter}'

class Adoption(models.Model):
    date = models.DateField(default=timezone.now)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE, related_name="adoptions", default='')
    def __str__(self):
        return f'{self.dog} - {self.date}'
    
class Euthanization(models.Model):
    date = models.DateField(default=timezone.now)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE, related_name="euthanizations", default='')
    def __str__(self):
        return f'{self.dog} - {self.date}'