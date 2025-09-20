# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.conf import settings  # اضافه کردن import برای استفاده از AUTH_USER_MODEL
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(unique=True)  # ایمیل باید یکتا باشد
    first_name = models.CharField(max_length=30, blank=False)  # نام
    last_name = models.CharField(max_length=30, blank=True)  # نام خانوادگی (اختیاری)

    def __str__(self):
        return self.username



class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=9)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_code = models.CharField(max_length=9, blank=True, null=True)
    reset_code_expiration = models.DateTimeField(null=True, blank=True)  # تاریخ انقضای کد ریست پسورد

    def generate_verification_code(self):
        """Generate a random 9-character code for email verification"""
        code = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=9))
        self.verification_code = code
        self.save()
        return code

    def generate_reset_code(self):
        """Generate a random 9-character reset code and set expiration time"""
        reset_code = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=9))
        self.reset_code = reset_code
        self.reset_code_expiration = timezone.now() + timedelta(hours=1)  # کد ریست به مدت 1 ساعت اعتبار دارد
        self.save()
        return reset_code

    def is_reset_code_valid(self):
        """Check if the reset code is still valid"""
        if self.reset_code_expiration and self.reset_code_expiration > timezone.now():
            return True
        return False