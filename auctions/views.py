from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import ModelForm
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse


from .models import User, Listing, Bid, Comment, Watchlist

        
        
class NewListing(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'starting_bid', 'image_URL']
        
class NewComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        
class NewBid(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['new_bid']  


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
       
        
def index(request):    
    listings = Listing.objects.all() 
    active_listings = []
    for i in range(len(listings)):
        active = listings[i]
        if active.end_list == False:
            active_listings.append(active)  
    
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })  
      


def alllistings(request):
    listings = Listing.objects.all()
    
    return render(request, "auctions/alllistings.html", {
        "listings": listings
    }) 
       

          
def listing(request, listing_title): 
    if request.method == "POST":
        user = request.user
            
        if user.is_authenticated:
        
            listing = Listing.objects.get(title=listing_title)
            active_list = Listing.objects.get(title=listing_title).end_list == False
            
            bid_form = NewBid(request.POST)
            form = NewComment(request.POST)
        
            watchlist_btn = request.POST.get('watchlist')
            if watchlist_btn == "Add to watchlist": 
                if active_list:
                    title = listing_title
                    id = listing.id
                    user = request.user 
                    watchlist = Watchlist.objects.filter(title=id, user=user)
                    if watchlist:
                        return render(request, "auctions/error.html", {"error": "This item is already in your watchlist"}) 
                    else:                
                        watchlist = Watchlist()
                        watchlist.user = request.user
                        watchlist.title = Listing.objects.get(title=title)
                        watchlist.save()
                        watchlist_id = watchlist.id 
                        return HttpResponseRedirect(reverse("auctions:title", args=(listing_title,)))
                else:
                    warning = "Auction is ended."
                    return render(request, "auctions/error.html", {"warning": warning})
                
            endlist_btn = request.POST.get('endlist')
            if endlist_btn == "end auction":
                if Listing.objects.get(title=listing_title).end_list == False:
                    title = listing_title 
                    item_to_end = Listing.objects.get(title=title)
                    item_to_end.end_list = True
                    item_to_end.save()
                    return HttpResponseRedirect(reverse("auctions:title", args=(listing_title,)))
       
                return HttpResponseRedirect(reverse("auctions:title", args=(listing_title,)))            
   
            bid_btn = request.POST.get('bid')
            if bid_btn == "Bid":
                if bid_form.is_valid():
                    if active_list:
                        bid = bid_form.save(commit=False)
                        bid.user = request.user 
                        bid.title = listing_title   
                        
                        if listing.current_bid > 0:
                            if bid.new_bid is not None:
                                if bid.new_bid > listing.current_bid:
                                    bid.save()
                                    listing.current_bid = Bid.objects.filter(title=listing_title).last().new_bid
                                    listing.save()                                     
                                    return HttpResponseRedirect(reverse("auctions:title", args=(listing_title,))) 
                                else:
                                    warning = "Bid must be greater than current bid"
                                    return render(request, "auctions/error.html", {"warning": warning})                    
                        else:
                            listing.current_bid = listing.starting_bid 
                            if bid.new_bid is not None:
                                if bid.new_bid > listing.current_bid:
                                    listing.current_bid = Bid.objects.filter(title=listing_title).last()
                                    bid.save()
                                    listing.save()
                                    return HttpResponseRedirect(reverse("auctions:title", args=(listing_title,))) 
                                else:
                                    warning = "Bid must be greater than starting bid"
                                    return render(request, "auctions/error.html", {"warning": warning}) 
                    else:
                        warning = "Auction is ended."
                        return render(request, "auctions/error.html", {"warning": warning})                                
            
            comment_btn = request.POST.get('new_comment')
            if comment_btn == "Submit": 
                if form.is_valid():
                    if active_list:
                        comments = form.save(commit=False)
                        comments.user = request.user 
                        comments.title = listing_title
                        user_comment = comments.comment
                        comments.save()
                        return HttpResponseRedirect(reverse("auctions:title", args=(listing_title,)))
                    else:
                        warning = "Auction is ended."
                        return render(request, "auctions/error.html", {"warning": warning}) 

        else:       
            return render(request, "auctions/login.html") 
        
    if request.method == "GET":
        listing = Listing.objects.get(title=listing_title)
        comments = Comment.objects.filter(title=listing_title)
        auctions_owner = Listing.objects.get(title=listing_title).user
        user = request.user 
               
        bid = Bid.objects.filter(title=listing_title)
        
        if bid: 
            listing.current_bid = Bid.objects.filter(title=listing_title).last().new_bid
            listing.save()
            
            sold = Listing.objects.get(title=listing_title).end_list == True
            if sold:
                title = Listing.objects.get(title=listing_title).title;
                winner = Bid.objects.filter(title=title).last().user 
                if winner == user:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bid_form":NewBid(),
                        "form": NewComment(),
                        "comments": comments,
                        "winner": winner
                    })
                    
            if auctions_owner == user:        
                return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_form":NewBid(),
                "form": NewComment(),
                "comments": comments,
                "owner": user
                })
                
            return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid_form":NewBid(),
            "form": NewComment(),
            "comments": comments,
            "non_owner": user
            })
        
        else:        
            if auctions_owner == user:        
                return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_form":NewBid(),
                "form": NewComment(),
                "comments": comments,
                "owner": user
                })
            
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_form":NewBid(),
                "form": NewComment(),
                "comments": comments,
                "non_owner": user
            })
        

@login_required(login_url='auctions:login')
def create(request):
    if request.method == "POST":
        form = NewListing(request.POST)
        if form.is_valid():            
            listing = form.save(commit=False) 
            title = listing.title            
            listing.user = request.user
            listing.save()
            return HttpResponseRedirect(reverse("auctions:index"))
             
            
    return render(request, "auctions/create.html", {
        "form": NewListing()
    })
           
      
def userlisting(request):
    user = request.user   
    user_listings = Listing.objects.filter(user=user) 

    return render(request, "auctions/userlisting.html", {
        "listings": user_listings
    }) 


def deletelisting(request,listing_id=None):
    item_to_delete=Listing.objects.get(id=listing_id)
    item_to_delete.delete()
    
    user = request.user   
    user_listings = Listing.objects.filter(user=user)
    return render(request, "auctions/userlisting.html", {
        "listings": user_listings
    }) 
       
      
def watchlist(request):
    watchlists = Watchlist.objects.all()
    user = request.user    
    watchlist_user = Watchlist.objects.filter(user=user)
    
    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlist_user
    }) 
    
    
def delete(request,watchlist_id=None):
    item_to_delete=Watchlist.objects.get(id=watchlist_id)
    item_to_delete.delete()
    
    return HttpResponseRedirect(reverse("auctions:watchlist"))
        
def category(request):    
    return render(request, "auctions/category.html") 
    
    
def fashion(request):
    listings = Listing.objects.all()
    fashion = []
    for i in range(len(listings)):        
        if listings[i].category == "FA":      
            fashion.append(listings[i])
    return render(request, "auctions/fashion.html", {
        "listings": fashion
    })
    
    
def toys(request):
    listings = Listing.objects.all()
    toys = []
    for i in range(len(listings)):        
        if listings[i].category == "TO":      
            toys.append(listings[i])
    return render(request, "auctions/toys.html", {
        "listings": toys
    })
    
    
def electronics(request):
    listings = Listing.objects.all()
    electronics = []
    for i in range(len(listings)):        
        if listings[i].category == "EL":      
            electronics.append(listings[i])
    return render(request, "auctions/electronics.html", {
        "listings": electronics
    })
       

def home(request):
    listings = Listing.objects.all()
    home = []
    for i in range(len(listings)):        
        if listings[i].category == "HO":      
            home.append(listings[i])
    return render(request, "auctions/home.html", {
        "listings": home
    })  
    
def uncategorized(request):
    listings = Listing.objects.all()
    uncategorized = []
    for i in range(len(listings)):        
        if listings[i].category == "UN":      
            uncategorized.append(listings[i])
    return render(request, "auctions/uncategorized.html", {
        "listings": uncategorized
    })
    
def error(request):
    return render(request, "auctions/error.html") 
