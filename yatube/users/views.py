from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, View

from .forms import CreationForm, UserProfileForm
from .models import UserProfile
from .utils import set_session_user_profile


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        form = UserProfileForm(instance=profile)
        return render(
            request,
            'users/user_profile.html',
            {
                'form': form,
                'profile': profile
            }
        )

    def post(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        form = UserProfileForm(
            request.POST or None,
            instance=profile,
            files=request.FILES or None
        )
        if form.is_valid():
            new_profile = form.save()
            set_session_user_profile(request, new_profile)
            cache.clear()
            return redirect('posts:index')
        return render(
            request,
            'users/user_profile.html',
            {
                'form': form,
                'profile': profile
            }
        )
