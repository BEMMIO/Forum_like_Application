import logging

from django.contrib.auth.password_validation import password_validators_help_text_html
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction as tx
from django.utils.html import mark_safe
from django.db import IntegrityError
from django.utils import timezone
from django import forms as f
from django.apps import apps

# Third-Party
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from dev.core.utils.ip import client_ip_address
from dev.users.services import User as user_cls 
from dev.invitation.signals import invite_is_accepted

logger = logging.getLogger(__name__)

USERNAME_RE = r'^[\.\w]+$'


class AuthenticationMixin:
    
    error_messages = {
        "invalid_login": "Login or password is incorrect.",
        "empty_data": "Fill out both fields.",
        "in_active_user": "Your account is currently in-active.",
    }


    def confirm_user_active(self,user):
        """ 
        [*] Did user delete own account ?

        """
        pass


    def confirm_user_not_banned(self,user):
        """
        [*] check if user is banned? display `ban message`
        """
        pass 




# Login-Form
class AuthenticationForm(f.Form,AuthenticationMixin):
    username    =   f.CharField(label="Username",required=True,widget=f.TextInput(attrs={
        'placeholder':'eg. herty','autofocus':True,'autocomplete':"off",
        }))

    password    =   f.CharField(label="Password",widget=f.PasswordInput(attrs={
        'placeholder': '*************'
        }))

    remember_me =   f.BooleanField(label="Remember me",required=False,widget=f.CheckboxInput())
 

    def clean(self):
        from django.contrib.auth import authenticate

        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(username=username, password=password)

            if self.user_cache is None or not self.user_cache.is_active:
                raise ValidationError(
                        self.error_messages["invalid_login"], code="invalid_login"
                )
            else:
                self.confirm_login_for_request(self.user_cache)
        else:
            raise ValidationError(self.error_messages["empty_data"], code="empty_data")
        return self.cleaned_data


    def confirm_login_for_request(self,user):
        self.confirm_user_active(user)
        self.confirm_user_not_banned(user)





class BaseRegisterationForm(f.Form):

    username    = f.RegexField(regex=USERNAME_RE,max_length=15,label="Username (www.devblog.to/@<b class='on-keyup-username'></b>)",required=True,
        error_messages={"invalid":"Username must contain only letters,numbers,dots and underscores."},
        widget=f.TextInput(attrs={'autofocus':True,'autocomplete':"off",
        }))

    email       = f.EmailField(label='Email',required=True,disabled=True,
        widget=f.EmailInput(attrs={'autocomplete':"off",}))

    # captha - required field
    captch      = ReCaptchaField(
                widget=ReCaptchaV3,
                label='',
                help_text=(''),
        )


class RegisterationForm(BaseRegisterationForm):

    password1 = f.CharField(
        label=('Password'), required=True,
        widget=f.PasswordInput(attrs={'autocomplete': 'off'}),
        help_text=("Enter a strong password"))

    password2 = f.CharField(
        label=("Password confirmation"), required=True,
        widget=f.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=("Enter the same password as above, for verification."))


    read_terms_and_agreement = f.BooleanField(label="By signing up, you agree to our <a href='#'><b>terms</b></a> and <a href='#'><b>privacy policy</b></a>. We do not allow adult content.",initial=True,required=True,widget=f.CheckboxInput())


    def __init__(self,*args,invitation=None,**kwargs):
        self.invitation = invitation
        super().__init__(*args,**kwargs)
        self.fields["username"].initial = self.invitation.invite_to_user.username
        self.fields["email"].initial = self.invitation.invite_to_user.email


    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise f.ValidationError("the two password fields didn\'t match.")
        return self.cleaned_data


    def clean_username(self):
        username = self.cleaned_data.get("username")

        user_cache = self.invitation.invite_to_user

        users_qs = user_cls._default_manager.exclude(username__iexact=user_cache.username)

        if user_cache.username != username:
            users_qs = users_qs.filter(username__iexact=username)
            if users_qs.exists():
                raise f.ValidationError("user with username already exists.")
            return self.cleaned_data.get("username")
        return self.cleaned_data.get("username")


    def save(self,force_insert=False,force_update=False,commit=True,**kwargs):
        user = self.invitation.invite_to_user

        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data["email"]
        user.is_active = True

        user.set_password(self.cleaned_data['password2']) 

        user.date_joined = timezone.now()

        # Signal : invitation accepted
        invite_is_accepted.send(sender=None,invite=self.invitation)

        if commit:
            try:
                user.save()
            except IntegrityError:
                raise ValidationError("User is already registered")
        return user