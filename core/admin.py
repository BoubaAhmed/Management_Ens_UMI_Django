from django.contrib import admin
from .models import Slide, Article
from django.contrib.auth.models import Group

# Unregister the Group model
admin.site.unregister(Group)

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'image')
    list_editable = ('order',)
    ordering = ('order',)
    search_fields = ('title', 'description')  # Optional search fields
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image', 'order')
        }),
    )
  

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'is_published')  # Display specific fields in the admin panel
    list_editable = ('is_published',)
    search_fields = ('title', 'description')  # Enable search functionality
    list_filter = ('is_published', 'published_date')  # Add filtering options
    ordering = ['-published_date']  # Default ordering in the admin panel

