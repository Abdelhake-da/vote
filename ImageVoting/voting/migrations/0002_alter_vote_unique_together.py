# Generated by Django 5.2 on 2025-04-06 04:50

from django.db import migrations
from django.db.models import Count


def remove_duplicate_votes(apps, schema_editor):
    # Get the Vote model from the migration state
    Vote = apps.get_model('voting', 'Vote')
    
    # Find all duplicate votes (same session_key and photo)
    duplicates = Vote.objects.values('photo_id', 'session_key').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    # For each set of duplicates, keep only one and delete the rest
    for duplicate in duplicates:
        # Get all votes for this photo and session
        votes = Vote.objects.filter(
            photo_id=duplicate['photo_id'],
            session_key=duplicate['session_key']
        ).order_by('timestamp')
        
        # Keep the first vote (oldest) and delete the rest
        first_vote = votes.first()
        if first_vote:
            votes.exclude(id=first_vote.id).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        # First run the function to remove duplicates
        migrations.RunPython(remove_duplicate_votes),
        # Then add the unique constraint
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together={('photo', 'session_key')},
        ),
    ]
