import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import json


AUTH0_DOMAIN = 'fsnd-udacity-21.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffe-shop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """obtain the token from the authorization header
    checks for the correct input format of the header
    """
    auth = request.headers.get("Authorization", None)

    if not auth:
        raise AuthError({
        "code" : "Authorization header has not been given",
        "description": "Authorization header is expected"
        }, 401)

    parts = auth.split() 

    if parts[0].lower() != "bearer":
        raise AuthError({
        "code": "invalid_header",
        "description": "Auhtorization header must start with Bearer"
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    token = parts[1]
    return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if "permissions" not in payload:
        raise AuthError({
            "code": "invalid_claims",
            "description": "Permissions not included in JWT"
        }, 400)
        
    if permission not in payload["permissions"]:
        raise AuthError({
            "code": "unauthorised",
            "description": " Permission not found"
        }, 403)

    return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    """decode the jwt token and verifies it has the key id against the Auth0 service, it decodes the payload and validates the claim
    """
    # Get the public key from the AUTH0 service
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jkws = json.loads(jsonurl.read())

    # get the data from the header
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if "kid" not in unverified_header:
        raise AuthError({
            "code": "invalid_header",
            "description": "Authorization malformed"
        }, 401)

    for key in jkws["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            # use the key to validate the payload
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/"
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                "code": "token_expired",
                "description": "Token expired"
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                "code": "invalid_claims",
                "description": "Incorrect claims. Please, check the audiance and issuer"
            }, 401)

        except Exception:
            raise AuthError({
                "code": "invalid_header",
                "description": "Unable to parse authentication token"
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                # raise AuthError({
                #     "code": "invalid_token",
                #     "descriotion": "Access denied due to invalid token"
                # }, 401)
                abort(401)

            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


