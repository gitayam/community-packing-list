from django.contrib import admin
from .models import Item, Price, UserProfile

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('item', 'price', 'store_name', 'submitted_by_name', 'submitted_at', 'upvotes', 'downvotes')
    readonly_fields = ('item', 'submitted_by_name', 'submitted_at')

    def get_readonly_fields(self, request, obj=None):
        if obj: # obj is not None, so this is an existing object
            return self.readonly_fields
        return () # No readonly fields for new objects

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'reputation_score')
    readonly_fields = ('reputation_score',)
