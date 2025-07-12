from django import forms
from .models import PackingList, School, Price, Store, Item, PackingListItem
from datetime import date
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db.models import Avg, Min, Max
import re

# School types for 'School' event type
SCHOOL_TYPE_CHOICES = [
    ("airborne", "Airborne School"),
    ("air_assault", "Air Assault School"),
    ("jumpmaster", "Jumpmaster School"),
    ("ranger_school", "Ranger School"),
    ("pathfinder", "Pathfinder School"),
    ("sniper", "Sniper School"),
    ("mountain", "Mountain Warfare School"),
    ("sapper", "Sapper School"),
    ("cdqc", "Combat Diver Qualification Course (CDQC)"),
    ("sfqc", "Special Forces Qualification Course (SFQC)"),
    ("buds", "Basic Underwater Demolition/SEAL (BUD/S)"),
    ("sere", "Survival, Evasion, Resistance and Escape (SERE) School"),
    ("other", "Other School (specify in description)")
]
# Assessment & Selection types
ASSESSMENT_TYPE_CHOICES = [
    ("sfas", "Special Forces Assessment & Selection (SFAS)"),
    ("poas", "Psychological Operations Assessment & Selection (POAS)"),
    ("caas", "Civil Affairs Assessment & Selection (CAAS)"),
    ("rasp", "Ranger Assessment & Selection Program (RASP)"),
    ("ocs", "Officer Candidate School (OCS)"),
    ("wocs", "Warrant Officer Candidate School (WOCS)"),
    ("seal_pst", "Navy SEAL/SWCC PST (Physical Screening Test)"),
    ("recon", "Marine Corps Reconnaissance Selection"),
    ("pj_indoc", "Air Force Pararescue Indoctrination Course"),
    ("marsoc_as", "Marine Raider Assessment and Selection (MARSOC A&S)"),
    ("cct_selection", "Combat Control Selection Course"),
    ("other", "Other Assessment (specify in description)")
]
TRAINING_TYPE_CHOICES = [
    ("bct", "Basic Combat Training (BCT)"),
    ("ait", "Advanced Individual Training (AIT)"),
    ("osut", "Infantry One Station Unit Training (OSUT)"),
    ("pre_ranger", "Pre-Ranger Course"),
    ("pre_sapper", "Pre-Sapper Course"),
    ("pre_airborne", "Pre-Airborne Course"),
    ("pre_seal", "Pre-SEAL/SWCC Training"),
    ("tactical_fitness", "Tactical Fitness Course"),
    ("never_quit", "Never Quit Mindset Training Course"),
    ("other", "Other Training (specify in description)")
]
# To add more, just edit the above lists.

BRANCH_CHOICES = [
    ("all", "ALL"),
    ("army", "Army"),
    ("navy", "Navy"),
    ("marines", "Marines"),
    ("air_force", "Air Force")
]

# Mapping of type to branch for filtering
SCHOOL_TYPE_BRANCHES = {
    "airborne": ["army", "all"],
    "air_assault": ["army", "all"],
    "jumpmaster": ["army", "all"],
    "ranger_school": ["army", "all"],
    "pathfinder": ["army", "all"],
    "sniper": ["army", "marines", "all"],
    "mountain": ["army", "all"],
    "sapper": ["army", "all"],
    "cdqc": ["army", "all"],
    "sfqc": ["army", "all"],
    "buds": ["navy", "all"],
    "sere": ["army", "navy", "marines", "air_force", "all"],
    "other": ["all", "army", "navy", "marines", "air_force"]
}
ASSESSMENT_TYPE_BRANCHES = {
    "sfas": ["army", "all"],
    "poas": ["army", "all"],
    "caas": ["army", "all"],
    "rasp": ["army", "all"],
    "ocs": ["army", "navy", "marines", "air_force", "all"],
    "wocs": ["army", "all"],
    "seal_pst": ["navy", "all"],
    "recon": ["marines", "all"],
    "pj_indoc": ["air_force", "all"],
    "marsoc_as": ["marines", "all"],
    "cct_selection": ["air_force", "all"],
    "other": ["all", "army", "navy", "marines", "air_force"]
}
TRAINING_TYPE_BRANCHES = {
    "bct": ["army", "all"],
    "ait": ["army", "all"],
    "osut": ["army", "all"],
    "pre_ranger": ["army", "all"],
    "pre_sapper": ["army", "all"],
    "pre_airborne": ["army", "all"],
    "pre_seal": ["navy", "all"],
    "tactical_fitness": ["all", "army", "navy", "marines", "air_force"],
    "never_quit": ["all", "army", "navy", "marines", "air_force"],
    "other": ["all", "army", "navy", "marines", "air_force"]
}

class PackingListForm(forms.ModelForm):
    """
    Form for creating a Packing List manually.
    """
    branch = forms.ChoiceField(choices=BRANCH_CHOICES, initial='all', label="Branch", help_text="Which military branch is this list for?")
    school_name = forms.CharField(max_length=200, required=False, help_text="If your school isn't listed, enter its name here to create it.")
    uploaded_file = forms.FileField(required=False, help_text="Upload CSV, Excel, or PDF file.")
    last_updated = forms.CharField(max_length=20, required=False, help_text="Last update (YYYY, YYYY-MM, or YYYY-MM-DD)")
    direct_url = forms.URLField(required=False, help_text="Direct URL to the official or source list")
    event_type = forms.ChoiceField(choices=[('school', 'School'), ('assessment', 'Assessment & Selection'), ('training', 'Training'), ('deployment', 'Deployment'), ('other', 'Other/Custom')], initial='school', help_text="Type of event this list is for.")
    school_type = forms.ChoiceField(choices=SCHOOL_TYPE_CHOICES, required=False, help_text="Select school type", label="School Type")
    assessment_type = forms.ChoiceField(choices=ASSESSMENT_TYPE_CHOICES, required=False, help_text="Select assessment type", label="Assessment Type")
    training_type = forms.ChoiceField(choices=TRAINING_TYPE_CHOICES, required=False, help_text="Select training type", label="Training Type")
    custom_event_type = forms.CharField(max_length=100, required=False, help_text="If 'Other/Custom', specify type")

    class Meta:
        model = PackingList
        fields = ['branch', 'event_type', 'school_type', 'assessment_type', 'training_type', 'name', 'description', 'school', 'custom_event_type', 'last_updated', 'direct_url', 'uploaded_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'name': forms.TextInput(attrs={'placeholder': 'Packing List Name'}),
        }
        labels = {
            'name': 'Packing List Name',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].queryset = School.objects.all().order_by('name')
        self.fields['school'].required = False # Allow creating a list without initially assigning a school
        self.fields['custom_event_type'].widget.attrs['placeholder'] = 'Specify event type if Other/Custom'
        self.fields['school_type'].widget.attrs['style'] = 'display:none;'
        self.fields['assessment_type'].widget.attrs['style'] = 'display:none;'
        self.fields['training_type'].widget.attrs['style'] = 'display:none;'
        # Set last_updated initial value to today if not already set
        if not self.initial.get('last_updated') and not self.data.get('last_updated'):
            self.fields['last_updated'].initial = date.today().isoformat()
        # Filter type choices by branch
        branch = self.data.get('branch') or self.initial.get('branch') or 'all'
        # School types
        self.fields['school_type'].choices = [
            (k, v) for k, v in SCHOOL_TYPE_CHOICES if branch in SCHOOL_TYPE_BRANCHES.get(k, []) or branch == 'all'
        ]
        # Assessment types
        self.fields['assessment_type'].choices = [
            (k, v) for k, v in ASSESSMENT_TYPE_CHOICES if branch in ASSESSMENT_TYPE_BRANCHES.get(k, []) or branch == 'all'
        ]
        # Training types
        self.fields['training_type'].choices = [
            (k, v) for k, v in TRAINING_TYPE_CHOICES if branch in TRAINING_TYPE_BRANCHES.get(k, []) or branch == 'all'
        ]
        # Show/hide logic will be handled in the template with JS

    def clean(self):
        cleaned_data = super().clean()
        event_type = cleaned_data.get('event_type')
        custom_event_type = cleaned_data.get('custom_event_type')
        if event_type == 'other' and not custom_event_type:
            self.add_error('custom_event_type', "Please specify the event type if 'Other/Custom' is selected.")
        return cleaned_data

    def save(self, commit=True):
        # Handle creation of new school if school_name is provided
        school_name = self.cleaned_data.get('school_name')
        school = self.cleaned_data.get('school')
        if school_name and not school:
            school, created = School.objects.get_or_create(name=school_name.strip())
            self.instance.school = school
        # Handle file upload
        uploaded_file = self.cleaned_data.get('uploaded_file')
        if uploaded_file:
            self.instance.uploaded_file = uploaded_file
        return super().save(commit=commit)


class PriceForm(forms.ModelForm):
    """
    Enhanced form for adding or editing a price for an item with validation and smart features.
    """
    store_name = forms.CharField(max_length=200, required=False,
                                 help_text="If the store isn't listed, enter its name here to create it.")
    
    date_purchased = forms.DateField(
        required=False,
        label="Date of Price Confirmation",
        help_text="The date you confirmed this price (for comparing prices between stores)",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today
    )
    
    confidence = forms.ChoiceField(
        choices=[
            ('high', 'High - Verified receipt/website'),
            ('medium', 'Medium - Personal observation'),
            ('low', 'Low - Estimated/heard from others')
        ],
        initial='medium',
        required=False,
        help_text="How confident are you in this price?",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Price
        fields = ['store', 'price', 'quantity', 'date_purchased', 'confidence']
        widgets = {
            'date_purchased': forms.DateInput(attrs={'type': 'date'}),
            'price': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0.01',
                'class': 'form-control price-input',
                'placeholder': 'Enter price (e.g., 19.99)'
            }),
            'quantity': forms.NumberInput(attrs={
                'min': '1',
                'class': 'form-control',
                'placeholder': 'Quantity (e.g., 1 for single item, 3 for pack of 3)'
            })
        }

    def __init__(self, *args, **kwargs):
        self.item_instance = kwargs.pop('item_instance', None)
        super().__init__(*args, **kwargs)
        
        # Add option to create new store with smart suggestions
        popular_stores = Store.objects.all().order_by('name')
        store_choices = [('', 'Select a store...')] + [(store.id, store.name) for store in popular_stores]
        store_choices.append(('__add_new__', '➕ Add New Store...'))
        self.fields['store'].choices = store_choices
        self.fields['store'].required = False
        self.fields['date_purchased'].required = False
        
        # Add price per unit calculation in JavaScript
        self.fields['price'].widget.attrs.update({
            'data-toggle': 'price-calculator',
            'onkeyup': 'calculatePricePerUnit()'
        })
        self.fields['quantity'].widget.attrs.update({
            'onkeyup': 'calculatePricePerUnit()'
        })
        
        # Add price suggestions if item exists
        if self.item_instance:
            self._add_price_suggestions()

    def _add_price_suggestions(self):
        """Add price suggestions based on historical data and similar items"""
        try:
            # Get recent prices for this item
            recent_prices = Price.objects.filter(
                item=self.item_instance,
                date_purchased__isnull=False
            ).order_by('-date_purchased')[:5]
            
            if recent_prices.exists():
                avg_price = sum(p.price for p in recent_prices) / len(recent_prices)
                self.fields['price'].help_text = f"Recent average: ${avg_price:.2f}. " + (self.fields['price'].help_text or "")
                
                # Add data attributes for JavaScript
                self.fields['price'].widget.attrs['data-avg-price'] = str(avg_price)
                self.fields['price'].widget.attrs['data-recent-prices'] = ','.join(str(p.price) for p in recent_prices)
            
            # Look for similar items (basic text matching)
            similar_items = Item.objects.filter(
                name__icontains=self.item_instance.name.split()[0]
            ).exclude(id=self.item_instance.id)[:3]
            
            if similar_items.exists():
                similar_prices = Price.objects.filter(
                    item__in=similar_items
                ).order_by('-date_purchased')[:10]
                
                if similar_prices.exists():
                    similar_avg = sum(p.price for p in similar_prices) / len(similar_prices)
                    self.fields['price'].widget.attrs['data-similar-avg'] = str(similar_avg)
                    
        except Exception:
            # Silently fail if there are any issues with suggestions
            pass

    def clean_price(self):
        price = self.cleaned_data.get('price')
        
        if price is None:
            raise ValidationError("Price is required.")
            
        if price <= 0:
            raise ValidationError("Price must be greater than zero.")
            
        # Check for reasonable price ranges
        if price > 10000:
            raise ValidationError("Price seems unusually high. Please verify this amount.")
            
        if price < 0.01:
            raise ValidationError("Price cannot be less than $0.01.")
            
        # Check against historical data if item exists
        if self.item_instance:
            existing_prices = Price.objects.filter(item=self.item_instance)
            if existing_prices.exists():
                avg_price = existing_prices.aggregate(avg=Avg('price'))['avg']
                min_price = existing_prices.aggregate(min=Min('price'))['min']
                max_price = existing_prices.aggregate(max=Max('price'))['max']
                
                # Flag outliers (prices more than 5x average or less than 1/5 average)
                if avg_price and (price > avg_price * 5 or price < avg_price / 5):
                    # Don't block, just add a warning
                    pass
                    
        return price
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        
        if quantity is None or quantity <= 0:
            raise ValidationError("Quantity must be a positive integer.")
            
        if quantity > 1000:
            raise ValidationError("Quantity seems unusually high. Please verify this amount.")
            
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        store = cleaned_data.get('store')
        store_name = cleaned_data.get('store_name')
        price = cleaned_data.get('price')
        quantity = cleaned_data.get('quantity')

        # Handle the case where user selected "Add New Store"
        if store == '__add_new__':
            if not store_name:
                raise forms.ValidationError("Please provide a name for the new store.")
            # Clear the store field so the save method will create a new store
            cleaned_data['store'] = ''
            
        elif not store and not store_name:
            raise forms.ValidationError("Please select an existing store or provide a new store name.")
            
        # Validate price per unit makes sense
        if price and quantity:
            price_per_unit = price / quantity
            if price_per_unit < 0.01:
                raise forms.ValidationError("Price per unit cannot be less than $0.01.")

        return cleaned_data

    def save(self, commit=True, item_instance=None):
        price_instance = super().save(commit=False)

        # Associate the item if provided
        if item_instance:
            price_instance.item = item_instance
        elif not self.instance.item_id: # Check if item is already set on the instance (e.g. editing)
             # This should ideally not happen if 'item' is excluded from fields and set in view.
             # If 'item' was in fields and hidden, self.cleaned_data.get('item') would be used.
            raise ValueError("Item instance must be provided to save the price.")


        # Handle creation of new store if store_name is provided and no store selected
        store = self.cleaned_data.get('store')
        store_name = self.cleaned_data.get('store_name')
        if store_name and not store:
            store, created = Store.objects.get_or_create(name=store_name.strip())
            price_instance.store = store

        if commit:
            price_instance.save()
        return price_instance


class BulkPriceForm(forms.Form):
    """
    Form for adding prices to multiple items at once from a single store.
    """
    store_name = forms.CharField(max_length=200, required=False,
                                 help_text="If the store isn't listed, enter its name here to create it.")
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        required=False,
        empty_label="Select a store...",
        help_text="Choose an existing store"
    )
    
    date_purchased = forms.DateField(
        required=False,
        label="Date of Price Confirmation",
        help_text="The date you confirmed these prices",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today
    )
    
    confidence = forms.ChoiceField(
        choices=[
            ('high', 'High - Verified receipt/website'),
            ('medium', 'Medium - Personal observation'),
            ('low', 'Low - Estimated/heard from others')
        ],
        initial='medium',
        required=True,
        help_text="How confident are you in these prices?"
    )
    
    price_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'placeholder': 'Enter one item per line in format: Item Name, Price, Quantity\nExample:\nCompass, 19.99, 1\nSleeping Bag, 89.99, 1\nFirst Aid Kit, 24.99, 1',
            'class': 'form-control'
        }),
        help_text="Enter items in CSV format: Item Name, Price, Quantity (one per line)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add option to create new store
        store_choices = Store.objects.all().order_by('name')
        self.fields['store'].queryset = store_choices

    def clean_price_data(self):
        price_data = self.cleaned_data.get('price_data', '')
        if not price_data.strip():
            raise ValidationError("Please enter at least one item with pricing data.")
        
        lines = [line.strip() for line in price_data.strip().split('\n') if line.strip()]
        parsed_items = []
        errors = []
        
        for i, line in enumerate(lines, 1):
            try:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) != 3:
                    errors.append(f"Line {i}: Expected format 'Item Name, Price, Quantity' but got: {line}")
                    continue
                
                item_name, price_str, quantity_str = parts
                
                if not item_name:
                    errors.append(f"Line {i}: Item name cannot be empty")
                    continue
                
                try:
                    price = Decimal(price_str)
                    if price <= 0:
                        errors.append(f"Line {i}: Price must be greater than zero")
                        continue
                    if price > 10000:
                        errors.append(f"Line {i}: Price seems unusually high ({price})")
                        continue
                except (ValueError, InvalidOperation):
                    errors.append(f"Line {i}: Invalid price format: {price_str}")
                    continue
                
                try:
                    quantity = int(quantity_str)
                    if quantity <= 0:
                        errors.append(f"Line {i}: Quantity must be greater than zero")
                        continue
                    if quantity > 1000:
                        errors.append(f"Line {i}: Quantity seems unusually high ({quantity})")
                        continue
                except ValueError:
                    errors.append(f"Line {i}: Invalid quantity format: {quantity_str}")
                    continue
                
                parsed_items.append({
                    'name': item_name,
                    'price': price,
                    'quantity': quantity
                })
                
            except Exception as e:
                errors.append(f"Line {i}: Unexpected error processing line: {str(e)}")
        
        if errors:
            raise ValidationError(errors)
        
        if not parsed_items:
            raise ValidationError("No valid items found in the data.")
        
        return parsed_items

    def clean(self):
        cleaned_data = super().clean()
        store = cleaned_data.get('store')
        store_name = cleaned_data.get('store_name')
        
        if not store and not store_name:
            raise ValidationError("Please select an existing store or provide a new store name.")
        
        return cleaned_data

    def save(self, commit=True):
        """
        Process the bulk price data and create Price objects.
        Returns a list of created Price objects and any items that were created.
        """
        if not commit:
            return [], []
        
        store = self.cleaned_data.get('store')
        store_name = self.cleaned_data.get('store_name')
        date_purchased = self.cleaned_data.get('date_purchased')
        confidence = self.cleaned_data.get('confidence')
        price_data = self.cleaned_data.get('price_data')
        
        # Handle store creation
        if store_name and not store:
            store, created = Store.objects.get_or_create(name=store_name.strip())
        
        created_prices = []
        created_items = []
        
        for item_data in price_data:
            # Get or create item
            item, item_created = Item.objects.get_or_create(
                name__iexact=item_data['name'],
                defaults={'name': item_data['name']}
            )
            if item_created:
                created_items.append(item)
            
            # Create price
            price = Price.objects.create(
                item=item,
                store=store,
                price=item_data['price'],
                quantity=item_data['quantity'],
                date_purchased=date_purchased,
                confidence=confidence
            )
            created_prices.append(price)
        
        return created_prices, created_items


class VoteForm(forms.Form):
    """
    Form for voting on a price.
    """
    price_id = forms.IntegerField(widget=forms.HiddenInput())
    is_correct_price = forms.BooleanField(required=False, widget=forms.HiddenInput()) # True for up, False for down

    def __init__(self, *args, **kwargs):
        self.vote_type = kwargs.pop('vote_type', None) # 'up' or 'down'
        super().__init__(*args, **kwargs)
        if self.vote_type == 'up':
            self.fields['is_correct_price'].initial = True
        elif self.vote_type == 'down':
            self.fields['is_correct_price'].initial = False


class PackingListItemForm(forms.ModelForm):
    class Meta:
        model = PackingListItem
        fields = ['section', 'item', 'quantity', 'nsn_lin', 'required', 'notes', 'instructions']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
            'instructions': forms.Textarea(attrs={'rows': 2}),
            'section': forms.TextInput(attrs={'placeholder': 'Section or category (optional)'}),
            'nsn_lin': forms.TextInput(attrs={'placeholder': 'NSN/LIN (optional)'}),
        }

class StoreForm(forms.ModelForm):
    """
    Form for adding or editing a store.
    """
    class Meta:
        model = Store
        fields = [
            'name', 'address_line1', 'address_line2', 'city', 'state', 'zip_code', 'country',
            'url',
            'is_online', 'is_in_person'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Store Name'}),
            'address_line1': forms.TextInput(attrs={'placeholder': 'Address Line 1'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Address Line 2 (Optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State/Province'}),
            'zip_code': forms.TextInput(attrs={'placeholder': 'ZIP/Postal Code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country', 'value': 'USA'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://store-website.com'}),
        }
        labels = {
            'name': 'Store Name',
            'address_line1': 'Address Line 1',
            'address_line2': 'Address Line 2',
            'city': 'City',
            'state': 'State/Province',
            'zip_code': 'ZIP/Postal Code',
            'country': 'Country',
            'url': 'Website URL',
            'is_online': 'Online Store',
            'is_in_person': 'Physical Location',
        }
        help_texts = {
            'is_online': 'Check if this store operates online',
            'is_in_person': 'Check if this store has a physical location',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial country to USA if not already set
        if not self.initial.get('country') and not self.data.get('country'):
            self.fields['country'].initial = 'USA'


class ItemForm(forms.ModelForm):
    """
    Form for creating or editing a standalone item.
    """
    class Meta:
        model = Item
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Item Name',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Optional description of the item...',
                'rows': 3,
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Item Name',
            'description': 'Description',
        }
        help_texts = {
            'name': 'Enter the name of the item (e.g., "Compass", "Sleeping Bag", "First Aid Kit")',
            'description': 'Optional description to help identify the item',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            # Check if item with this name already exists (case-insensitive)
            existing_item = Item.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing_item = existing_item.exclude(pk=self.instance.pk)
            if existing_item.exists():
                raise forms.ValidationError("An item with this name already exists.")
        return name
