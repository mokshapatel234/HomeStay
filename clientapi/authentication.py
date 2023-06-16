from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

class JWTAuthentication(BaseJSONWebTokenAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization')

        if not auth:
            return None

        token = auth.strip()

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        try:
            payload = self.decode_token(token)
            client = self.authenticate_payload(payload)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return (client, token)
