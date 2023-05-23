from itertools import product
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from store.admin import ProductAdmin, ProductImageInLine
from store.models import Product
from tags.models import TaggedItem
from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )
     

class TagInLine(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem

class CustomProductAdmin(ProductAdmin):
    inlines = [TagInLine , ProductImageInLine]

admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)