from django.db import models
from django.contrib.auth.models import ( AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from .utils import validate_username
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    
    def _create_user(self, username, email, password, **extra_fields):

        if not username:
            raise ValueError("The given username must be set")

        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)

        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=True, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_verified", False) # False if email verification
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=True, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)

     
class User(AbstractBaseUser, PermissionsMixin):
    
    # username_validator = UnicodeUsernameValidator()
    first_name=models.CharField("Ad", blank=True, max_length=60)
    last_name=models.CharField("Soyad", blank=True, max_length=60)
    username = models.CharField(
        _("Kullanıcı Adı"),
        max_length=20,
        unique=True,
        help_text=_(
            "Zorunlu. En fazla 20 karakter."
        ),
        validators=[validate_username],

        db_index=True
    )
    email=models.EmailField(_("E-Posta"), max_length=255, unique=True, blank=False, db_index=True)

    is_verified=models.BooleanField(_("Verified"), default=False,  help_text="E-mail verification")
    is_active=models.BooleanField(_("Active"), default=True)
    is_staff=models.BooleanField(default=False)

    date_joined = models.DateTimeField(_('Date Joined'), auto_now_add=True)    

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=('username',)

    objects= UserManager()

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        return super(User, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Add profile photo field
    # first_name=models.CharField("Ad", blank=True, max_length=60)
    # last_name=models.CharField("Soyad", blank=True, max_length=60)

    def __str__(self):
        return f'Profile of {self.user.email}'
    

from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a profile for the user upon registration.
    """
    if created:
        Profile.objects.create(user=instance)