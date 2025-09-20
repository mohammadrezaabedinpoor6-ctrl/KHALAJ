# views.py
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm
import string
import random
from .forms import PasswordResetRequestForm, PasswordResetForm
from django.contrib import messages
from .models import EmailVerification,CustomUser
from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model


User = get_user_model()




def generate_reset_code():
    """Generate a random 9-character reset code with uppercase, lowercase letters and digits"""
    reset_code = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=9))
    return reset_code

def send_verification_email(user):
    # ایجاد کد تایید و ارسال به ایمیل کاربر
    verification = EmailVerification.objects.get(user=user)
    verification_code = verification.generate_verification_code()

    subject = 'تایید ایمیل برای لاگین'
    message = f'کد تایید شما {verification_code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)



def generate_reset_code():
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=9))

def send_reset_email(email):
    try:
        user = CustomUser.objects.get(email=email)
        email_verification, created = EmailVerification.objects.get_or_create(user=user)
        reset_code = email_verification.generate_reset_code()
        # ارسال ایمیل به کاربر با کد ریست
        subject = 'Password Reset Code'
        message = f'Your password reset code is: {reset_code}'
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [email])

    except CustomUser.DoesNotExist:
        raise ValueError("این ایمیل وجود ندارد")




def request_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                send_reset_email(email)
                messages.success(request, 'کد برای ریست پسوورد برای ایمیل شما ارسال شد')
                return redirect('password_reset_code')  # هدایت به صفحه وارد کردن کد ریست پسورد
            except ValueError as e:
                messages.error(request, str(e))  # نمایش پیام خطای ایمیل اشتباه
                return render(request, 'registration/password_reset_request.html', {'form': form})

    else:
        form = PasswordResetRequestForm()

    return render(request, 'registration/password_reset_request.html', {'form': form})




# فرم وارد کردن کد تایید و تغییر رمز عبور








def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            reset_code = form.cleaned_data['reset_code']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            # بررسی کد ریست
            try:
                verification = EmailVerification.objects.get(reset_code=reset_code)
                if not verification.is_reset_code_valid():  # بررسی انقضای کد
                    messages.error(request, 'کد نامعتبر یا منقضی شده است.')
                    return redirect('password_reset_code')
            except EmailVerification.DoesNotExist:
                messages.error(request, 'کد ریست نامعتبر است.')
                return redirect('password_reset_code')

            # مقایسه پسورد جدید و تکرار آن
            if new_password != confirm_password:
                form.add_error('confirm_password', "پسووردها یکی نیستند.")  # اضافه کردن ارور به فیلد
                return render(request, 'registration/password_reset.html', {'form': form})

            # ریست پسورد
            user = verification.user
            user.set_password(new_password)
            user.save()

            messages.success(request, 'پسوورد شما با موفقیت ریست شد.')
            return redirect('login')  # هدایت به صفحه لاگین

    else:
        form = PasswordResetForm()

    return render(request, 'registration/password_reset.html', {'form': form})







def sign_up_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # ذخیره کاربر جدید

            # ایجاد و ذخیره کد تایید
            verification = EmailVerification.objects.create(user=user)
            verification_code = verification.generate_verification_code()

            # ارسال ایمیل با کد تایید
            subject = 'Verify your email for registration'
            message = f'Your verification code is {verification_code}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [form.cleaned_data.get('email')]
            send_mail(subject, message, from_email, recipient_list)

            # هدایت به صفحه وارد کردن کد تایید
            return redirect('verify_email', user_id=user.id)
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

def verify_email(request, user_id):
    # دریافت مدل کاربر سفارشی
    User = apps.get_model(settings.AUTH_USER_MODEL)
    
    # گرفتن کاربر بر اساس شناسه
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        code = request.POST.get('verification_code')  # کد تایید از فرم

        try:
            # گرفتن رکورد تایید ایمیل برای کاربر
            verification = EmailVerification.objects.get(user=user)

            # مقایسه کد وارد شده با کد ذخیره‌شده
            if verification.verification_code == code:
                verification.is_verified = True
                verification.save()
                messages.success(request, 'ایمیل شما تایید شد. ثبت نام با موفقیت انجام شد')
                return redirect('login')  # هدایت به صفحه لاگین
            else:
                messages.error(request, 'کد نامعتبر است. دوباره تلاش کنید.')
        except EmailVerification.DoesNotExist:
            messages.error(request, ' سابقه شما پیدا نشد اطلاعات شما اشتباه است')

    return render(request, 'registration/verify_email.html', {'user': user})

def verify_code(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == 'POST':
        code = request.POST.get('verification_code')

        try:
            verification = EmailVerification.objects.get(user=user)

            # بررسی کد تایید
            if verification.verification_code == code:
                verification.is_verified = True
                verification.save()
                messages.success(request, 'ایمیل شما تایید شد. الان میتوانید ورود کنید')
                return redirect('home')  # هدایت به صفحه اصلی
            else:
                messages.error(request, 'کد تایید نشد. دوباره تلاش کنید.')

        except EmailVerification.DoesNotExist:
            messages.error(request, ' سابقه شما پیدا نشد اطلاعات شما اشتباه است')

    return render(request, 'registration/verify_code.html', {'user': user})