from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record
from django.contrib.auth.decorators import login_required
from .ai_utils import analyze_sentiment, categorize_customer, smart_search
from .ai_engagement import (
    segment_customers, generate_recommendations, 
    create_smart_workflow, generate_dynamic_message
)
from .ml_models import predict_churn_probability, analyze_business_metrics
from django.db.models import Avg, Count, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
import json

def home(request):
    records = Record.objects.all()
    
    # Check to see if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')
    else:
        return render(request, 'home.html', {'records':records})

@login_required
def ai_dashboard(request):
    # Get search query from GET parameters
    query = request.GET.get('q', '')
    search_results = []
    
    if query:
        # Perform smart search if there's a query
        records = Record.objects.all()
        search_results = smart_search(query, records)
    
    # Calculate customer categories
    categories = Record.objects.values('customer_category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Convert to dictionary for template
    categories_dict = {cat['customer_category'] or 'Uncategorized': cat['count'] for cat in categories}
    
    # Calculate sentiment metrics
    sentiment_metrics = Record.objects.aggregate(
        avg_sentiment=Avg('sentiment_score'),
        positive_count=Count(Case(When(sentiment_score__gt=0, then=1))),
        negative_count=Count(Case(When(sentiment_score__lte=0, then=1)))
    )
    
    # Get priority customers (sorted by priority score)
    priority_customers = Record.objects.exclude(
        priority_score__isnull=True
    ).order_by('-priority_score')[:5]
    
    context = {
        'query': query,
        'search_results': search_results,
        'categories': categories_dict,
        'avg_sentiment': sentiment_metrics['avg_sentiment'] or 0,
        'positive_count': sentiment_metrics['positive_count'],
        'negative_count': sentiment_metrics['negative_count'],
        'priority_customers': priority_customers,
    }
    
    return render(request, 'ai_dashboard.html', context)

@login_required
def ai_engagement(request):
    if request.user.is_authenticated:
        records = Record.objects.all()
        
        # Calculate segments and prepare message data
        segments = {}
        messages_data = {}
        
        for record in records:
            # Calculate segment based on your criteria
            total_value = record.total_value if hasattr(record, 'total_value') else 0
            if total_value > 1000:
                segment = 'High Value'
            elif total_value < 500:
                segment = 'Need Attention'
            else:
                segment = 'Regular'
            
            segments[record] = segment
            
            # Generate personalized messages
            follow_up = f"Hi {record.first_name}, thank you for your continued business! We noticed you might be interested in our new products."
            promo = f"Dear {record.first_name}, as a valued {segment.lower()} customer, we'd like to offer you a special discount!"
            
            messages_data[str(record.id)] = {
                'followUp': follow_up,
                'promo': promo
            }
            
            # Add AI recommendations
            record.recommendations = [
                {'type': 'follow_up', 'action': 'Send a personalized follow-up message'},
                {'type': 'offer', 'action': 'Present special discount on premium products'}
            ]
            record.follow_up_message = follow_up
            record.promo_message = promo
        
        return render(request, 'ai_engagement.html', {
            'segments': segments,
            'messages_data': json.dumps(messages_data)
        })
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')

@login_required
def smart_workflows(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        workflow_type = request.POST.get('workflow_type')
        
        if customer_id and workflow_type:
            record = Record.objects.get(id=customer_id)
            workflow = create_smart_workflow(record, workflow_type)
            messages.success(request, f"Created new {workflow_type} workflow for {record.first_name}")
            
    # Get all active workflows (for demo, we'll create some sample ones)
    active_workflows = []
    for record in Record.objects.all()[:5]:  # Limit to 5 for demo
        workflow_type = 'support' if record.sentiment_score and record.sentiment_score < 0 else 'sales'
        workflow = create_smart_workflow(record, workflow_type)
        if workflow:
            workflow['id'] = len(active_workflows) + 1
            workflow['record'] = record
            workflow['progress'] = 50  # Demo progress
            workflow['created_at'] = datetime.now()
            active_workflows.append(workflow)
    
    context = {
        'active_workflows': active_workflows,
        'customers': Record.objects.all()
    }
    
    return render(request, 'smart_workflows.html', context)

@login_required
def analytics_dashboard(request):
    # Get all records
    records = Record.objects.all()
    
    # Get business metrics
    metrics = analyze_business_metrics(records)
    
    # Get high-risk customers
    high_risk_customers = []
    for record in records:
        if record.created_at:  # Add null check
            churn_prob = predict_churn_probability({
                'interaction_frequency': 1,  # You would calculate this from actual data
                'last_purchase_days': (timezone.now() - record.created_at).days,
                'total_spend': float(record.price or 0),  # Handle null price
                'support_tickets': 1  # You would get this from actual data
            })
            if churn_prob > 0.7:
                high_risk_customers.append({
                    'customer': record,
                    'churn_probability': round(churn_prob * 100, 1)
                })
    
    context = {
        'metrics': {
            'total_sales': float(metrics['total_sales']),  # Convert Decimal to float for template
            'avg_ticket_value': float(metrics['avg_ticket_value']),  # Convert Decimal to float for template
            'customer_satisfaction': metrics['customer_satisfaction'],
            'churn_risk_customers': metrics['churn_risk_customers']
        },
        'high_risk_customers': high_risk_customers[:5]  # Show top 5 at risk
    }
    
    return render(request, 'analytics_dashboard.html', context)

def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})

    return render(request, 'register.html', {'form':form})

@login_required
def customer_record(request, pk):
    if request.user.is_authenticated:
        # Look Up Records
        customer_record = Record.objects.get(id=pk)
        return render(request, 'record.html', {'customer_record':customer_record})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

@login_required
def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_it = Record.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record Deleted Successfully...")
        return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')

@login_required
def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                record = form.save(commit=False)
                
                # Initialize default values
                record.sentiment_score = 0
                record.customer_category = 'New Customer'
                record.priority_score = 5
                
                # Analyze sentiment from notes if available
                if record.notes:
                    try:
                        record.sentiment_score = analyze_sentiment(record.notes)
                    except Exception as e:
                        print(f"Error analyzing sentiment: {e}")
                        record.sentiment_score = 0
                
                # Categorize customer
                try:
                    record.customer_category = categorize_customer(record.email, record.notes or '')
                except Exception as e:
                    print(f"Error categorizing customer: {e}")
                    record.customer_category = 'New Customer'
                
                # Calculate priority score (1-10) with error handling
                try:
                    record.priority_score = min(10, max(1, int((record.sentiment_score + 1) * 5)))
                except Exception as e:
                    print(f"Error calculating priority score: {e}")
                    record.priority_score = 5
                
                record.save()
                messages.success(request, "Record Added Successfully!")
                return redirect('home')
        return render(request, 'add_record.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')

@login_required
def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = Record.objects.get(id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if form.is_valid():
            record = form.save(commit=False)
            
            # Keep existing values as fallback
            old_sentiment = record.sentiment_score or 0
            old_category = record.customer_category or 'Regular Customer'
            old_priority = record.priority_score or 5
            
            # Update AI analysis with error handling
            if record.notes:
                try:
                    record.sentiment_score = analyze_sentiment(record.notes)
                except Exception as e:
                    print(f"Error analyzing sentiment: {e}")
                    record.sentiment_score = old_sentiment
            
            try:
                record.customer_category = categorize_customer(record.email, record.notes or '')
            except Exception as e:
                print(f"Error categorizing customer: {e}")
                record.customer_category = old_category
            
            try:
                record.priority_score = min(10, max(1, int((record.sentiment_score + 1) * 5)))
            except Exception as e:
                print(f"Error calculating priority score: {e}")
                record.priority_score = old_priority
            
            record.save()
            messages.success(request, "Record Has Been Updated Successfully!")
            return redirect('home')
        return render(request, 'update_record.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')

@login_required
def send_message(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        record_id = request.POST.get('recordId')
        message_type = request.POST.get('type')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        try:
            # Get the customer record
            record = Record.objects.get(id=record_id)
            
            # TODO: Add your message sending logic here
            # For now, we'll just log the message
            print(f"Message sent to {record.first_name} {record.last_name}: {subject}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Message sent successfully'
            })
        except Record.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Customer record not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })
