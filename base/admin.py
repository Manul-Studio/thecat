from django.contrib import admin

from.models import User, Post, Message, Profile, Hashtag, Location



class ProfileInline(admin.StackedInline):
    model = Profile
    

class UserAdmin(admin.ModelAdmin):
    model= User

    inlines = [ProfileInline]

admin.site.register(User, UserAdmin)
admin.site.register(Post)

admin.site.register(Message)
admin.site.register(Hashtag)
admin.site.register(Location)