from django.db import models

# Create your models here.
# models.py

class UploadedFile(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='uploads/')  # media/uploads/ に保存される
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
