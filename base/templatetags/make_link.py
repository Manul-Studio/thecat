from django import template

register = template.Library()


@register.filter
def hashtag_link(word):
    description= word.description + ' '
    hashtags = word.hashtags.all()
    for hashtag in hashtags:
        description = description.replace('#' + hashtag.description + ' ', f'<a href="/posts/{hashtag.pk}/hashtag/">#{hashtag.description} </a>')
    return description