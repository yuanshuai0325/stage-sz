from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)

class Device(models.Model):
    name = models.CharField(max_length=30)

class Use(models.Model):
    sn = models.CharField(max_length=30)
    comment = models.CharField(max_length=50)
    user = models.ForeignKey('User',on_delete=models.CASCADE)
    device = models.ForeignKey('Device',on_delete=models.CASCADE)

class Storge(models.Model):    
    device = models.ForeignKey('Device',on_delete=models.CASCADE)
    sn = models.CharField(max_length=30)
    comment = models.CharField(max_length=50)
