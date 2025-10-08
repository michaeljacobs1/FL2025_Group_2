"""
Django management command to generate sample financial data
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from api.projection_service import DataGenerator


class Command(BaseCommand):
    help = 'Generate sample financial data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to generate data for (default: creates a new user)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='demo@example.com',
            help='Email for the user',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        
        # Create or get user
        if username:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
        else:
            # Create a demo user
            user, created = User.objects.get_or_create(
                username='demo_user',
                defaults={'email': email}
            )
        
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created user: {user.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Using existing user: {user.username}')
            )
        
        # Generate sample data
        try:
            # Generate financial profile
            #profile = DataGenerator.generate_sample_financial_profile(user)
            self.stdout.write(
                self.style.SUCCESS(f'Generated financial profile for {user.username}')
            )
            
            # Generate income entries
            DataGenerator.generate_sample_income_entries(user)
            self.stdout.write(
                self.style.SUCCESS(f'Generated income timeline for {user.username}')
            )
            
            # Generate projections
            projections = DataGenerator.generate_sample_projections(user)
            self.stdout.write(
                self.style.SUCCESS(f'Generated {len(projections)} projections for {user.username}')
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully generated sample data for {user.username}!\n'
                    f'You can now login with username: {user.username} and password: demo123'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating sample data: {str(e)}')
            )

