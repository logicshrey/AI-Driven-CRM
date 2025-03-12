from django.db import models


class Record(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    last_name =  models.CharField(max_length=50)
    email =  models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address =  models.CharField(max_length=100)
    city =  models.CharField(max_length=50)
    state =  models.CharField(max_length=50)
    zipcode =  models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    notes = models.TextField(blank=True, null=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    customer_category = models.CharField(max_length=50, blank=True, null=True)
    priority_score = models.IntegerField(default=0)

    def __str__(self):
        return(f"{self.first_name} {self.last_name}")
