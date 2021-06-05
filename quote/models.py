from django.db import models

<<<<<<< HEAD

# Create your models here.

class Quote(models.Model):

    name = models.CharField(max_length=250)
    quote = models.TextField(max_length=1000)


=======
class Quote(models.Model):
    name = models.CharField(max_length=250)
    quote = models.TextField(max_length=1000)

>>>>>>> 79de67609188f3399d109f86fd4433abacd09efd
    def __str__(self):
        return self.quote
