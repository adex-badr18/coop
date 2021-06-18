from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.forms.widgets import NumberInput
from django.utils import timezone

GENDER = (
    ('--------------', '--------------'),
    ('male', 'MALE'),
    ('female', 'FEMALE')
)

RELIGION = (
    ('--------------', '--------------'),
    ('islam', 'ISLAM'),
    ('christianity', 'CHRISTIANITY'),
    ('others', 'OTHERS')
)

MARITAL_STATUS = (
    ('--------------', '--------------'),
    ('single', 'SINGLE'),
    ('married', 'MARRIED')
)


def upload_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'


class State(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Lga(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        # Creates and saves a User with the given email and password.
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        # Creates and saves a superuser with the given email and password.
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False)  # is email confirmed?
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)  # is superuser?
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True)
    reg_approved = models.BooleanField(default=False)
    membership_id = models.CharField(max_length=200, blank=True, null=True, unique=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'

    def get_username(self):
        return self.email

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Does the user have permissions to view the app `app_label`?
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff_member(self):
        # Is the user a member of staff?
        return self.is_staff

    @property
    def is_superuser(self):
        # Is the user a admin member?
        return self.is_admin


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', unique=True)
    gender = models.CharField(max_length=100, choices=GENDER, default='Select gender')
    marital_status = models.CharField(max_length=100, choices=MARITAL_STATUS, default='Select marital status')
    religion = models.CharField(max_length=100, choices=RELIGION, default='Select religion', blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.SET_NULL, related_name='state')
    lg = models.ForeignKey(Lga, null=True, blank=True, on_delete=models.SET_NULL, related_name='lg')
    hometown = models.ForeignKey(Lga, null=True, blank=True, on_delete=models.SET_NULL, related_name='hometown')
    #  Next of Kin
    nok_name = models.CharField(max_length=150, blank=True)
    nok_address = models.CharField(max_length=200, blank=True)
    nok_relationship = models.CharField(max_length=100, blank=True)
    nok_occupation = models.CharField(max_length=100, blank=True)
    nok_age = models.IntegerField(help_text="not less than 18", null=True, blank=True, default=0)
    nok_phone = models.CharField(max_length=100, unique=False, blank=True)
    #  Job Info
    job_name = models.CharField(max_length=200, blank=True)
    job_address = models.CharField(max_length=200, blank=True)
    job_responsibility = models.CharField(max_length=200, blank=True)
    job_post = models.CharField(max_length=100, blank=True)
    #  Referees
    ref_name1 = models.CharField(max_length=200, blank=True)
    ref_name2 = models.CharField(max_length=200, blank=True)
    ref_phone1 = models.CharField(max_length=100, unique=False, blank=True)
    ref_phone2 = models.CharField(max_length=100, unique=False, blank=True)
    ref_id1 = models.CharField(max_length=100, blank=True)
    ref_id2 = models.CharField(max_length=100, blank=True)
    #  File uploads
    form_receipt = models.ImageField(upload_to=upload_directory_path, blank=True, max_length=255)
    applicant_photo = models.ImageField(upload_to=upload_directory_path, blank=True, max_length=255)
    applicant_id = models.ImageField(upload_to=upload_directory_path, blank=True, max_length=255)
    nok_photo = models.ImageField(upload_to=upload_directory_path, blank=True, max_length=255)
    nok_id = models.ImageField(upload_to=upload_directory_path, blank=True, max_length=255)
    reg_receipt = models.ImageField(upload_to='reg_receipt', max_length=255)

    def __str__(self):
        return self.user.get_full_name()


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
