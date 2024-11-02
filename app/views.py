from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *

def Registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html')

        # Create the new user if the username is not taken
        user = User.objects.create_user(
            username=username, 
            first_name=first_name,
            last_name=last_name, 
            email=email, 
            password=password
        )
        user.save()
        messages.success(request, "Account created successfully.")
        return redirect('login')  # Redirect to login after successful registration

    # Render the registration form for GET request
    return render(request, 'signup.html')



def Login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')

def Logout(request):
    if request.user.is_authenticated:
        logout(request)  
    return redirect('/login')  

def Home(request):
    return render(request, 'home.html')

@login_required
def seller_dashboard(request):
    # Ensure the user is authenticated before accessing the dashboard
    if not request.user.is_authenticated:
        return redirect('login')
    # Fetch seller's properties and other relevant data
    seller_id = request.user.id
    properties = Property.objects.filter(seller_id=seller_id)
    
    context = {
        'seller_id': seller_id,
        'properties': properties
    }
    # Render the seller dashboard with the context
    return render(request, 'seller_dashboard.html', context)



