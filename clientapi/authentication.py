from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from superadmin.models import *
import jwt
from rest_framework import permissions

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.headers.get('Authorization', None)
        
        if jwt_token:
            try:
                payload = jwt.decode(jwt_token, 'secret', algorithm='HS256')
            except (jwt.DecodeError, jwt.ExpiredSignatureError) as e:
                print(e)
                raise exceptions.AuthenticationFailed('Token is invalid')
        else:
            raise exceptions.AuthenticationFailed('Token is required')
        
    

        try:
            request.user = Client.objects.get(id=payload['user_id'])
        except Client.DoesNotExist:
            raise exceptions.AuthenticationFailed('Client not found.')

        return (request.user, jwt_token)


class IsClientVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.session.get('client_verified', False)
        return False
