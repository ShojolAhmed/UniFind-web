from io import BytesIO
import tempfile

from django.contrib.auth.models import User
from django.test import override_settings

from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Item, Claim, Notification


def make_image(name='test.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), (200, 120, 40)).save(buffer, 'PNG')
    buffer.seek(0)
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(name, buffer.read(), content_type='image/png')


def create_item(owner, **overrides):
    data = dict(
        owner=owner,
        title='Sample Item',
        item_type='Lost',
        description='A sample description',
        location='Library',
        image='items/sample.jpg',
        contact='0123456789',
    )
    data.update(overrides)
    return Item.objects.create(**data)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class AuthTests(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'student',
                'email': 'student@example.com',
                'password': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'student')

        user = User.objects.get(username='student')
        self.assertEqual(user.email, 'student@example.com')
        self.assertTrue(user.check_password('StrongPass123!'))

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'student',
                'email': 'student@example.com',
                'password': 'StrongPass123!',
                'password2': 'Different123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)
        self.assertFalse(User.objects.filter(username='student').exists())

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'student',
                'email': 'student@example.com',
                'password': '123',
                'password2': '123',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='dupe@example.com',
            password='StrongPass123!',
        )
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'newuser',
                'email': 'dupe@example.com',
                'password': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_token_login_returns_tokens_and_user(self):
        User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass123!',
        )
        response = self.client.post(
            '/api/auth/token/',
            {'username': 'student', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'student')

    def test_me_requires_authentication(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'student')
        self.assertEqual(response.data['email'], 'student@example.com')


# ---------------------------------------------------------------------------
# Items: listing, filtering, CRUD and permissions
# ---------------------------------------------------------------------------

class ItemListTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pw')
        self.other = User.objects.create_user(username='other', password='pw')
        self.backpack = create_item(
            self.owner, title='Black Backpack', item_type='Lost', location='Cafeteria'
        )
        self.calculator = create_item(
            self.other, title='Scientific Calculator', item_type='Found', location='Lab'
        )

    def test_list_is_public(self):
        response = self.client.get('/api/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_title(self):
        response = self.client.get('/api/items/?title=backpack')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Black Backpack')

    def test_filter_by_location(self):
        response = self.client.get('/api/items/?location=lab')
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_item_type(self):
        response = self.client.get('/api/items/?item_type=Found')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['item_type'], 'Found')

    def test_filter_owner_me(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/items/?owner=me')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Black Backpack')

    def test_is_owner_flag(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/items/{self.backpack.id}/')
        self.assertTrue(response.data['is_owner'])
        response = self.client.get(f'/api/items/{self.calculator.id}/')
        self.assertFalse(response.data['is_owner'])


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ItemCrudTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pw')
        self.other = User.objects.create_user(username='other', password='pw')

    def test_create_requires_authentication(self):
        response = self.client.post('/api/items/', {'title': 'X'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_sets_owner_from_request(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            '/api/items/',
            {
                'title': 'Lost Keys',
                'item_type': 'Lost',
                'description': 'A bunch of keys',
                'location': 'Gate 2',
                'contact': '0123456789',
                'image': make_image(),
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        item = Item.objects.get(title='Lost Keys')
        self.assertEqual(item.owner, self.owner)
        self.assertFalse(item.claimed)

    def test_owner_can_update_own_item(self):
        item = create_item(self.owner)
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f'/api/items/{item.id}/', {'title': 'Updated'}, format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.title, 'Updated')

    def test_non_owner_cannot_update_item(self):
        item = create_item(self.owner)
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f'/api/items/{item.id}/', {'title': 'Hacked'}, format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        item.refresh_from_db()
        self.assertEqual(item.title, 'Sample Item')

    def test_non_owner_cannot_delete_item(self):
        item = create_item(self.owner)
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(f'/api/items/{item.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Item.objects.filter(id=item.id).exists())

    def test_owner_can_delete_item(self):
        item = create_item(self.owner)
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/items/{item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Item.objects.filter(id=item.id).exists())


# ---------------------------------------------------------------------------
# Claim workflow
# ---------------------------------------------------------------------------

class ClaimWorkflowTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pw')
        self.claimer = User.objects.create_user(username='claimer', password='pw')
        self.claimer2 = User.objects.create_user(username='claimer2', password='pw')
        self.item = create_item(self.owner, title='Blue Umbrella', item_type='Found')

    def test_claim_creates_claim_and_notifies_owner(self):
        self.client.force_authenticate(user=self.claimer)
        response = self.client.post(f'/api/items/{self.item.id}/claim/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        claim = Claim.objects.get(item=self.item, claimant=self.claimer)
        self.assertEqual(claim.status, 'pending')
        self.assertTrue(
            Notification.objects.filter(recipient=self.owner, claim=claim).exists()
        )
        self.item.refresh_from_db()
        self.assertFalse(self.item.claimed)

    def test_owner_cannot_claim_own_item(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/items/{self.item.id}/claim/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Claim.objects.count(), 0)

    def test_cannot_claim_twice(self):
        self.client.force_authenticate(user=self.claimer)
        self.client.post(f'/api/items/{self.item.id}/claim/')
        response = self.client.post(f'/api/items/{self.item.id}/claim/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Claim.objects.filter(item=self.item).count(), 1)

    def test_cannot_claim_already_claimed_item(self):
        self.item.claimed = True
        self.item.save(update_fields=['claimed'])
        self.client.force_authenticate(user=self.claimer)
        response = self.client.post(f'/api/items/{self.item.id}/claim/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_claim_requires_authentication(self):
        response = self.client.post(f'/api/items/{self.item.id}/claim/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_approves_claim_and_rejects_competing_claims(self):
        claim1 = Claim.objects.create(item=self.item, claimant=self.claimer)
        claim2 = Claim.objects.create(item=self.item, claimant=self.claimer2)

        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/claims/{claim1.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        claim1.refresh_from_db()
        claim2.refresh_from_db()
        self.item.refresh_from_db()

        self.assertEqual(claim1.status, 'approved')
        self.assertEqual(claim2.status, 'rejected')
        self.assertTrue(self.item.claimed)
        self.assertEqual(self.item.claimed_by, self.claimer)

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.claimer, message__icontains='approved'
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.claimer2, message__icontains='rejected'
            ).exists()
        )

    def test_non_owner_cannot_approve_claim(self):
        claim = Claim.objects.create(item=self.item, claimant=self.claimer)
        self.client.force_authenticate(user=self.claimer2)
        response = self.client.post(f'/api/claims/{claim.id}/approve/')
        # claimer2 is neither claimant nor owner -> not in queryset -> 404
        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )
        claim.refresh_from_db()
        self.assertEqual(claim.status, 'pending')

    def test_owner_rejects_claim_and_notifies_claimant(self):
        claim = Claim.objects.create(item=self.item, claimant=self.claimer)
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/claims/{claim.id}/reject/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        claim.refresh_from_db()
        self.assertEqual(claim.status, 'rejected')
        self.item.refresh_from_db()
        self.assertFalse(self.item.claimed)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.claimer, message__icontains='rejected'
            ).exists()
        )

    def test_list_my_claims(self):
        Claim.objects.create(item=self.item, claimant=self.claimer)
        other_item = create_item(self.claimer2, title='Other')
        Claim.objects.create(item=other_item, claimant=self.claimer2)

        self.client.force_authenticate(user=self.claimer)
        response = self.client.get('/api/claims/')
        self.assertEqual(response.data['count'], 1)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pw')
        self.other = User.objects.create_user(username='other', password='pw')
        self.item = create_item(self.owner)
        claim = Claim.objects.create(item=self.item, claimant=self.other)
        self.notification = Notification.objects.create(
            recipient=self.owner, claim=claim, message='Someone wants your item.'
        )
        Notification.objects.create(
            recipient=self.other, message='Not for owner.'
        )

    def test_notifications_scoped_to_recipient(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['message'], 'Someone wants your item.'
        )

    def test_mark_notification_read(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f'/api/notifications/{self.notification.id}/read/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_unread_count(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.data['unread'], 1)

    def test_cannot_mark_others_notification(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            f'/api/notifications/{self.notification.id}/read/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
