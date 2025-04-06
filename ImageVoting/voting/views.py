from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count
from django.db import IntegrityError
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

def admin_dashboard(request):
    # Get AdminInfo data
    admin_info = get_admin_info()  # Get the AdminInfo object with site configuration
    
    # In a real app you would protect this view with admin authentication.
    photos = Photo.objects.all().order_by('-votes')  # Get all photos ordered by votes (descending)
    context = {
        'photos': photos,  # All photos ordered by votes
        'admin_info': admin_info,  # Pass the AdminInfo object to the template
    }
    return render(request, 'voting/admin_dashboard.html', context)  # Render the admin dashboard template

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
