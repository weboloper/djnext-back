from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_verified)

    def test_create_superuser(self):
        admin_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpassword',
        }
        admin = User.objects.create_superuser(**admin_data)
        self.assertEqual(admin.username, admin_data['username'])
        self.assertEqual(admin.email, admin_data['email'])
        self.assertTrue(admin.check_password(admin_data['password']))
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_verified)


class ProfileModelTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_profile_creation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(str(profile), f'Profile of {self.user.email}')
        self.assertIsNone(profile.bio)
        self.assertEqual(profile.avatar.name, 'default_avatar.png')  # Check against the default value

    def test_profile_str(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), f'Profile of {self.user.email}')


from rest_framework.test import APITestCase
from .serializers import ProfileSerializer, UserSerializer, RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, ResendVerifyEmailSerializer
# Add more test cases as needed.
# class ProfileSerializerTest(APITestCase):
#     def test_profile_serializer(self):
#         # Create a user
#         user = User.objects.create(username='testuser', email='test@example.com')
        
#         # Define profile data with the user's ID
#         profile_data = {'user': user.id, 'bio': 'Test bio', 'avatar': None}
        
#         # Create a serializer instance with the profile data
#         serializer = ProfileSerializer(data=profile_data)
        
#         # Ensure the serializer is valid
#         self.assertTrue(serializer.is_valid())

#         # Save the profile
#         profile = serializer.save()
        
#         # Assert the profile is associated with the correct user
#         self.assertEqual(profile.user, user)


class UserSerializerTest(APITestCase):
    def test_user_serializer(self):
        user_data = {'username': 'testuser', 'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User', 'is_staff': False, 'is_verified': False}
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_verified)


class RegisterSerializerTest(APITestCase):
    def test_register_serializer(self):
        register_data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'testpassword', 're_password': 'testpassword'}
        serializer = RegisterSerializer(data=register_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')


class PasswordResetSerializerTest(APITestCase):
    def test_password_reset_serializer(self):
        # Define valid serializer data (ensure it's valid based on your serializer's requirements)
        serializer_data = {'email': 'test@example.com', 'app_url': 'http://example.com'}
        
        # Create a serializer instance with the data
        serializer = PasswordResetSerializer(data=serializer_data)
        
        # Check if the serializer data is valid
        if not serializer.is_valid():
            print("Errors:", serializer.errors)  # Print out the validation errors
        
        # Ensure the serializer data is valid
        self.assertTrue(serializer.is_valid())


class PasswordResetConfirmSerializerTest(APITestCase):
    def test_password_reset_confirm_serializer(self):
        # Define valid serializer data (ensure it's valid based on your serializer's requirements)
        serializer_data = {'password': 'new_password'}
        
        # Create a serializer instance with the data
        serializer = PasswordResetConfirmSerializer(data=serializer_data)
        
        # Check if the serializer data is valid
        if not serializer.is_valid():
            print("Errors:", serializer.errors)  # Print out the validation errors
        
        # Ensure the serializer data is valid
        self.assertTrue(serializer.is_valid())


class ResendVerifyEmailSerializerTest(APITestCase):
    def test_resend_verify_email_serializer(self):
        # Define valid serializer data (ensure it's valid based on your serializer's requirements)
        serializer_data = {'email': 'test@example.com', 'app_url': 'http://example.com'}
        
        # Create a serializer instance with the data
        serializer = ResendVerifyEmailSerializer(data=serializer_data)
        
        # Check if the serializer data is valid
        if not serializer.is_valid():
            print("Errors:", serializer.errors)  # Print out the validation errors
        
        # Ensure the serializer data is valid
        self.assertTrue(serializer.is_valid())