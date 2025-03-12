import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

def predict_churn_probability(customer_data):
    """
    Predict the probability of customer churn based on their data
    """
    # Example features: interaction_frequency, last_purchase_days, total_spend, support_tickets
    features = [
        customer_data.get('interaction_frequency', 0),
        customer_data.get('last_purchase_days', 0),
        float(customer_data.get('total_spend', 0)),
        customer_data.get('support_tickets', 0)
    ]
    
    # Normalize features (in production, you'd load a pre-trained scaler)
    features = np.array(features).reshape(1, -1)
    
    # Simple neural network for demonstration
    model = keras.Sequential([
        keras.layers.Dense(8, activation='relu', input_shape=(4,)),
        keras.layers.Dense(4, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    
    # In production, you'd load pre-trained weights
    # For demo, return a probability based on simple rules
    last_purchase = features[0][1]
    tickets = features[0][3]
    
    if last_purchase > 90 and tickets > 5:
        return 0.8
    elif last_purchase > 60:
        return 0.5
    return 0.2

def analyze_business_metrics(records, days=30):
    """
    Analyze business metrics and detect anomalies
    """
    today = timezone.now()
    start_date = today - timedelta(days=days)
    
    # Convert records to DataFrame
    metrics = {
        'total_sales': Decimal('0.00'),
        'avg_ticket_value': Decimal('0.00'),
        'customer_satisfaction': 0,
        'churn_risk_customers': 0
    }
    
    if records:
        # Calculate metrics
        recent_records = [r for r in records if r.created_at and r.created_at >= start_date]
        
        if recent_records:
            # Calculate total sales and average ticket value
            prices = [r.price or Decimal('0.00') for r in recent_records]
            total_sales = sum(prices)
            avg_ticket = total_sales / len(recent_records) if recent_records else Decimal('0.00')
            
            # Calculate satisfaction score
            satisfaction_scores = [float(r.sentiment_score or 0) for r in recent_records]
            satisfaction = sum(satisfaction_scores) / len(recent_records) if satisfaction_scores else 0
            
            # Count high-risk customers
            high_risk = sum(1 for r in recent_records if predict_churn_probability({
                'interaction_frequency': 1,
                'last_purchase_days': (today - r.created_at).days,
                'total_spend': float(r.price or 0),
                'support_tickets': 1
            }) > 0.7)
            
            metrics.update({
                'total_sales': round(total_sales, 2),
                'avg_ticket_value': round(avg_ticket, 2),
                'customer_satisfaction': round(satisfaction * 20, 1),  # Scale to 0-100
                'churn_risk_customers': high_risk
            })
    
    return metrics
