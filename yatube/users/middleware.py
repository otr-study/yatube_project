from django.shortcuts import get_object_or_404
from users.models import UserProfile
from users.utils import set_session_user_profile


class ProfileMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated
                and not request.session.get('user_profile', False)):
            profile = get_object_or_404(UserProfile, user=request.user)
            set_session_user_profile(request, profile)
        request.user_profile = request.session['user_profile']
        return self._get_response(request)
