from django.db import models


# Create your models here.

class Quote(models.Model):

    name = models.CharField(max_length=250)
    quote = models.TextField(max_length=1000)


    def __str__(self):
        return self.quote
