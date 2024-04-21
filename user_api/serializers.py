from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.validators import UnicodeUsernameValidator
from .utils import validate_username
from django.contrib.auth import get_user_model
from .models import Profile
from django.contrib.auth.hashers import check_password
from io import BytesIO
from PIL import Image
from django.core.files import File
User = get_user_model()



class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    class Meta:
        model = Profile
        fields = [  'bio', 'avatar']
        read_only_fields = ['id', 'user']  # These fields will be read-only

    
    def validate_avatar(self, value):

        if value is None:
            return value  # If avatar is None, no need for further validation
    
        max_size = 2 * 1024 * 1024  # 2MB
        max_width = 2048
        max_height = 2048
        target_width = 300
        target_height = 300

        # if not value.name.lower().endswith(('.jpeg', '.jpg', '.png')):
        #     raise serializers.ValidationError("Only JPEG, JPG, or PNG file types are allowed.")

        # Check file size
        if value.size > max_size:
            raise serializers.ValidationError("File size too large. Max size is 2MB.")

        # Check image dimensions
        img = Image.open(value)
        if img.width > max_width or img.height > max_height:
            raise serializers.ValidationError("Image dimensions too large. Max size is 2048x2048.")

        # Resize the image and fill background with white if necessary
        img.thumbnail((target_width, target_height))
        new_img = Image.new("RGB", (target_width, target_height), "white")
        new_img.paste(img, ((target_width - img.width) // 2, (target_height - img.height) // 2))

        # Save the resized image in JPG format
        output = BytesIO()
        new_img.save(output, format='PNG')  # Save in JPG format
        output.seek(0)

        # Change the file extension to .jpg
        filename = f'{value.name.rsplit(".", 1)[0]}.png'

        return File(output, name=filename)

class UserSerializer(serializers.ModelSerializer):
    pass_set = serializers.SerializerMethodField('has_usable_password')
    profile = ProfileSerializer(required=True)

    def get_role(self,obj):
        role_array = []
        if obj.is_superuser:
            role_array.append("admin")
        if obj.is_staff:
            role_array.append("staff")
        return role_array
    
    def has_usable_password(self, obj):
        if obj.password == "":
            return False
        return obj.has_usable_password()

    class Meta:
        model = User
        fields = ("id", 'username', 'email',  "profile" , "is_staff" , "is_verified", "pass_set")
        read_only_fields = ['pass_set']  # These fields will be read-only

class MeUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, validators=[validate_username])
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    new_password = serializers.CharField(write_only=True, required=False,  validators=[validate_password])
    re_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'new_password', 're_password', 'email')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Kullanıcı adı kullanımda")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu e-posta adresi kullanımda")
        return value

    def validate(self, data):
        user = self.instance  # Assuming you've set instance when initializing the serializer
        current_password = data.get('password')

        if not check_password(current_password, user.password):
            raise serializers.ValidationError( {"password": "Şifreniz hatalı"} )

        return data
    
    def update(self, instance, validated_data):
        new_password = validated_data.get('new_password')
        re_password = validated_data.get('re_password')
        if new_password:
            if new_password !=  re_password:
                raise serializers.ValidationError({"password": "Şifreler uyuşmuyor"})
            instance.set_password(new_password)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'email' in validated_data:
            instance.is_verified = False
        instance.save()
    
        return instance

    

    # def validate(self, data):
    #     if 'password' in data:
    #         if data['password'] != data['re_password']:
    #             raise serializers.ValidationError({"password": "Şifreler uyuşmuyor"})
    #     return data
# Custom serializer field with alphanumeric validation


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, validators=[validate_username])
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 're_password', 'email')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Kullanıcı adı kullanımda")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu e-posta adresi kullanımda")
        return value

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({"password": "Şifreler uyuşmuyor"})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password')
        user = User.objects.create_user(**validated_data)
        return user





class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    app_url = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'app_url', ]
        read_only_fields = ['app_url', ]  # These fields will be read-only

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Bu e-posta ile kayıtlı bir kullanıcı bulunamadı.")
        return value

    def save(self):
        email = self.validated_data['email']
        app_url = self.validated_data['app_url']
        user = User.objects.get(email=email)

        # Generate password reset token
        token = default_token_generator.make_token(user)

        # Encode user ID and token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{app_url}/reset-password-confirm/{uid}/{token}/"
        # reset_url = f"http://127.0.0.1:8000/api/user/reset-password/{uid}/{token}/"

        # Send email with reset link (you need to implement this part)
        # send_reset_email(user.email, reset_url)

        return reset_url

from django.contrib.auth import password_validation
class PasswordResetConfirmSerializer(serializers.Serializer):

    password = serializers.CharField(
        label="New password confirmation",
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value
    
class ResendVerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    app_url = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'app_url', ]
        read_only_fields = ['app_url', ]  # These fields will be read-only

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)

            if user.is_verified:
                raise serializers.ValidationError("Bu e-posta adresi doğrulanmış.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        app_url = self.validated_data['app_url']
        # Generate password reset token
        token = default_token_generator.make_token(user)

        # Encode user ID and token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verify_url = f"{app_url}/verify-email-confirm/{uid}/{token}/"
        # verify_url = f"http://127.0.0.1:8000/api/user/verify-email/{uid}/{token}/"

        # Send email with reset link (you need to implement this part)
        # send_reset_email(user.email, reset_url)

        return verify_url
    
