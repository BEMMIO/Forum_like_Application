from django.contrib.auth.password_validation import password_validators_help_text_html
# from django.core.exceptions import ValidationError
from django.core.validators import ValidationError, validate_email
from django.db import transaction as tx
from django.db import IntegrityError
from django.utils import timezone
from django.utils.html import mark_safe
from django import forms
from django.db.models.fields import (
    EmailField,
)

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from dev.core.tasks import create_new_user_task,send_invite_email
from .models import Invitation,InvitationChoices
from .signals import invite_is_sent


def valid_email_or_none(email):
    ret = None
    try:
        if email:
            validate_email(email)
            if len(email) <= EmailField().max_length:
                ret = email
    except ValidationError:
        pass
    return ret

class InvitationForm(forms.ModelForm):
    # # ToDo: with from_user full_name.
    # built_message = """Hey,am a message from me !
    # """

    invite_to_user_email = forms.EmailField(label="",required=True,max_length=32,widget=forms.EmailInput(attrs={
        'placeholder':'Invite by email address','autocomplete':"off"}))

    # message = forms.CharField(label="",help_text=mark_safe("<b>You can leave blank.</b>"),required=False,widget=forms.Textarea(attrs={
    #     'placeholder':'Message to send to this e-mail address'}))

    # captha - required field
    captch      = ReCaptchaField(
                widget=ReCaptchaV3,
                label='',
                help_text=(''),
        )

    class Meta:
        model = Invitation
        # fields = ['invite_to_user_email','message']
        fields = ['invite_to_user_email',]



    def __init__(self,request,*args,**kwargs):
        self.request = request
        self.from_user = self.request.user
        super(self.__class__,self).__init__(*args,**kwargs)
        # self.fields["message"].initial = self.built_message


    # def clean_message(self):
    #     message = self.cleaned_data.get('message')
    #     # validate content

    #     is_empty = bool(len(message))
    #     if not is_empty:
    #         message = self.built_message
    #         return message
    #     return self.cleaned_data["message"]

    def validate_email(self,data):
        data = data.split("@")[:-1]
        count_dots = "".join(data).count(".")
        
        if count_dots >= 2:
            raise ValidationError("This email type is not allowed.")


    def clean_invite_to_user_email(self):
        # Clean me!
        email = self.cleaned_data.get('invite_to_user_email')

        self.validate_email(email)
        
        qs = Invitation._default_manager.filter(invite_to_user_email__iexact=email)

        if qs.exists():
            if (qs[0].status == InvitationChoices.ACCEPTED) and qs[0].invite_to_user.is_active:
                raise forms.ValidationError("User with this e-mail already exists")
            elif (qs[0].status == InvitationChoices.SENT) and not qs[0].invite_to_user.is_active:
                if not qs[0].invite_from_user == self.from_user:
                    raise forms.ValidationError("A user with this e-mail has already been invited")
                else:
                    raise forms.ValidationError("You have already invited someone with this email")
        if self.from_user.email == email:
            raise forms.ValidationError("Sorry,you cannot send an invite to yourself")
        return self.cleaned_data.get('invite_to_user_email')



    def save(self,force_insert=False,force_update=False,commit=True,**kwargs):
        invite = super().save(commit=False)
        invite.invite_from_user = self.from_user
        invite.sent_date = timezone.now()
        invite.invite_sent()
        
        with tx.atomic():
            if commit:
                invite.save()
                # Signal : invite sent
                invite_is_sent.send(sender=None,invite=invite)
                # celery : create user
                create_new_user_task(invite)
                # celery : send email
                # send_invite_email(invite)
            return invite