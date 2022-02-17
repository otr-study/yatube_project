def set_session_user_profile(request, profile=None):
    user_profile = {
        'use_pop_article': True,
        'theme': '',
        'is_authenticated': request.user.is_authenticated
    }
    if profile:
        user_profile['use_pop_article'] = profile.use_pop_article
        user_profile['theme'] = profile.theme
    request.session['user_profile'] = user_profile
