from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, name, first_name, last_name, password=None,otp =None, password2 = None):             ## otp
        """
        Creates and saves a User with the given email, name ,
        otp  and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email = self.normalize_email(email),                  ## we need to normalize the email
            name = name,                                                ##
            first_name =first_name,
            last_name = last_name,
            otp = otp,                                               ##
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name,first_name, last_name,otp=None, password=None):             ## otp
        """
        Creates and saves a superuser with the given email, name,
        tc and password.
        """
        user = self.create_user(
            email,
            password = password,
            name = name,                                                    ##
            first_name = first_name,
            last_name = last_name,
            otp = otp,
        )
        user.is_admin = True
        user.is_verified = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        primary_key=True,
        verbose_name='Email',                 ##
        max_length=255
    )
    name = models.CharField(max_length=100, verbose_name='Full Name')                ##
    first_name = models.CharField(max_length=50, verbose_name='First Name', blank=False, null=False)
    last_name = models.CharField(max_length=50, verbose_name='Last Name', blank=False, null=False)
    is_verified = models.BooleanField(default= False)
    otp = models.CharField(max_length=4, null=True, blank=True, default="")                     ##
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add= True)       ##
    updated_at = models.DateTimeField(auto_now=True)            ##
    last_login = models.DateTimeField(auto_now=True)            ##


    objects = UserManager()                                     ##

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','first_name','last_name']                         ##

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin                                        ##

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin