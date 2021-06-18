import unicodedata
from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, State, Lga, Profile
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model, authenticate, password_validation
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, identify_hasher,
)
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _


CustomUserModel = get_user_model()


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(max_length=50, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=50, label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone',)
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(max_length=50, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=50, label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone', 'is_active',
                  'is_admin', 'is_staff', 'reg_approved', 'membership_id',)
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):  # User update

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserChangeForm(forms.ModelForm):  # Admin user update
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('gender', 'marital_status', 'religion', 'address', 'state',
                  'lg', 'hometown', 'job_name', 'job_address', 'job_responsibility', 'job_post', 'nok_name',
                  'nok_address', 'nok_relationship', 'nok_occupation', 'nok_age', 'nok_phone', 'ref_name1', 'ref_name2',
                  'ref_phone1', 'ref_phone2', 'ref_id1', 'ref_id2', 'form_receipt', 'applicant_photo', 'applicant_id',
                  'nok_photo', 'nok_id',)
        # labels = {
        #     'lg': 'Local govt. area', 'job_name': 'Name', 'job_address': 'Address',
        #     'job_responsibility': 'Responsibility', 'job_post': 'Post', 'nok_name': 'Full Name',
        #     'nok_address': 'Address',
        #     'nok_relationship': 'Relationship',
        #     'nok_occupation': 'Occupation',
        #     'nok_age': 'Age',
        #     'nok_phone': 'Phone Number',
        #     'ref_name1': 'Name',
        #     'ref_name2': 'Name',
        #     'ref_phone1': 'Phone Number',
        #     'ref_phone2': 'Phone Number',
        #     'ref_id1': 'Membership ID',
        #     'ref_id2': 'Membership ID',
        #     'form_receipt': 'Receipt of form',
        #     'applicant_photo': "Applicant's Passport",
        #     'applicant_id': 'Applicant ID Card',
        #     'nok_photo': "Next of Kin Passport",
        #     'nok_id': 'Next of Kin ID Card',
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lg'].queryset = Lga.objects.none()

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['lg'].queryset = Lga.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['lg'].queryset = self.instance.state.lg_set.order_by('name')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('gender', 'marital_status', 'religion', 'address', 'state',
                  'lg', 'hometown', 'job_name', 'job_address', 'job_responsibility', 'job_post', 'nok_name',
                  'nok_address', 'nok_relationship', 'nok_occupation', 'nok_age', 'nok_phone', 'ref_name1', 'ref_name2',
                  'ref_phone1', 'ref_phone2', 'ref_id1', 'ref_id2', 'form_receipt', 'applicant_photo', 'applicant_id',
                  'nok_photo', 'nok_id', 'reg_receipt')
        # labels = {
        #     'lg': 'Local govt. area', 'job_name': 'Name', 'job_address': 'Address',
        #     'job_responsibility': 'Responsibility', 'job_post': 'Post', 'nok_name': 'Full Name',
        #     'nok_address': 'Address',
        #     'nok_relationship': 'Relationship',
        #     'nok_occupation': 'Occupation',
        #     'nok_age': 'Age',
        #     'nok_phone': 'Phone Number',
        #     'ref_name1': 'Name',
        #     'ref_name2': 'Name',
        #     'ref_phone1': 'Phone Number',
        #     'ref_phone2': 'Phone Number',
        #     'ref_id1': 'Membership ID',
        #     'ref_id2': 'Membership ID',
        #     'form_receipt': 'Receipt of form',
        #     'applicant_photo': "Applicant's Passport",
        #     'applicant_id': 'Applicant ID Card',
        #     'nok_photo': "Next of Kin Passport",
        #     'nok_id': 'Next of Kin ID Card',
        # },

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['lg'].queryset = Lga.objects.none()
    #
    #     if 'state' in self.data:
    #         try:
    #             state_id = int(self.data.get('state'))
    #             self.fields['lg'].queryset = Lga.objects.filter(state_id=state_id).order_by('name')
    #         except (ValueError, TypeError):
    #             pass  # invalid input from the client; ignore and fallback to empty City queryset
    #     elif self.instance.pk:
    #         self.fields['lg'].queryset = self.instance.state.lg_set.order_by('name')


class LoginForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    email = forms.EmailField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.email_field = CustomUserModel._meta.get_field(CustomUserModel.EMAIL_FIELD)
        email_max_length = self.email_field.max_length or 254
        self.fields['email'].max_length = email_max_length
        self.fields['email'].widget.attrs['max_length'] = email_max_length
        if self.fields['email'].label is None:
            self.fields['email'].label = capfirst(self.email_field.verbose_name)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'email': self.email_field.verbose_name},
        )


class UpdatePasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': _('The two password fields did not match.'),
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    }

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
