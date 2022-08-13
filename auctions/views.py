from datetime import datetime
from email.mime import image
import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import ModelForm, TextInput
from django.utils import timezone

from .models import Auction, Bid, Category, Comment, User

class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['item_name',
                  'image',
                  'item_description',
                  'start_bid',
                  'duration',
                  'category']

    def __init__(self, *args, **kwargs):
        super(AuctionForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['message']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = 'form-control w-75 h-75'

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control m-2'

class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['message']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = 'form-control w-75 h-75'


def auction_bid(request, id):
    bid_form = BidForm(request.POST or None)

    if bid_form.is_valid():
        auction = Auction.objects.get(pk=id)
        new_bid = bid_form.save(commit=False)
        current_bids = Bid.objects.filter(auction=auction)
        is_highest_bid = all(new_bid.amount > n.amount for n in current_bids)
        is_valid_first_bid = new_bid.amount >= auction.start_bid

        if is_highest_bid and is_valid_first_bid:
            new_bid.auction = auction
            new_bid.user = request.user
            new_bid.save()

    url = reverse('auction', kwargs={'id': id})
    return HttpResponseRedirect(url)

def auction_comment(request, id):
    comment_form = CommentForm(request.POST or None)

    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.user = request.user
        new_comment.auction = Auction.objects.get(pk=id)
        new_comment.save()

    url = reverse('auction', kwargs={'id': id})
    return HttpResponseRedirect(url)

def auction_close(request, id):
    auction = Auction.objects.get(pk=id)
    auction.ended_manually = True;
    auction.save()

    url = reverse('auction', kwargs={'id': id})
    return HttpResponseRedirect(url)


#listing all active auctions (not wathced)
def index(request):
    active_auctions = Auction.objects.filter(ended_manually=False, end_time__gte=datetime.now())
    if request.user.is_authenticated:
        active_auctions = active_auctions.exclude(pk__in=request.user.watchlist.all().values("pk"))
    
        print(active_auctions.values("image"))
    return render(request, "auctions/index.html",{
        "auctions": active_auctions,
        "title": "Curently active"
    })

def wiev_watched(request):
    wathced_auctions = request.user.watchlist.all()

    return render(request, "auctions/index.html",{
        "auctions": wathced_auctions,
        "title": "Watched"
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def category(request, id):
    params = {}
    params["categoryes"] = Category.objects.filter(~Q(pk=id))
    params["category_chousen"] = category_chousen = Category.objects.get(pk=id)
    params["auctions"] = Auction.objects.filter(ended_manually=False, end_time__gte=datetime.now(), category=category_chousen)

    return render(request ,"auctions/category.html", params)

def category_list(request):
    params = {}
    params["categories"] = Category.objects.all()

    return render(request ,"auctions/category_list.html", params)

def auction(request, id):
    # check that auction exists
    try:
        auction = Auction.objects.get(id=id)
    except:
        return HttpResponse("Entry does not exist")


    context = {}
    context["auction"] = auction

    if auction.is_finshed():
        context["ended"] = True
        return render(request, "auctions/auction.html", context)

    context["ended"] = False

    # calculate times
    time_remaining = auction.end_time - timezone.now()
    context["days"] = time_remaining.days
    context["hours"] = int(time_remaining.seconds / 3600)
    context["minutes"] = int(time_remaining.seconds / 60 - (context["hours"] * 60))
    context["bid_form"] = BidForm()
    context["comment_form"] = CommentForm()

    return render(request, "auctions/auction.html", context)

def watch_auction(request, id):
    auction = Auction.objects.get(pk=id)
    watched_auctions = request.user.watchlist
    if auction in watched_auctions.all():
        watched_auctions.remove(auction)
    else:
        watched_auctions.add(auction)

    url = reverse('auction', kwargs={'id': id})
    return HttpResponseRedirect(url)


def create_auction(request):
    form = AuctionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_listing = form.save(commit=False)
        new_listing.user = request.user
        new_listing.save()

        url = reverse('auction', kwargs={'id': new_listing.id})
        return HttpResponseRedirect(url)

    else:
        return render(request, "auctions/create_auction.html", {
            'form': form
        })
    
    

