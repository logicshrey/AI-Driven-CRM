from django.core.management.base import BaseCommand
from website.models import Record
from website.ai_utils import analyze_sentiment, categorize_customer

class Command(BaseCommand):
    help = 'Adds sample customer records to demonstrate AI features'

    def handle(self, *args, **kwargs):
        # Sample customer data with different sentiments and categories
        sample_customers = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'vip.john@example.com',
                'phone': '1234567890',
                'address': '123 Park Avenue',
                'city': 'New York',
                'state': 'NY',
                'zipcode': '10001',
                'notes': 'Excellent VIP customer. Always satisfied with our premium services. Highly recommends us to others.'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.corp@business.com',
                'phone': '9876543210',
                'address': '456 Business Street',
                'city': 'Chicago',
                'state': 'IL',
                'zipcode': '60601',
                'notes': 'Corporate client experiencing some issues with recent service. Needs immediate attention.'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': 'mike@example.com',
                'phone': '5551234567',
                'address': '789 Main St',
                'city': 'Los Angeles',
                'state': 'CA',
                'zipcode': '90001',
                'notes': 'Regular customer. Generally satisfied but had a complaint about delivery times.'
            },
            {
                'first_name': 'Emily',
                'last_name': 'Wilson',
                'email': 'emily.vip@company.com',
                'phone': '3334445555',
                'address': '321 VIP Road',
                'city': 'Miami',
                'state': 'FL',
                'zipcode': '33101',
                'notes': 'Premium member. Loves our exclusive services. Always provides positive feedback.'
            },
            {
                'first_name': 'David',
                'last_name': 'Lee',
                'email': 'david@support.com',
                'phone': '7778889999',
                'address': '555 Tech Lane',
                'city': 'San Francisco',
                'state': 'CA',
                'zipcode': '94105',
                'notes': 'Frustrated with technical issues. Requires urgent support and follow-up.'
            }
        ]

        for customer_data in sample_customers:
            # Create record
            record = Record(**customer_data)
            
            # Apply AI analysis
            record.sentiment_score = analyze_sentiment(record.notes)
            record.customer_category = categorize_customer(record.email, record.notes)
            record.priority_score = min(10, max(1, int((record.sentiment_score + 1) * 5)))
            
            record.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Added {record.first_name} {record.last_name} - '
                    f'Category: {record.customer_category}, '
                    f'Sentiment: {record.sentiment_score:.2f}, '
                    f'Priority: {record.priority_score}'
                )
            )
