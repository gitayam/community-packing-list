from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_DOWN
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
    url = models.URLField(blank=True, null=True, help_text="Store website URL")

    # GIS fields for future use (GeoDjango)
    # from django.contrib.gis.db import models as gis_models
    # location = gis_models.PointField(null=True, blank=True, srid=4326) # SRID 4326 for WGS84
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    is_online = models.BooleanField(default=False, help_text="Is this store online?")
    is_in_person = models.BooleanField(default=True, help_text="Is this store a physical location?")

    def __str__(self):
        return self.name

    @property
    def formatted_address(self):
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.zip_code]
        if any(parts) and any(p for p in parts if p):
            return ", ".join(filter(None, parts + [self.country]))
        elif self.full_address_legacy:
            return self.full_address_legacy
        else:
            return "No address provided"

    def google_maps_link(self):
        if self.formatted_address:
            import urllib.parse
            q = urllib.parse.quote(self.formatted_address)
            return f"https://www.google.com/maps/search/?api=1&query={q}"
        return None

    def apple_maps_link(self):
        if self.formatted_address:
            import urllib.parse
            q = urllib.parse.quote(self.formatted_address)
            return f"https://maps.apple.com/?q={q}"
        return None

class Base(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

PACKING_LIST_TYPE_CHOICES = [
    ("course", "Course"),
    ("selection", "Selection"),
    ("training", "Training"),
    ("deployment", "Deployment"),
    ("other", "Other"),
]

class PackingList(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, default="")
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='packing_lists')
    base = models.ForeignKey('Base', on_delete=models.SET_NULL, null=True, blank=True, related_name='packing_lists')
    type = models.CharField(max_length=20, choices=PACKING_LIST_TYPE_CHOICES, default="course")
    custom_type = models.CharField(max_length=100, blank=True, null=True, help_text="If 'Other', specify type")
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # If user-specific lists

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=200, unique=True) # Ensure item names are unique
    description = models.TextField(blank=True, null=True, default="")

    def __str__(self):
        return self.name

class PackingListItem(models.Model):
    packing_list = models.ForeignKey(PackingList, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='packing_list_items')
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True, default="")
    packed = models.BooleanField(default=False) # For users to check off items
    # New fields for structured lists:
    section = models.CharField(max_length=200, blank=True, null=True, help_text="Section or category header")
    nsn_lin = models.CharField(max_length=100, blank=True, null=True, help_text="NSN/LIN or similar code")
    required = models.BooleanField(default=True, help_text="Is this item required?")
    instructions = models.TextField(blank=True, null=True, help_text="Special notes or instructions")

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

    def save(self, *args, **kwargs):
        if self.price is not None:
            self.price = Decimal(self.price).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        super().save(*args, **kwargs)

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
        user_info = f"by IP {self.ip_address}" if self.ip_address else "by anonymous"
        return f"{'Upvote' if self.is_correct_price else 'Downvote'} for {self.price_id} {user_info}"
