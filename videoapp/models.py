from django.db import models
import os

class Video(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='videos/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.title and self.file:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        
        super().save(*args, **kwargs)