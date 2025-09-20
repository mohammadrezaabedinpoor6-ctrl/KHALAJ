from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
import re



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'age')

    email = forms.EmailField(label='ایمیل')
    first_name = forms.CharField(label='نام', max_length=30)
    last_name = forms.CharField(label='نام خانوادگی', max_length=30, required=False)
    age = forms.IntegerField(label='سن')

    username = forms.CharField(label='نام کاربری', help_text=None)

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if len(password) < 8:
            raise ValidationError("پسورد باید حداقل ۸ کاراکتر باشد.")
        
        if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
            raise ValidationError("پسورد باید شامل حروف و اعداد باشد.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        # بررسی که آیا فیلد ایمیل خالی نباشد
        if not email:
            raise ValidationError("لطفاً ایمیل خود را وارد کنید.")

        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("نام کاربری قبلاً انتخاب شده است.")

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("ایمیل قبلاً انتخاب شده است.")

        # بررسی مشابه بودن نام کاربری و ایمیل
        if username and email and username.lower() == email.split('@')[0].lower():
            raise ValidationError("نام کاربری و ایمیل مشابه هستند. لطفاً از نام کاربری متفاوت استفاده کنید.")

        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="نام کاربری یا ایمیل")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            return CustomUser.objects.get(email=username)
        return CustomUser.objects.get(username=username)
# forms.py


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'age')  # اضافه کردن فیلدهای جدید

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="ایمیل")
# forms.py
class PasswordResetForm(forms.Form):
    reset_code = forms.CharField(label="کد ریست", max_length=6)
    new_password = forms.CharField(widget=forms.PasswordInput, label="گذرواژه جدید")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="تکرار گذرواژه جدید")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # بررسی اینکه پسوردها مشابه باشند
        if new_password != confirm_password:
            raise forms.ValidationError("پسوورد ها یکی نیستند.")

        return cleaned_data