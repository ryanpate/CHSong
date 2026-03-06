from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta

from .forms import RegisterForm, LoginForm
from .models import EmailVerificationToken

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('songs:dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()
            token = EmailVerificationToken.objects.create(user=user)
            verify_url = request.build_absolute_uri(f'/accounts/verify/{token.token}/')
            send_mail(
                subject='Verify your Cherry Hills Song account',
                message=f'Click here to verify your email:\n\n{verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return redirect('accounts:verify_sent')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('songs:dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Check if user exists but is inactive (unverified)
            try:
                user_obj = User.objects.get(email=email)
                if not user_obj.is_active:
                    messages.error(request, 'Please verify your email before logging in.')
                    return render(request, 'accounts/login.html', {'form': form})
            except User.DoesNotExist:
                pass
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('songs:dashboard')


def verify_email_view(request, token):
    try:
        verification = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('accounts:login')

    if timezone.now() - verification.created_at > timedelta(hours=24):
        messages.error(request, 'Verification link has expired. Please register again.')
        verification.user.delete()
        return redirect('accounts:register')

    user = verification.user
    user.is_active = True
    user.email_verified = True
    user.save()
    verification.delete()
    messages.success(request, 'Email verified! You can now log in.')
    return redirect('accounts:login')


def verify_sent_view(request):
    return render(request, 'accounts/verify_sent.html')
