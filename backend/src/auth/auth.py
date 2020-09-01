import json
from flask import request, _request_ctx_stack,abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-tg3jd163.us.auth0.com'#udacity-fsnd.auth0.com
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffe_shop'#dev

class AuthError(Exception):
        def __init__(self, error, status_code):
            self.error = error
            self.status_code = status_code

def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)
    # ____________________________________________________________________________________________________

# ___________________________________________________AUTH___________________________________________________

def get_token_auth_header():
    # Check if Authorization is present in the header or not
    if 'Authorization' not in request.headers:
        abort(401)

    # 'Authorization': 'Bearer <TOKEN>'
    # ['Bearer', '<TOKEN>']
    auth_header = request.headers['Authorization'].split(' ')
    # print(auth_header)

    if len(auth_header) != 2:
        abort(401)
    elif auth_header[0].lower() != 'bearer':
        abort(401)
    return auth_header[1]

def check_permission(permissions, payload):
    if 'permissions' not in payload:
        abort(400)
    for permission in permissions:
        if permission not in payload['permissions']:
            abort(401)
    return True

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permission(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
# ______________________________________________________________________________________________________
