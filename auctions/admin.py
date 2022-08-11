from django.contrib import admin
from .models import Auction, Bid, Category, Comment, User

# Register your models here.

admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(User)