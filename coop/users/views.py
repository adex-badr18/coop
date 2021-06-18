from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from .forms import SignUpForm, ProfileForm, UserUpdateForm, LoginForm, UpdatePasswordForm, ProfileUpdateForm
from django.views.generic.edit import CreateView, UpdateView
from .models import CustomUser, Lga, Profile
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import datetime

from .models import CustomUser as User
# User = settings.AUTH_USER_MODEL


# Create your views here.
def index(request):
    return render(request, 'index.html')


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        user = SignUpForm(request.POST)
        profile = ProfileForm(request.POST, request.FILES)
        if user.is_valid() and profile.is_valid():
            user = user.save(commit=False)
            user.is_active = False
            user.save()
            user.refresh_from_db()
            # Profile
            profile = ProfileForm(request.POST, request.FILES, instance=user.profile)
            profile.full_clean()
            profile.save()

            current_site = get_current_site(request)
            subject = 'Activate your GRT-Pristine account'
            message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = user.cleaned_data.get('email')
            email = EmailMessage(subject, message, to=[to_email])
            email.send()
            messages.info(request, "Account activation sent. Please confirm your email address to complete your "
                                   "registration.")
            return redirect('users:index')
        else:
            messages.error(request, "Registration unsuccessful! Invalid information supplied.")
            return redirect('users:signup')
    else:
        user = SignUpForm()
        profile = ProfileForm()
    return render(request, 'users/signup.html', {'user': user,
                                                 'profile': profile})


@login_required
def user_profile_update(request):
    # profile = get_object_or_404(Profile, pk=pk)
    # user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your Profile has been updated!')
            return redirect('users:index')
        else:
            messages.error(request, 'Error updating profile')
            return redirect('users:update_profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'users/update_profile.html', {'p_form': p_form, 'u_form': u_form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {email}.")
                return redirect("users:index")
            else:
                messages.error(request, 'Invalid e-mail or password.')
                return redirect('users:login')
        else:
            messages.error(request, 'Invalid e-mail or password.')
            return redirect('users:login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have successfully logged out!')
    return redirect('users:index')


def load_lg(request):
    state_id = request.GET.get('state')
    lgs = Lga.objects.filter(state_id=state_id).order_by('name')
    return render(request, 'users/lg_options.html', {'lgs': lgs})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        # login(request, user)
        return redirect('users:index')
    else:
        messages.warning(request, 'The confirmation link was invalid, possibly because it has already been used.')
        return redirect('users:index')


@login_required
def update_password(request):
    if request.method == 'POST':
        form = UpdatePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:index')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = UpdatePasswordForm(request.user)
    return render(request, 'registration/update_password.html', {'form': form})


# @transaction.atomic
# def signup(request):
#     if request.method == 'POST':
#         user_form = SignUpForm(request.POST)
#         profile_form = ProfileForm(request.POST)
#         next_of_kin_form = NextOfKinForm(request.POST)
#         job_info_form = JobInfoForm(request.POST)
#         referees_form = RefereesForm(request.POST)
#         file_uploads_form = FileUploadsForm(request.POST, request.FILES)
#         if user_form.is_valid() and profile_form.is_valid() and next_of_kin_form.is_valid() and job_info_form.is_valid() and referees_form.is_valid() and file_uploads_form.is_valid():
#             user_form.instance.email = user_form.cleaned_data.get('username')
#             user = user_form.save(commit=False)
#             user.is_active = False
#             user.email = user_form.cleaned_data.get('username')
#             user.save()
#             user.refresh_from_db()
#             # profile
#             profile_form = ProfileForm(request.POST, instance=user.profile)
#             profile_form.full_clean()
#             profile_form.save()
#             # job info
#             job_info_form = JobInfoForm(request.POST, instance=user.job_info)
#             job_info_form.full_clean()
#             job_info_form.save()
#             # Next of kin
#             next_of_kin_form = NextOfKinForm(request.POST, instance=user.next_of_kin)
#             next_of_kin_form.full_clean()
#             next_of_kin_form.save()
#             # referees
#             referees_form = RefereesForm(request.POST, instance=user.referees)
#             referees_form.full_clean()
#             referees_form.save()
#             # file uploads
#             file_uploads_form = FileUploadsForm(request.POST, request.FILES, instance=user.file_uploads)
#             file_uploads_form.full_clean()
#             file_uploads_form.save()
#
#             current_site = get_current_site(request)
#             subject = 'Activate your GRT-Pristine account'
#             message = render_to_string('users/account_activation_email.html', {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token': account_activation_token.make_token(user),
#             })
#             to_email = user_form.cleaned_data.get('username')
#             email = EmailMessage(subject, message, to=[to_email])
#             email.send()
#
#             return HttpResponse('Account activation sent. Please confirm your email address to '
#                                 'complete your registration.')
#     else:
#         user_form = SignUpForm()
#         profile_form = ProfileForm()
#         next_of_kin_form = NextOfKinForm()
#         job_info_form = JobInfoForm()
#         referees_form = RefereesForm()
#         file_uploads_form = FileUploadsForm()
#     return render(request, 'users/signup.html', {'user_form': user_form,
#                                                  'profile_form': profile_form,
#                                                  'next_of_kin_form': next_of_kin_form,
#                                                  'job_info_form': job_info_form,
#                                                  'referees_form': referees_form,
#                                                  'file_uploads_form': file_uploads_form
#                                                  })
#
#
# @login_required
# @transaction.atomic
# def update_profile(request):
#     message = ''
#     if request.method == 'POST':
#         user_form = UserUpdateForm(request.POST, instance=request.user)
#         profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
#         next_of_kin_form = NextOfKinUpdateForm(request.POST, instance=request.user.next_of_kin)
#         job_info_form = JobInfoUpdateForm(request.POST, instance=request.user.job_info)
#         referees_form = RefereesUpdateForm(request.POST, instance=request.user.referees)
#         file_uploads_form = FileUploadsUpdateForm(request.POST, request.FILES, instance=request.user.file_uploads)
#         if user_form.is_valid() and profile_form.is_valid() and next_of_kin_form.is_valid() and job_info_form.is_valid() and referees_form.is_valid() and file_uploads_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             next_of_kin_form.save()
#             job_info_form.save()
#             referees_form.save()
#             file_uploads_form.save()
#             message = messages.success(request, 'Your profile was successfully updated!')
#             return redirect('dashboard')
#         else:
#             message = messages.error(request, 'Please correct the error(s) below to proceed.')
#     else:
#         user_form = UserUpdateForm(instance=request.user)
#         profile_form = ProfileUpdateForm(instance=request.user.profile)
#         next_of_kin_form = NextOfKinUpdateForm(instance=request.user.next_of_kin)
#         job_info_form = JobInfoUpdateForm(instance=request.user.job_info)
#         referees_form = RefereesUpdateForm(instance=request.user.referees)
#         file_uploads_form = FileUploadsUpdateForm(request.FILES, instance=request.user.file_uploads)
#     return render(request, 'users/update_profile.html', {'user_form': user_form,
#                                                          'profile_form': profile_form,
#                                                          'next_of_kin_form': next_of_kin_form,
#                                                          'job_info_form': job_info_form,
#                                                          'referees_form': referees_form,
#                                                          'file_uploads_form': file_uploads_form,
#                                                          'message': message,
#                                                          })
