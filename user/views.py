from django.shortcuts import render

# Create your views here.
def profile(request, user_id):
    return render(request, 'user/profile.html', {'user_id': user_id})
