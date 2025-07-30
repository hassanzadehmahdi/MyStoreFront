from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from store.models import Product
from store.admin import ProductAdmin, ProductImageInline
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
                "fields": ("username", "usable_password", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )


class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']
    min_num = 0
    max_num = 5
    extra = 0


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline, ProductImageInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)