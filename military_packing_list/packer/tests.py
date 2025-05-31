from django.test import TestCase, Client
from django.urls import reverse
from .models import Item, Price, UserProfile
from .forms import PriceForm
# from django.contrib.auth.models import User # Not strictly needed for current tests

# Helper function to create items/prices if needed repeatedly
def create_item(name="Test Item", description="Test Description"):
    return Item.objects.create(name=name, description=description)

def create_user_profile(name="testuser", reputation_score=0):
    return UserProfile.objects.create(name=name, reputation_score=reputation_score)

def create_price(item, price_value=10.99, store_name="Test Store", submitted_by_name="testuser"):
    # Ensure user profile exists if not anonymous
    if submitted_by_name != "Anonymous":
        UserProfile.objects.get_or_create(name=submitted_by_name)
    return Price.objects.create(
        item=item,
        price=price_value,
        store_name=store_name,
        submitted_by_name=submitted_by_name
    )

class ModelTests(TestCase):
    def test_create_item(self):
        item = create_item()
        retrieved_item = Item.objects.get(id=item.id)
        self.assertEqual(retrieved_item.name, "Test Item")
        self.assertEqual(retrieved_item.description, "Test Description")

    def test_create_user_profile(self):
        user_profile = create_user_profile(name="profile_tester", reputation_score=5)
        retrieved_profile = UserProfile.objects.get(id=user_profile.id)
        self.assertEqual(retrieved_profile.name, "profile_tester")
        self.assertEqual(retrieved_profile.reputation_score, 5)

    def test_create_price(self):
        item = create_item(name="Pricing Item")
        # UserProfile will be created by create_price helper if submitted_by_name is not Anonymous
        price_instance = create_price(item=item, price_value=100.50, store_name="Main Store", submitted_by_name="price_submitter")
        retrieved_price = Price.objects.get(id=price_instance.id)
        self.assertEqual(retrieved_price.item, item)
        self.assertEqual(retrieved_price.price, 100.50)
        self.assertEqual(retrieved_price.store_name, "Main Store")
        self.assertEqual(retrieved_price.submitted_by_name, "price_submitter")
        # Check if UserProfile for price_submitter was created
        self.assertTrue(UserProfile.objects.filter(name="price_submitter").exists())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.item1 = create_item(name="Item Alpha")
        self.item2 = create_item(name="Item Beta", description="Description for Beta")
        self.price1_item1 = create_price(item=self.item1, price_value=20.00, submitted_by_name="UserA")
        self.price2_item1 = create_price(item=self.item1, price_value=19.50, submitted_by_name="UserB")

    def test_item_list_view(self):
        response = self.client.get(reverse('packer:item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packer/item_list.html')
        self.assertContains(response, self.item1.name)
        self.assertContains(response, self.item2.name)

    def test_item_detail_view(self):
        response = self.client.get(reverse('packer:item_detail', args=[self.item1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packer/item_detail.html')
        self.assertContains(response, self.item1.name)
        self.assertContains(response, str(self.price1_item1.price)) # Check for price
        self.assertContains(response, self.price1_item1.store_name) # Check for store

    def test_add_price_view_get(self):
        response = self.client.get(reverse('packer:add_price', args=[self.item1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packer/add_price_form.html')
        self.assertIsInstance(response.context['form'], PriceForm)

    def test_add_price_view_post_valid(self):
        item_for_new_price = create_item(name="New Price Item")
        data = {
            'price': '25.99',
            'store_name': 'Online Shop',
            'submitted_by_name': 'NewSubmitter'
        }
        response = self.client.post(reverse('packer:add_price', args=[item_for_new_price.id]), data)
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertRedirects(response, reverse('packer:item_detail', args=[item_for_new_price.id]))

        self.assertTrue(Price.objects.filter(item=item_for_new_price, price=25.99).exists())
        self.assertTrue(UserProfile.objects.filter(name='NewSubmitter').exists())

    def test_add_price_view_post_invalid(self):
        data = {
            'price': '', # Invalid - price is required
            'store_name': 'Offline Store',
            'submitted_by_name': 'InvalidSubmitter'
        }
        response = self.client.post(reverse('packer:add_price', args=[self.item1.id]), data)
        self.assertEqual(response.status_code, 200) # Re-renders form
        self.assertIn('form', response.context)
        form_in_context = response.context['form']
        self.assertFormError(form_in_context, 'price', 'This field is required.')


class FormTests(TestCase):
    def test_price_form_valid(self):
        data = {'price': '123.45', 'store_name': 'Valid Store', 'submitted_by_name': 'FormTester'}
        form = PriceForm(data=data)
        self.assertTrue(form.is_valid())

    def test_price_form_invalid_missing_price(self):
        data = {'store_name': 'Invalid Store', 'submitted_by_name': 'FormTester'} # Missing price
        form = PriceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_price_form_invalid_price_format(self):
        data = {'price': 'not-a-price', 'store_name': 'Invalid Store', 'submitted_by_name': 'FormTester'}
        form = PriceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertEqual(form.errors['price'], ['Enter a number.'])


class VoteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = create_item(name="Votable Item")
        self.submitter_profile = create_user_profile(name="testvoter", reputation_score=10)
        self.price = create_price(item=self.item, submitted_by_name=self.submitter_profile.name, price_value=50.00)

        self.anonymous_price = create_price(item=self.item, submitted_by_name="Anonymous", price_value=60.00)

    def test_upvote_price(self):
        initial_upvotes = self.price.upvotes
        initial_reputation = self.submitter_profile.reputation_score

        response = self.client.post(reverse('packer:vote_price', args=[self.price.id, 'upvote']))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')

        self.price.refresh_from_db()
        self.submitter_profile.refresh_from_db()

        self.assertEqual(self.price.upvotes, initial_upvotes + 1)
        self.assertEqual(self.submitter_profile.reputation_score, initial_reputation + 1)
        self.assertEqual(json_response['upvotes'], self.price.upvotes)
        self.assertEqual(json_response['reputation_score'], self.submitter_profile.reputation_score)

    def test_downvote_price(self):
        initial_downvotes = self.price.downvotes
        initial_reputation = self.submitter_profile.reputation_score

        response = self.client.post(reverse('packer:vote_price', args=[self.price.id, 'downvote']))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')

        self.price.refresh_from_db()
        self.submitter_profile.refresh_from_db()

        self.assertEqual(self.price.downvotes, initial_downvotes + 1)
        self.assertEqual(self.submitter_profile.reputation_score, initial_reputation - 1)
        self.assertEqual(json_response['downvotes'], self.price.downvotes)

    def test_vote_anonymous_price_upvote(self):
        initial_upvotes = self.anonymous_price.upvotes

        response = self.client.post(reverse('packer:vote_price', args=[self.anonymous_price.id, 'upvote']))
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')

        self.anonymous_price.refresh_from_db()
        self.assertEqual(self.anonymous_price.upvotes, initial_upvotes + 1)
        self.assertIsNone(json_response['reputation_score']) # No reputation for Anonymous

    def test_vote_invalid_type(self):
        response = self.client.post(reverse('packer:vote_price', args=[self.price.id, 'invalidvote']))
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'error')
        self.assertEqual(json_response['message'], 'Invalid vote type')

    def test_vote_requires_post(self):
        response = self.client.get(reverse('packer:vote_price', args=[self.price.id, 'upvote']))
        self.assertEqual(response.status_code, 403) # HttpResponseForbidden

    def test_vote_on_nonexistent_price(self):
        non_existent_price_id = Price.objects.count() + 999
        response = self.client.post(reverse('packer:vote_price', args=[non_existent_price_id, 'upvote']))
        self.assertEqual(response.status_code, 404) # get_object_or_404 should trigger this
