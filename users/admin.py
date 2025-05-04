from django.contrib import admin
from .models import User, Movie, Comic, Blog, Like, Comment, Profile, Testimonial, CharacterCard

admin.site.register(User)
admin.site.register(Movie)
admin.site.register(Comic)
# admin.site.register(Blog)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Testimonial)
admin.site.register(CharacterCard)