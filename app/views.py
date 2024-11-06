from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import PropertyForm
from django.urls import reverse
from django.template import loader

def index(request):
    return render(request, 'index.html')

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

def Properties(request):
    property=Property.objects.all()
    context={
        'property':property
    }
    return render(request,'property.html',context)


@login_required
def update_property(request, property_id):
    # Get the property and check if it belongs to the current user
    property_instance = get_object_or_404(Property, id=property_id, seller=request.user)
    
    # If it's a POST request, handle the form submission
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_instance)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')  # Redirect to dashboard after updating
    else:
        form = PropertyForm(instance=property_instance)

    # Render the update page
    return render(request, 'update_property.html', {'form': form})


@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)  # Include request.FILES for image upload
        if form.is_valid():
            property = form.save(commit=False)
            property.seller = request.user
            # Set availability based on checkbox
            is_available = request.POST.get('is_available')
            property.is_available = True if is_available == "on" else False
            property.save()
            return redirect('allproperties')  # Redirect to avoid resubmission on page refresh
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})

@login_required
def property_list(request):
    properties = Property.objects.filter(seller=request.user)
    return render(request, 'properties/property_list.html', {'properties': properties})

@login_required
def seller_bookings(request):
    # Fetch properties listed by the logged-in seller and related bookings
    properties = Property.objects.filter(seller=request.user).select_related('seller')
    bookings = Booking.objects.filter(property__in=properties).select_related('property', 'client')
    
    # Prepare context for the template
    context = {
        'bookings': bookings,
    }
    return render(request, 'seller_bookings.html', context)

@login_required
def property_detail(request, property_id):
    # Retrieve the property by ID or return a 404 if not found
    property = get_object_or_404(Property, id=property_id)
    
    # Initialize booking to None; will only populate if the user has an active booking
    booking = None
    
    # Check if the authenticated user has any booking for this property
    if request.user.is_authenticated:
        booking = Booking.objects.filter(property=property, client=request.user).first()
    
    # Determine if the property is available for booking:
    # - It should be available
    # - Either no booking exists for this user, or the existing booking was rejected
    is_available = property.is_available and (booking is None or booking.approval_status == 'rejected')

    # Prepare context data for rendering
    context = {
        'property': property,
        'booking': booking,
        'is_available': is_available,
    }
    
    # Render the property detail page with context
    return render(request, 'property_details.html', context)


@login_required
def book_property(request, property_id):
    # Retrieve the property; ensure it is available
    property = get_object_or_404(Property, id=property_id, is_available=True)
    
    # Check if the user already has a pending or approved booking for this property
    existing_booking = Booking.objects.filter(
        property=property, client=request.user, approval_status__in=['pending', 'approved']
    ).first()
    
    if existing_booking:
        # Redirect to property details with a message if a booking already exists
        messages.warning(request, "You already have a pending or approved booking for this property.")
        return redirect('property_detail', property_id=property.id)

    # Create a new booking if no previous booking exists
    Booking.objects.create(property=property, client=request.user, is_booked=True, approval_status='pending')
    
    # Redirect to a confirmation or properties page with a success message
    messages.success(request, "Your booking request has been submitted and is pending approval.")
    return redirect(reverse('property_detail', args=[property.id]))

def booking_list(request):
    bookings = Booking.objects.all()  # Retrieve all bookings, or filter by user if needed
    return render(request, 'booking_list.html', {'bookings': bookings})


