from django.db import models
from django.utils import timezone
# from django.contrib.auth.models import User # Import User if you implement user accounts

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True) # Full address, can be used for display or geocoding
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=200)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True) # Or use choices for states/provinces
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, default="USA") # Default country if applicable

    full_address_legacy = models.TextField(blank=True, null=True, help_text="For unstructured or imported addresses.")

    # GIS fields for future use (GeoDjango)
    # from django.contrib.gis.db import models as gis_models
    # location = gis_models.PointField(null=True, blank=True, srid=4326) # SRID 4326 for WGS84
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)


    def __str__(self):
        return self.name

    @property
    def formatted_address(self):
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.zip_code, self.country]
        return ", ".join(filter(None, parts)) if any(parts) else self.full_address_legacy or "No address provided"

class PackingList(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='packing_lists')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # If user-specific lists

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=200, unique=True) # Ensure item names are unique
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class PackingListItem(models.Model):
    packing_list = models.ForeignKey(PackingList, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='packing_list_items')
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    packed = models.BooleanField(default=False) # For users to check off items

    class Meta:
        unique_together = ('packing_list', 'item') # Each item should appear once per list

    def __str__(self):
        return f"{self.quantity} x {self.item.name} for {self.packing_list.name}"

class Price(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='prices')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1) # e.g. price for 1 item, or a pack of 3
    date_purchased = models.DateField(null=True, blank=True)
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Who reported this price

    def __str__(self):
        return f"{self.item.name} at {self.store.name}: {self.price} for {self.quantity}"

class Vote(models.Model):
    price = models.ForeignKey(Price, on_delete=models.CASCADE, related_name='votes')
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # User who voted, set to SET_NULL if user deleted
    is_correct_price = models.BooleanField() # True for upvote, False for downvote
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now) # Use default instead of auto_now_add for non-interactive migration

    # class Meta:
    #     unique_together = ('price', 'user') # If users must log in to vote, or one vote per IP
    #     # Or: unique_together = ('price', 'ip_address') # if anonymous but one vote per IP

    def __str__(self):
        user_info = f"by User {self.user_id}" if self.user_id else f"by IP {self.ip_address}"
        return f"{'Upvote' if self.is_correct_price else 'Downvote'} for {self.price_id} {user_info}"
