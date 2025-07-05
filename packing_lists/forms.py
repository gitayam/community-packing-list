from django import forms
from .models import PackingList, School, Price, Store, Item

class PackingListForm(forms.ModelForm):
    """
    Form for creating a Packing List manually.
    """
    school_name = forms.CharField(max_length=200, required=False, help_text="If your school isn't listed, enter its name here to create it.")

    class Meta:
        model = PackingList
        fields = ['name', 'description', 'school']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].queryset = School.objects.all().order_by('name')
        self.fields['school'].required = False # Allow creating a list without initially assigning a school

    def save(self, commit=True):
        # Handle creation of new school if school_name is provided
        school_name = self.cleaned_data.get('school_name')
        school = self.cleaned_data.get('school')
        if school_name and not school:
            school, created = School.objects.get_or_create(name=school_name.strip())
            self.instance.school = school
        return super().save(commit=commit)


class UploadFileForm(forms.Form):
    """
    Form for uploading a file (CSV, Excel, PDF) or pasting text.
    """
    file = forms.FileField(required=False, help_text="Upload CSV, Excel, or PDF file.")
    text_content = forms.CharField(widget=forms.Textarea, required=False, help_text="Or paste text content here (one item per line).")
    # We might add a PackingList association here later, or handle it in the view
    # packing_list = forms.ModelChoiceField(queryset=PackingList.objects.all(), required=False, help_text="Add items to an existing list (optional)")

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        text_content = cleaned_data.get("text_content")

        if not file and not text_content:
            raise forms.ValidationError("Please provide either a file or text content.")
        if file and text_content:
            raise forms.ValidationError("Please provide either a file OR text content, not both.")

        if file:
            # Basic file type validation by extension (can be improved with content type checking)
            allowed_extensions = ['.csv', '.xls', '.xlsx', '.pdf']
            filename = file.name.lower()
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

            # TODO: Add file size validation if necessary
            # max_upload_size = 2621440 # 2.5MB
            # if file.size > max_upload_size:
            #     raise forms.ValidationError('Please keep filesize under 2.5MB.')


        return cleaned_data


class PriceForm(forms.ModelForm):
    """
    Form for adding or editing a price for an item.
    """
    store_name = forms.CharField(max_length=200, required=False,
                                 help_text="If the store isn't listed, enter its name here to create it.")
    # The 'item' field will be set in the view, not by the user directly in this form.
    # So we might exclude it here, or make it a HiddenInput if needed for some reason.

    class Meta:
        model = Price
        fields = ['store', 'price', 'quantity', 'date_purchased']
        # Or explicitly: fields = ['store', 'store_name', 'price', 'quantity', 'date_purchased']
        # 'item' will be associated in the view.
        widgets = {
            'date_purchased': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # item_instance = kwargs.pop('item_instance', None) # If we were to pass item for context
        super().__init__(*args, **kwargs)
        self.fields['store'].queryset = Store.objects.all().order_by('name')
        self.fields['store'].required = False # Allow creating a new store via store_name
        self.fields['date_purchased'].required = False

    def clean(self):
        cleaned_data = super().clean()
        store = cleaned_data.get('store')
        store_name = cleaned_data.get('store_name')

        if not store and not store_name:
            raise forms.ValidationError("Please select an existing store or provide a new store name.")
        if store and store_name:
            # Prefer selected store if both are provided, or raise an error
            # For now, let's assume if store is selected, store_name is ignored for creation.
            # Alternatively, could be:
            # self.add_error('store_name', "Provide a new store name only if you are not selecting an existing store.")
            pass

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


class ConfigureUploadListForm(forms.Form):
    """
    Form for configuring a newly uploaded list (name, school).
    This is similar to PackingListForm but not a ModelForm directly on PackingList
    initially, as the list itself isn't created until this form is submitted.
    However, it can reuse much of the logic for school creation.
    """
    list_name = forms.CharField(max_length=200, label="Packing List Name",
                                help_text="Enter a name for this new packing list.")
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    school = forms.ModelChoiceField(queryset=School.objects.all().order_by('name'), required=False)
    school_name = forms.CharField(max_length=200, required=False, label="Or New School Name",
                                  help_text="If your school isn't listed, enter its name here to create it.")

    def clean(self):
        cleaned_data = super().clean()
        school = cleaned_data.get('school')
        school_name = cleaned_data.get('school_name')

        if school and school_name:
            # Potentially confusing for the user; usually one or the other.
            # Depending on desired behavior, either raise error or prioritize one.
            # For now, let's say if an existing school is chosen, new school name is ignored.
            # Or, add a validation error:
            self.add_error('school_name', "Please select an existing school OR enter a new school name, not both.")

        # Ensure list_name is unique, or handle it in the view
        list_name = cleaned_data.get('list_name')
        if list_name and PackingList.objects.filter(name=list_name).exists():
            self.add_error('list_name', "A packing list with this name already exists. Please choose a different name.")

        return cleaned_data

    def get_school_instance(self):
        """
        Helper to get or create the school instance based on form data.
        Call this after form is validated.
        """
        school = self.cleaned_data.get('school')
        school_name = self.cleaned_data.get('school_name')
        if school_name and not school:
            school, _ = School.objects.get_or_create(name=school_name.strip())
        return school
