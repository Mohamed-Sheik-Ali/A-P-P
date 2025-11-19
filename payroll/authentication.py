from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .jwt_utils import decode_jwt_token


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication backend for Django REST Framework
    """
    
    def authenticate(self, request):
        """
        Authenticate a user using JWT token from Authorization header
        """
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not authorization_header:
            return None
        
        try:
            # Check if header starts with 'Bearer '
            if not authorization_header.startswith('Bearer '):
                return None
            
            # Extract token
            token = authorization_header[7:]  # Remove 'Bearer ' prefix
            
            # Decode token
            payload = decode_jwt_token(token)
            
            if payload is None:
                raise AuthenticationFailed('Invalid or expired token')
            
            # Get user from payload
            try:
                user = User.objects.get(id=payload['user_id'])
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found')
            
            if not user.is_active:
                raise AuthenticationFailed('User is inactive')
            
            return (user, token)
            
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return the header name to use for challenges.
        """
        return 'Bearer'
