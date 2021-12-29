import secrets

from django.apps import apps
from dev.invitation.models import Invitation as invitation_model_cls,InvitationChoices

# Get a safe-User
user_model_cls = apps.get_model('users', 'User') 


def generate_random_code_for_invite():
    '''
    > assume user model as a invite_code field
    > use signals to assign code to that field when user is created

    user.invite_code = generate_random_code_for_invite()

    '''
    code = generate_random_code()
    while is_code_available(code):
        code = generate_random_code()
    return code


def generate_random_code():
    # generate code in format "ABCD-FGHI-JKLM"
    code = secrets.token_hex(nbytes=6).upper()
    return "-".join(code[i : i + 4] for i in range(0, len(code), 4)) 


def is_code_available(code):
    return user_model_cls._default_manager.filter(invite_code__iexact=code).exists()


def invitation_code_exists(code:str) -> bool:
    # invitation code exists? True if it does, else False
    qs = invitation_model_cls._default_manager
    return qs.filter(invite_token__iexact=code).exists()


def is_invitation_code_expired(code:str) -> bool:
    pass


def get_invitation_object_for_code(code:str):
    pass






