from django.db import models
from SL import algorithms
class Entry(models.Model):
    package = models.CharField(max_length=100, blank=False)
    algorithm = models.CharField(max_length=100, blank=False)
    config = models.TextField()
    checkpoint = models.TextField()

    
    # Override
    def save(self, *args, **kwargs):
        if self.algorithm not in algos:
            # Algorithm isn't defined. Raise an exception when saving to databse.
            raise ValueError("Algorithm is unknown")
        else:
            # Save to database.
            super(Entry, self).save(*args, **kwargs)
            