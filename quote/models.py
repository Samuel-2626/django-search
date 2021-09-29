from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Quote(models.Model):
    name = models.CharField(max_length=250)
    quote = models.TextField(max_length=1000)

    def __str__(self):
        return self.quote

    class Meta:
        indexes = [
            GinIndex(name="NewGinIndex", fields=[
                     'quote'], opclasses=['gin_trgm_ops'])
        ]
