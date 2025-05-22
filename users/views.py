from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    """View for user registration."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been successfully created! Welcome to MassiveGameArchive.")
            return redirect('profile')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    """View for displaying user profile."""
    # We'll implement contributed games functionality later
    contributed_games = []

    return render(request, 'users/profile.html', {
        'contributed_games': contributed_games
    })

@login_required
def edit_profile(request):
    """View for editing user profile."""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()

            # Update profile fields
            profile = request.user.profile
            profile.bio = p_form.cleaned_data.get('bio')
            profile.location = p_form.cleaned_data.get('location')

            profile.save()

            messages.success(request, "Your profile has been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

        # Get initial data for the profile form
        initial_data = {
            'bio': request.user.profile.bio,
            'location': request.user.profile.location,
        }
        p_form = ProfileUpdateForm(initial=initial_data)

    return render(request, 'users/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })

def logout_view(request):
    """Custom view for logging out users."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return render(request, 'users/logout.html')
