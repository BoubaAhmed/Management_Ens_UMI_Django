from django.db import models
from ckeditor.fields import RichTextField
import os 

class Slide(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = RichTextField(blank=True, null=True)  
    image = models.ImageField(upload_to='static/Assets/slides/' , null=False, blank=False)
    order = models.PositiveIntegerField(default=0, help_text="Order of the slide in the carousel")

    class Meta:
        ordering = ['order']  # Ensures slides appear in the correct order

    def __str__(self):
        return self.title or f"Slide {self.id}"
    
    def delete(self, *args, **kwargs):
        # Delete the image file when the instance is deleted
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(Slide, self).delete(*args, **kwargs)

class Article(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to='static/Assets/articles/', null=False, blank=False)
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']  # Articles appear in descending order of their publish date

    def snippet(self):
        # Return a shortened version of the description (e.g., first 200 characters)
        return self.description[:200] + "..." if self.description else ""
    
    def delete(self, *args, **kwargs):
        # Delete the image file when the instance is deleted
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super(Article, self).delete(*args, **kwargs)