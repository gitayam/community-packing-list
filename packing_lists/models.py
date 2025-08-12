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
    name = models.CharField(max_length=200, verbose_name="Packing List Name")
    description = models.TextField(blank=True, null=True, default="")
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='packing_lists')
    base = models.ForeignKey('Base', on_delete=models.SET_NULL, null=True, blank=True, related_name='packing_lists')

    EVENT_TYPE_CHOICES = [
        ("school", "School"),
        ("training", "Training"),
        ("deployment", "Deployment"),
        ("other", "Other/Custom"),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default="school", help_text="Type of event this list is for.")
    custom_event_type = models.CharField(max_length=100, blank=True, null=True, help_text="If 'Other/Custom', specify type")
    last_updated = models.CharField(max_length=20, blank=True, null=True, help_text="Last update (YYYY, YYYY-MM, or YYYY-MM-DD)")
    direct_url = models.URLField(blank=True, null=True, help_text="Direct URL to the official or source list")
    uploaded_file = models.FileField(upload_to="packing_list_uploads/", blank=True, null=True, help_text="Upload a file for this list (CSV, Excel, PDF, etc.)")
    
    # Sharing functionality fields
    is_public = models.BooleanField(default=True, help_text="Allow this list to be shared publicly")
    share_slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, help_text="Unique URL slug for sharing")
    view_count = models.PositiveIntegerField(default=0, help_text="Number of times this list has been viewed")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # If user-specific lists

    def save(self, *args, **kwargs):
        # Auto-generate share_slug if not provided
        try:
            if hasattr(self, 'share_slug') and not self.share_slug:
                from django.utils.text import slugify
                import uuid
                base_slug = slugify(self.name)[:50]  # Limit length
                self.share_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        except AttributeError:
            # share_slug field doesn't exist yet (migration not applied)
            pass
        super().save(*args, **kwargs)
    
    def get_share_url(self):
        """Get the public sharing URL for this list"""
        try:
            if self.share_slug:
                from django.urls import reverse
                return reverse('public_list', kwargs={'share_slug': self.share_slug})
        except AttributeError:
            # share_slug field doesn't exist yet (migration not applied)
            pass
        return None
    
    def get_absolute_url(self):
        """Get the detail URL for this list"""
        from django.urls import reverse
        return reverse('view_packing_list', kwargs={'list_id': self.id})
    
    def increment_view_count(self):
        """Increment the view count for this list"""
        try:
            self.view_count += 1
            self.save(update_fields=['view_count'])
        except AttributeError:
            # view_count field doesn't exist yet (migration not applied)
            pass
    
    def get_completion_stats(self):
        """Get packing completion statistics"""
        total_items = self.items.count()
        packed_items = self.items.filter(packed=True).count()
        required_items = self.items.filter(required=True).count()
        packed_required = self.items.filter(packed=True, required=True).count()
        
        completion_rate = round((packed_items / total_items * 100) if total_items > 0 else 0, 1)
        required_completion_rate = round((packed_required / required_items * 100) if required_items > 0 else 0, 1)
        
        return {
            'total': total_items,
            'packed': packed_items,
            'required': required_items,
            'packed_required': packed_required,
            'completion_rate': completion_rate,
            'required_completion_rate': required_completion_rate,
        }
    
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=200, unique=True) # Ensure item names are unique
    description = models.TextField(blank=True, null=True, default="")
    image = models.ImageField(upload_to='item_images/', blank=True, null=True, help_text="Upload an image of the item")

    def __str__(self):
        return self.name
    
    def get_price_history(self, days=90):
        """Get price history for the last N days with aggregated data"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg, Min, Max, Count
        
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        return self.prices.filter(
            date_purchased__gte=cutoff_date
        ).values(
            'date_purchased'
        ).annotate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            count=Count('id')
        ).order_by('date_purchased')
    
    def get_best_prices(self, limit=5):
        """Get the best (lowest) prices with confidence weighting"""
        from django.db.models import Case, When, Value, F, FloatField
        
        return self.prices.annotate(
            weighted_price=Case(
                When(confidence='high', then=F('price') / Value(1.0)),
                When(confidence='medium', then=F('price') / Value(1.1)),
                When(confidence='low', then=F('price') / Value(1.2)),
                default=F('price') / Value(1.1),
                output_field=FloatField()
            )
        ).order_by('weighted_price', '-created_at')[:limit]
    
    def get_price_statistics(self):
        """Get comprehensive price statistics for this item"""
        from django.db.models import Avg, Min, Max, Count, StdDev
        
        stats = self.prices.aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            count=Count('id'),
            std_dev=StdDev('price')
        )
        
        # Add confidence breakdown
        confidence_breakdown = {}
        for confidence, _ in Price.CONFIDENCE_CHOICES:
            confidence_breakdown[confidence] = self.prices.filter(confidence=confidence).count()
        
        stats['confidence_breakdown'] = confidence_breakdown
        return stats

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
    CONFIDENCE_CHOICES = [
        ('high', 'High - Verified receipt/website'),
        ('medium', 'Medium - Personal observation'),
        ('low', 'Low - Estimated/heard from others')
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='prices')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1) # e.g. price for 1 item, or a pack of 3
    date_purchased = models.DateField(null=True, blank=True)
    confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES, default='medium',
                                  help_text="Confidence level in price accuracy")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # Security and accountability fields for anonymous submissions
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of submitter for abuse prevention")
    is_verified = models.BooleanField(default=False, help_text="Verified by trusted source or repeat contributor")
    flagged_count = models.PositiveIntegerField(default=0, help_text="Number of times flagged as suspicious")
    
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Who reported this price

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item', 'store']),
            models.Index(fields=['item', 'created_at']),
            models.Index(fields=['confidence']),
            models.Index(fields=['ip_address', 'created_at']),  # For rate limiting
            models.Index(fields=['flagged_count']),  # For abuse detection
        ]

    def __str__(self):
        return f"{self.item.name} at {self.store.name}: {self.price} for {self.quantity}"

    @property
    def price_per_unit(self):
        """Calculate price per individual unit"""
        return self.price / self.quantity if self.quantity > 0 else self.price

    @property
    def confidence_score(self):
        """Return numeric confidence score for sorting/comparison"""
        return {'high': 3, 'medium': 2, 'low': 1}.get(self.confidence, 2)

    @property
    def is_recent(self):
        """Check if price is from within the last 30 days"""
        from django.utils import timezone
        from datetime import timedelta
        if not self.date_purchased:
            return False
        return self.date_purchased >= timezone.now().date() - timedelta(days=30)

    @property
    def is_anonymous(self):
        """Check if this price was submitted anonymously (has IP but no user)"""
        return bool(self.ip_address and not hasattr(self, 'user'))

    @property
    def trust_score(self):
        """Get trust score for this price's IP address"""
        if not self.ip_address:
            return 0.5  # Default for no IP
        from .security import calculate_trust_score
        return calculate_trust_score(self.ip_address)

    @property
    def trust_level(self):
        """Get human-readable trust level"""
        score = self.trust_score
        if score >= 0.8:
            return "High Trust"
        elif score >= 0.6:
            return "Medium Trust" 
        elif score >= 0.4:
            return "Low Trust"
        else:
            return "Very Low Trust"

    @property
    def trust_color(self):
        """Get CSS color class for trust level"""
        score = self.trust_score
        if score >= 0.8:
            return "trust-high"
        elif score >= 0.6:
            return "trust-medium"
        elif score >= 0.4:
            return "trust-low"
        else:
            return "trust-very-low"

    def get_anonymity_info(self):
        """Get detailed anonymity and trust information"""
        if not self.is_anonymous:
            return None
            
        return {
            'is_anonymous': True,
            'trust_score': self.trust_score,
            'trust_level': self.trust_level,
            'trust_color': self.trust_color,
            'is_verified': self.is_verified,
            'flagged_count': self.flagged_count,
            'confidence_adjusted': self.confidence,
            'ip_hash': self.ip_address[-4:] if self.ip_address else "****"  # Show last 4 chars for identification
        }

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
