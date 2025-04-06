from django.db import models

class Photo(models.Model):
    title = models.CharField(max_length=100)  # Field to store the title of the photo
    image = models.ImageField(upload_to='photos/')  # Field to store the image file
    description = models.TextField(blank=True)  # Field to store optional description
    votes = models.PositiveIntegerField(default=0)  # Field to track the total number of votes

    def __str__(self):
        return self.title  # Return the title as the string representation

class Vote(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)  # Relationship to the Photo being voted on
    session_key = models.CharField(max_length=40)  # Field to identify a voter session
    timestamp = models.DateTimeField(auto_now_add=True)  # Field to record when the vote was cast

    def __str__(self):
        return f"Vote for {self.photo.title} by {self.session_key}"  # String representation of the vote

    @classmethod
    def user_has_voted_for_photo(cls, session_key, photo_id):
        """
        Check if a user has already voted for a specific photo

        Args:
            session_key: The session key identifying the user
            photo_id: The ID of the photo to check

        Returns:
            bool: True if the user has already voted for this photo, False otherwise
        """
        return cls.objects.filter(session_key=session_key, photo_id=photo_id).exists()

    @classmethod
    def toggle_vote(cls, session_key, photo_id):
        """
        Toggle a vote for a specific photo - add vote if not voted, remove if already voted

        Args:
            session_key: The session key identifying the user
            photo_id: The ID of the photo to toggle vote for

        Returns:
            tuple: (bool, str) - (True if vote added, False if vote removed, message describing the action)
        """
        # Get the photo object
        photo = Photo.objects.get(pk=photo_id)  # Get the photo by ID

        # Check if user has already voted for this photo
        existing_vote = cls.objects.filter(session_key=session_key, photo_id=photo_id).first()  # Look for existing vote

        if existing_vote:
            # User already voted, so remove the vote
            existing_vote.delete()  # Delete the vote record

            # Decrease the vote counter
            photo.votes = max(0, photo.votes - 1)  # Decrement vote count (ensure it doesn't go below 0)
            photo.save()  # Save the updated photo

            return False, "Vote removed"  # Return False to indicate vote was removed
        else:
            # User hasn't voted, so add a vote
            cls.objects.create(photo=photo, session_key=session_key)  # Create a new vote

            # Increase the vote counter
            photo.votes += 1  # Increment the vote count
            photo.save()  # Save the updated photo

            return True, "Vote added"  # Return True to indicate vote was added

class AdminInfo(models.Model):
    max_votes = models.IntegerField(default=3)  # Maximum number of votes allowed per session
    title_of_the_page = models.CharField(max_length=100, default="Vote for Your Favorite Photos")
    description_of_the_page = models.TextField(default="Vote for your favorite photos and show your love for them.")

    def __str__(self):
        return f"Admin Info - Max Votes: {self.max_votes}, Title: {self.title_of_the_page}, Description: {self.description_of_the_page}"
