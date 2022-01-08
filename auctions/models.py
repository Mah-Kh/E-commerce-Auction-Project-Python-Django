from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db import models


class User(AbstractUser):
    pass 

             
    
class Listing(models.Model):
    UNCATEGORIZED = 'UN'
    FASHION = 'FA'
    TOYS = 'TO'
    ELECTRONIC = 'EL'
    HOME = 'HO'
    category = [
        (UNCATEGORIZED, 'Uncategorized'),
        (FASHION, 'Fashion'),
        (TOYS, 'Toys'),
        (ELECTRONIC, 'Electronics'),
        (HOME, 'Home'),
    ]
    
    category = models.CharField(
        max_length=2,
        choices=category,
        default=UNCATEGORIZED,
    )
    title = models.CharField(max_length=150)
    end_list = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    starting_bid = models.IntegerField(blank=True, null=True)
    current_bid = models.IntegerField(blank=True, null=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    image_URL = models.CharField(max_length=255, null=True, blank=True)
        
    def __str__(self):
        return f"{self.title}"


class Bid (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=150, null=True)
    new_bid = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}: {self.new_bid}"  
        
        

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user} {self.title}"
                
      
        
class Comment (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.comment})"


