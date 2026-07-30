
#logins imports and decorators
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

def global_context(request):
    if request.user.is_authenticated:
        return {
            "logged_in": True,
            "name": request.user.username,
            
        }
    else:
        return {
            "logged_in": False,
            "name": "foodie",
           
        }