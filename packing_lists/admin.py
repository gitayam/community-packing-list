from django.contrib import admin
from .models import School, Store, PackingList, Item, PackingListItem, Price, Vote

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')
    search_fields = ('name', 'address')
    fieldsets = (
        (None, {
            'fields': ('name', 'address')
        }),
        ('Coordinates (Optional)', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_address', 'city', 'state', 'zip_code')
    search_fields = ('name', 'address_line1', 'city', 'state', 'zip_code', 'country')
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code', 'country')
        }),
        ('Coordinates (Optional)', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',) # Collapsible section
        }),
        ('Legacy Address', {
            'fields': ('full_address_legacy',),
            'classes': ('collapse',)
        }),
    )

class PackingListItemInline(admin.TabularInline):
    model = PackingListItem
    extra = 1 # Number of empty forms to display

@admin.register(PackingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'description')
    list_filter = ('school',)
    search_fields = ('name', 'description')
    inlines = [PackingListItemInline]

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# I removed the PriceInline as it's not directly used here,
# but could be useful on an ItemAdmin page if desired.
# class PriceInline(admin.TabularInline):
#     model = Price
#     extra = 1

@admin.register(PackingListItem)
class PackingListItemAdmin(admin.ModelAdmin):
    list_display = ('packing_list', 'item', 'quantity', 'packed')
    list_filter = ('packing_list', 'item', 'packed')
    search_fields = ('item__name', 'packing_list__name')
    autocomplete_fields = ['item', 'packing_list']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('item', 'store', 'price', 'quantity', 'date_purchased')
    list_filter = ('store', 'date_purchased', 'item')
    search_fields = ('item__name', 'store__name')
    autocomplete_fields = ['item', 'store']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('price_display', 'is_correct_price') # Add 'user' if implemented
    list_filter = ('is_correct_price',) # Add 'user' if implemented
    autocomplete_fields = ['price'] # Add 'user' if user accounts are used

    def price_display(self, obj):
        return str(obj.price)
    price_display.short_description = "Price"

# If you prefer not to use decorators, you can use admin.site.register:
# admin.site.register(School, SchoolAdmin)
# admin.site.register(Store, StoreAdmin)
# ... and so on for all models.
