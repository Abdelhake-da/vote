from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count
from django.db import IntegrityError
from .models import Photo, Vote

MAX_VOTES_PER_SESSION = 3  # Maximum number of votes allowed per session

def vote_page(request):
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
        if not Vote.user_has_voted_for_photo(session_key, photo_id) and vote_count >= MAX_VOTES_PER_SESSION:  # Check if adding a new vote would exceed limit
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
                })  # Return JSON response for AJAX requests
            
            return redirect('vote_page')  # Redirect back to vote page for normal requests
        except IntegrityError:
            # This handles the case where a duplicate vote might occur due to race conditions
            return HttpResponseForbidden("An error occurred while processing your vote.")  # Return error if integrity error occurs

    context = {
        'photos': photos,  # All photos
        'vote_count': vote_count,  # Number of votes by this session
        'max_votes': MAX_VOTES_PER_SESSION,  # Maximum allowed votes
        'voted_photo_ids': voted_photo_ids,  # Photos already voted by this session
    }
    return render(request, 'voting/vote_page.html', context)  # Render the vote page template

def admin_dashboard(request):
    # In a real app you would protect this view with admin authentication.
    photos = Photo.objects.all().order_by('-votes')  # Get all photos ordered by votes (descending)
    context = {
        'photos': photos,  # All photos ordered by votes
    }
    return render(request, 'voting/admin_dashboard.html', context)  # Render the admin dashboard template
