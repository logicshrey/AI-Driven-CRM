from datetime import datetime, timedelta
from sklearn.cluster import KMeans
import numpy as np

def segment_customers(records):
    """
    Segment customers based on interaction patterns and sentiment
    """
    if not records:
        return {}
    
    # Create feature matrix from customer data
    features = []
    for record in records:
        sentiment = record.sentiment_score if record.sentiment_score is not None else 0
        priority = record.priority_score if record.priority_score is not None else 0
        features.append([sentiment, priority])
    
    # Perform clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(features)
    
    # Map clusters to segments
    segments = {
        0: 'High Value',
        1: 'Growth Potential',
        2: 'Need Attention'
    }
    
    # Create customer segments dictionary
    customer_segments = {}
    for record, cluster in zip(records, clusters):
        customer_segments[record.id] = segments[cluster]
    
    return customer_segments

def generate_recommendations(record):
    """
    Generate personalized recommendations based on customer data
    """
    recommendations = []
    
    # Check sentiment score
    if record.sentiment_score is not None:
        if record.sentiment_score < 0:
            recommendations.append({
                'type': 'support',
                'priority': 'high',
                'action': 'Schedule follow-up call',
                'reason': 'Recent negative feedback detected'
            })
        elif record.sentiment_score > 0.8:
            recommendations.append({
                'type': 'sales',
                'priority': 'medium',
                'action': 'Upsell premium services',
                'reason': 'Customer shows high satisfaction'
            })
    
    # Check customer category
    if record.customer_category == 'vip':
        recommendations.append({
            'type': 'engagement',
            'priority': 'high',
            'action': 'Send VIP event invitation',
            'reason': 'VIP customer engagement program'
        })
    elif record.customer_category == 'business':
        recommendations.append({
            'type': 'sales',
            'priority': 'medium',
            'action': 'Schedule business review',
            'reason': 'Quarterly business check-in'
        })
    
    return recommendations

def create_smart_workflow(record, interaction_type):
    """
    Create automated workflow based on customer interaction
    """
    workflows = {
        'support': {
            'steps': [
                {
                    'action': 'Create support ticket',
                    'assignee': 'support_team',
                    'deadline': datetime.now() + timedelta(hours=24)
                },
                {
                    'action': 'Schedule follow-up call',
                    'assignee': 'account_manager',
                    'deadline': datetime.now() + timedelta(hours=48)
                }
            ],
            'priority': 'high' if record.priority_score and record.priority_score > 7 else 'medium'
        },
        'sales': {
            'steps': [
                {
                    'action': 'Prepare proposal',
                    'assignee': 'sales_team',
                    'deadline': datetime.now() + timedelta(days=3)
                },
                {
                    'action': 'Schedule presentation',
                    'assignee': 'account_manager',
                    'deadline': datetime.now() + timedelta(days=7)
                }
            ],
            'priority': 'high' if record.customer_category == 'vip' else 'medium'
        },
        'onboarding': {
            'steps': [
                {
                    'action': 'Welcome email',
                    'assignee': 'system',
                    'deadline': datetime.now() + timedelta(hours=1)
                },
                {
                    'action': 'Setup guide',
                    'assignee': 'support_team',
                    'deadline': datetime.now() + timedelta(days=1)
                },
                {
                    'action': 'First check-in call',
                    'assignee': 'account_manager',
                    'deadline': datetime.now() + timedelta(days=7)
                }
            ],
            'priority': 'medium'
        }
    }
    
    return workflows.get(interaction_type, {})

def generate_dynamic_message(record, message_type):
    """
    Generate personalized message based on customer data and interaction type
    """
    templates = {
        'follow_up': {
            'positive': f"Hi {record.first_name}, thank you for your positive feedback! We're glad you're enjoying our services. Would you be interested in learning about our premium features?",
            'negative': f"Hi {record.first_name}, we noticed you had some concerns. Our team would like to help resolve any issues you're experiencing. When would be a good time to talk?",
            'neutral': f"Hi {record.first_name}, we value your business! How can we help you get the most out of our services?"
        },
        'promotion': {
            'vip': f"Exclusive VIP offer for you, {record.first_name}! As a valued premium customer, you get early access to our new features.",
            'business': f"Special business promotion: Upgrade your plan and get premium support included.",
            'general': f"Hi {record.first_name}, check out our latest offerings tailored for you!"
        }
    }
    
    if message_type not in templates:
        return ""
    
    if message_type == 'follow_up':
        if record.sentiment_score > 0.3:
            return templates['follow_up']['positive']
        elif record.sentiment_score < -0.3:
            return templates['follow_up']['negative']
        else:
            return templates['follow_up']['neutral']
    
    if message_type == 'promotion':
        if record.customer_category == 'vip':
            return templates['promotion']['vip']
        elif record.customer_category == 'business':
            return templates['promotion']['business']
        else:
            return templates['promotion']['general']
