from django.shortcuts import render

# Create your views here.
def profile(request, user_id):
    return render(request, 'custom_users/profile.html', {'user_id': user_id})
# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            pass
            #return redirect('home')
    else:
        form = CustomUserCreationForm()
    pass
    #return render(request, 'accounts/register.html', {'form': form})

