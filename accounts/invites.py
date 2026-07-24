# accounts/invites.py
from django.core import signing


SALT = 'company-invite'

def make_invite_token(company_id, email):
    return signing.dumps(
        {'company_id': str(company_id), 'email': email}, salt=SALT)

def read_invite_token(token, max_age=60 * 60 * 24 * 3):   # 3 jours
    return signing.loads(token, salt=SALT, max_age=max_age)
