def set_session_user_profile(request, profile):
    user_profile = {
        'use_pop_article': profile.use_pop_article,
        'theme': profile.theme
    }
    request.session['user_profile'] = user_profile
