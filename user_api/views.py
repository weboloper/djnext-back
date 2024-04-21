from rest_framework.views import APIView
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    ResendVerifyEmailSerializer,
    ProfileSerializer, MeUpdateSerializer
)
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .models import Profile
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework import status
import requests
from django.shortcuts import redirect
from django.http import Http404
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.utils.crypto import get_random_string
from io import BytesIO
from PIL import Image
from django.conf import settings

User = get_user_model()


# class UserUpdateAPIView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = UserUpdateSerializer

#     def get_object(self):
#         return self.request.user
    
#     def put(self, request, *args, **kwargs):
#         user = self.get_object()
#         serializer = UserUpdateSerializer(user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             data = serializer.data
#             data['message'] = "Değişiklikler başarıyla kaydedildi."
#             return Response(data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MeView(APIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
    
    def get(self, request,  format=None):
        user = self.get_object()
        serializer = UserSerializer(user,context={"request": request})
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = MeUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data['message'] = "Değişiklikler başarıyla kaydedildi."
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyProfileUpdate(APIView):

    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        return self.request.user.profile

    #used post instead of put
    def post(self, request,  format=None):
        profile = self.get_object()
        self.check_object_permissions(request, profile)
        serializer = ProfileSerializer(profile, data=request.data, partial=True ,context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserAPIView(APIView):
    permission_classes = [ permissions.AllowAny]

    def get_object(self, slug):
        try:
            return User.objects.get(username=slug)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        user = self.get_object(slug)
        serializer = UserSerializer(user,context={"request": request})
        return Response(serializer.data)

 # def put(self, request,  format=None):
    #     user = self.get_object()
    #     self.check_object_permissions(request, user)
    #     serializer = UserSerializer(user, data=request.data, partial=True)
    #     serializer2 = ProfileSerializer(user.profile, data=request.data, partial=True)
    #     if serializer.is_valid() and serializer2.is_valid():
    #         serializer.save()
    #         serializer2.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class RegisterAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response( serializer.data , status=status.HTTP_201_CREATED)
        return Response( serializer.errors  , status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetRequestAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            reset_url = serializer.save()
            return Response({"message": reset_url }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        password = request.data.get('password')
        

        if uidb64 is None or token is None or password is None:
            # return Response({'detail': 'uidb64, token, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'uidb64, token, ve şifre gerekli'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):

            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(password)
                user.save()
                return Response({'message': 'Şifreniz başarıyla değiştirildi.'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
            
        else:
            return Response({'detail': 'Şifre hatırlatma bağlantısı geçersiz. Lütfen tekrar deneyiniz.'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailRequestAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        serializer = ResendVerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            verify_url = serializer.save()
            return Response({"message": verify_url }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmailConfirmAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        

        if uidb64 is None or token is None :
            return Response({'detail': 'Doğrulama bağlantısı geçersiz. Lütfen tekrar deneyiniz.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):

            if user.is_verified:
                return Response({'detail': 'Bu e-posta zaten doğrulanmış.'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.save()
            return Response({'message': 'E-posta doğrulama başarıyla tamamlandı.'}, status=status.HTTP_200_OK)

        else:
            return Response({'detail': 'Doğrulama bağlantısı geçersiz. Lütfen tekrar deneyiniz.'}, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuth(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        # Redirect user to Google OAuth consent screen
        google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
        # redirect_uri = request.build_absolute_uri(reverse('google_auth_callback'))
        redirect_uri="http://localhost:3000/api/google/auth"
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'email profile',
        }
        redirect_url = google_oauth_url + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])
        return redirect(redirect_url)


class GoogleAuthCallback(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        

        json_data = json.loads(request.body)
        code = json_data["code"]
          
        # Exchange authorization code for access token
        # code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': '1Authorization code not found'}, status=status.HTTP_400_BAD_REQUEST)

        token_url = "https://oauth2.googleapis.com/token"
        # redirect_uri = request.build_absolute_uri(reverse('google_auth_callback'))
        redirect_uri="http://localhost:3000/api/google/auth"
        data = {
            'code': code,
            'client_id' : settings.GOOGLE_CLIENT_ID,
            'client_secret' : settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:

            access_token = response.json().get('access_token')
            
            # Get user info from Google API
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            user_info_response = requests.get(user_info_url, headers=headers)
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                username = self.unique_username(user_info)
                
                # Get or create user based on Google user info
                user, created = User.objects.get_or_create(email=user_info['email'])
                if created:
                    # If user is created, set additional attributes
                    user.username=username
                    # user.first_name = user_info.get('given_name', '')
                    # user.last_name = user_info.get('family_name', '')
                    user.is_verified = True
                    user.save()
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                # Fetch user's profile image from Google
                profile_image_url = user_info.get('picture')
                if profile_image_url:
                    response = requests.get(profile_image_url)
                    if response.status_code == 200:
                        # Open image using PIL
                        image = Image.open(BytesIO(response.content))
                        # Resize the image if needed
                        image.thumbnail((300, 300))
                        # Save the image to user's profile model
                        user_profile, created = Profile.objects.get_or_create(user=user)
                        
                        # Convert image to bytes
                        img_byte_array = BytesIO()
                        image.save(img_byte_array, format='JPEG')
                        img_byte_array.seek(0)
                        
                        user_profile.avatar.save(f'{user.username}_avatar.jpg', img_byte_array, save=True)
                
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                
                # Prepare response JSON
                response_data = {
                    "access": access,
                    "refresh": str(refresh)
                }
                
                # Return tokens in JSON response
                return JsonResponse(response_data)
            
        else:
            return JsonResponse({'error':  code}, status=response.status_code)
        
    def random_trailing(self):
        return get_random_string(length=5)
    
    def unique_username(self, user_info):
         
        username = user_info.get('given_name', '')+ user_info.get('family_name', '')
        counter = 1
        while User.objects.filter(username=username):
            username = username + str(counter)
            counter += 1
            
        return username  

class ProfileDetailAPIViewasaf(APIView):

    permission_classes = [ permissions.AllowAny]

    def get_object(self, pk):
        try:
            return Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        profile = self.get_object(pk)
        self.check_object_permissions(request, profile)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        profile = self.get_object(pk)
        self.check_object_permissions(request, profile)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)