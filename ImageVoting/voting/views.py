from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth.decorators import login_required  # Import login_required decorator
from django.contrib.auth import authenticate, login, logout  # Import authentication functions
from django.contrib import messages  # Import messages framework
from .models import Photo, Vote, AdminInfo  # Import AdminInfo model

# Get AdminInfo data or create default if it doesn't exist
def get_admin_info():
    """
    Get the AdminInfo object or create a default one if it doesn't exist
    
    Returns:
        AdminInfo: The AdminInfo object with site configuration
    """
    admin_info, created = AdminInfo.objects.get_or_create(pk=1)  # Get or create the AdminInfo object
    return admin_info  # Return the AdminInfo object

def vote_page(request):
    # Get AdminInfo data
    admin_info = get_admin_info()  # Get the AdminInfo object with site configuration
    
    # Use session key to track votes.
    if not request.session.session_key:  # Check if session key exists
        request.session.create()  # Create a new session if it doesn't exist
    session_key = request.session.session_key  # Get the session key

    # Count how many votes have been cast by this session.
    vote_count = Vote.objects.filter(session_key=session_key).count()  # Count votes by this session
    photos = Photo.objects.all()  # Get all photos

    # Get the IDs of photos this user has already voted for
    voted_photo_ids = Vote.objects.filter(session_key=session_key).values_list('photo_id', flat=True)  # Get photos already voted by this session

    if request.method == 'POST':  # If this is a POST request (user is voting)
        photo_id = request.POST.get('photo_id')  # Get the photo ID from the form
        
        # Check if this would exceed the maximum votes (only if adding a new vote)
        if not Vote.user_has_voted_for_photo(session_key, photo_id) and vote_count >= admin_info.max_votes:  # Check if adding a new vote would exceed limit
            return HttpResponseForbidden("You have reached the maximum number of votes.")  # Return error if max votes reached
            
        photo = get_object_or_404(Photo, pk=photo_id)  # Get the photo object
        
        try:
            # Toggle the vote (add or remove)
            vote_added, message = Vote.toggle_vote(session_key, photo_id)  # Toggle the vote using our new method
            
            # If AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if this is an AJAX request
                return JsonResponse({
                    'success': True,  # Operation was successful
                    'vote_added': vote_added,  # Whether vote was added (True) or removed (False)
                    'message': message,  # Message describing the action
                    'vote_count': Vote.objects.filter(session_key=session_key).count(),  # Updated vote count
                    'max_votes': admin_info.max_votes,  # Pass max_votes from AdminInfo
                })  # Return JSON response for AJAX requests
            
            return redirect('vote_page')  # Redirect back to vote page for normal requests
        except IntegrityError:
            # This handles the case where a duplicate vote might occur due to race conditions
            return HttpResponseForbidden("An error occurred while processing your vote.")  # Return error if integrity error occurs

    context = {
        'photos': photos,  # All photos
        'vote_count': vote_count,  # Number of votes by this session
        'max_votes': admin_info.max_votes,  # Maximum allowed votes from AdminInfo
        'voted_photo_ids': voted_photo_ids,  # Photos already voted by this session
        'page_title': admin_info.title_of_the_page,  # Page title from AdminInfo
        'page_description': admin_info.description_of_the_page,  # Page description from AdminInfo
    }
    return render(request, 'voting/vote_page.html', context)  # Render the vote page template

def login_view(request):
    """
    Handle user login
    
    Args:
        request: The HTTP request object
    
    Returns:
        HttpResponse: Redirect to admin dashboard on success or render login form
    """
    # Check if user is already logged in
    if request.user.is_authenticated:  # Check if user is already authenticated
        return redirect('admin_dashboard')  # Redirect to admin dashboard if already logged in
    
    # Handle login form submission
    if request.method == 'POST':  # Check if this is a POST request (form submission)
        username = request.POST.get('username')  # Get username from form
        password = request.POST.get('password')  # Get password from form
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)  # Try to authenticate with provided credentials
        
        if user is not None:  # If authentication was successful
            login(request, user)  # Log the user in
            # Redirect to the page they were trying to access, or admin dashboard
            next_page = request.GET.get('next', 'admin_dashboard')  # Get the next parameter or default to admin_dashboard
            return redirect(next_page)  # Redirect to the next page
        else:  # If authentication failed
            messages.error(request, "Invalid username or password.")  # Show error message
    
    # Render the login form
    return render(request, 'voting/login.html')  # Render the login template

def logout_view(request):
    """
    Handle user logout
    
    Args:
        request: The HTTP request object
    
    Returns:
        HttpResponse: Redirect to login page
    """
    logout(request)  # Log the user out
    messages.success(request, "You have been logged out successfully.")  # Show success message
    return redirect('login')  # Redirect to login page

@login_required  # Require login to access this view
def admin_dashboard(request):
    """
    Display admin dashboard with settings and upload functionality
    
    Args:
        request: The HTTP request object
    
    Returns:
        HttpResponse: Render the admin dashboard template
    """
    # Get AdminInfo data
    admin_info = get_admin_info()  # Get the AdminInfo object with site configuration
    
    # In a real app you would protect this view with admin authentication.
    photos = Photo.objects.all().order_by('-votes')  # Get all photos ordered by votes (descending)
    
    # Get upload status messages from session if they exist
    upload_error = request.session.pop('upload_error', None)  # Get and remove error message
    upload_success = request.session.pop('upload_success', None)  # Get and remove success message
    
    context = {
        'photos': photos,  # All photos ordered by votes
        'admin_info': admin_info,  # Pass the AdminInfo object to the template
        'upload_error': upload_error,  # Pass error message to template
        'upload_success': upload_success,  # Pass success message to template
    }
    return render(request, 'voting/admin_dashboard.html', context)  # Render the admin dashboard template

@login_required  # Require login to access this view
def statistics_dashboard(request):
    """
    Display statistics and analytics data
    
    Args:
        request: The HTTP request object
    
    Returns:
        HttpResponse: Render the statistics dashboard template
    """
    # Get AdminInfo data
    admin_info = get_admin_info()  # Get the AdminInfo object with site configuration
    
    # Get all photos ordered by votes
    photos = Photo.objects.all().order_by('-votes')  # Get all photos ordered by votes (descending)
    
    # Prepare data for the timeline chart
    # Get votes from the last 7 days
    end_date = timezone.now()  # Current date and time
    start_date = end_date - timedelta(days=7)  # 7 days ago
    
    # Get votes grouped by day
    votes_by_day = Vote.objects.filter(
        timestamp__gte=start_date,  # Filter votes from the last 7 days
        timestamp__lte=end_date  # Up to current time
    ).extra(
        select={'date': "DATE(timestamp)"}  # Extract the date part of the timestamp
    ).values('date').annotate(count=Count('id')).order_by('date')  # Group by date and count votes
    
    # Prepare data for the chart
    dates = []  # List to store dates
    counts = []  # List to store vote counts
    
    # Fill in any missing dates with zero counts
    current_date = start_date.date()  # Start with the first date
    while current_date <= end_date.date():  # Loop through all dates
        # Check if we have votes for this date
        votes_on_date = next((item for item in votes_by_day if item['date'] == current_date), None)  # Find votes for this date
        
        # Add the date to our list (formatted for display)
        dates.append(current_date.strftime('%Y-%m-%d'))  # Format date as YYYY-MM-DD
        
        # Add the vote count (or 0 if no votes)
        counts.append(votes_on_date['count'] if votes_on_date else 0)  # Add vote count or 0
        
        # Move to the next day
        current_date += timedelta(days=1)  # Increment date by 1 day
    
    context = {
        'photos': photos,  # All photos ordered by votes
        'admin_info': admin_info,  # Pass the AdminInfo object to the template
        'vote_dates': json.dumps(dates),  # Pass dates as JSON for the chart
        'vote_counts': json.dumps(counts),  # Pass vote counts as JSON for the chart
    }
    return render(request, 'voting/statistics_dashboard.html', context)  # Render the statistics dashboard template

@login_required  # Require login to access this view
def update_admin_info(request):
    """
    Update the AdminInfo settings
    
    Args:
        request: The HTTP request object
    
    Returns:
        HttpResponse: Redirect to admin dashboard after update
    """
    # In a real app you would protect this view with admin authentication
    if request.method == 'POST':  # Check if this is a POST request
        # Get the AdminInfo object
        admin_info = get_admin_info()  # Get the AdminInfo object
        
        # Update the fields from the form data
        admin_info.max_votes = int(request.POST.get('max_votes', 3))  # Get max_votes from form, default to 3
        admin_info.title_of_the_page = request.POST.get('title_of_the_page', 'Vote for Your Favorite Photos')  # Get title from form, with default
        admin_info.description_of_the_page = request.POST.get('description_of_the_page', 'Vote for your favorite photos and show your love for them.')  # Get description from form, with default
        
        # Save the updated AdminInfo
        admin_info.save()  # Save the updated AdminInfo object
        
    # Redirect back to the admin dashboard
    return redirect('admin_dashboard')  # Redirect to admin dashboard

@login_required  # Require login to access this view
def upload_photo(request):
    """
    Handle photo upload from the admin dashboard
    
    Args:
        request: The HTTP request object
    
    Returns:
        HttpResponse: Redirect to admin dashboard after upload
    """
    # In a real app you would protect this view with admin authentication
    if request.method == 'POST':  # Check if this is a POST request
        # Get form data
        title = request.POST.get('title')  # Get the photo title from the form
        description = request.POST.get('description', '')  # Get the photo description (optional)
        image = request.FILES.get('image')  # Get the uploaded image file
        
        # Debug information
        print(f"Upload attempt - Title: {title}, Image: {image is not None}")  # Print debug info
        
        # Validate the data
        if title and image:  # Make sure we have at least a title and image
            try:
                # Make sure the media directory exists
                import os
                from django.conf import settings
                media_root = settings.MEDIA_ROOT
                photos_dir = os.path.join(media_root, 'photos')
                
                # Create directories if they don't exist
                if not os.path.exists(media_root):
                    os.makedirs(media_root)
                if not os.path.exists(photos_dir):
                    os.makedirs(photos_dir)
                
                # Create a new Photo object
                photo = Photo(
                    title=title,  # Set the title
                    description=description,  # Set the description
                    image=image,  # Set the image
                    votes=0  # Initialize votes to 0
                )
                photo.save()  # Save the new photo to the database
                print(f"Photo saved successfully: {photo.id}")  # Print success message
                
                # Check if the image was saved correctly
                if photo.image and hasattr(photo.image, 'url'):
                    print(f"Image URL: {photo.image.url}")  # Print image URL
                    # Set success message in session
                    request.session['upload_success'] = f"Photo '{title}' uploaded successfully!"
                else:
                    print("Image URL not available")  # Print error message
                    # Set error message in session
                    request.session['upload_error'] = "Image was saved but URL is not available."
            except Exception as e:
                # Log the error
                print(f"Error saving photo: {str(e)}")  # Print error message
                # Set error message in session
                request.session['upload_error'] = f"Error uploading photo: {str(e)}"
        else:
            # Log what's missing
            error_msg = []
            if not title:
                print("Title is missing")  # Print error message
                error_msg.append("Title is required")
            if not image:
                print("Image is missing")  # Print error message
                error_msg.append("Image file is required")
            
            # Set error message in session
            request.session['upload_error'] = "Upload failed: " + ", ".join(error_msg)
            
    # Redirect back to the admin dashboard
    return redirect('admin_dashboard')  # Redirect to admin dashboard
