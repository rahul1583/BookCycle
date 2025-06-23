from django.contrib import admin
from .models import Book, Category, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'availability_status', 'price', 'rating')
    list_filter = ('category', 'availability_status', 'language')
    search_fields = ('title', 'author', 'isbn', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publication_date'
    ordering = ('-created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'user__username', 'comment')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
