from django.contrib import admin

from.models import User, Post, Topic, Message, Profile



class ProfileInline(admin.StackedInline):
    model = Profile
    

class UserAdmin(admin.ModelAdmin):
    model= User

    inlines = [ProfileInline]

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Message)
