import json

from celery import shared_task
from django.core.mail import send_mail

from blog.models import CustomUser, Feed
from blog.serializers import FeedSerializerEmail


@shared_task()
def send_feed() -> None:
    '''Sends an email with last 5 post
    '''

    def send_email_task(email_address, message):

        print(f'{message} sent to {email_address}')

    users_lst = CustomUser.objects.iterator()

    for user in users_lst:
        feed_lst = Feed.objects.filter(recipient=user).select_related('post').order_by('-post_id')[:5]
        json_payload = FeedSerializerEmail(feed_lst, many=True).data
        json_str = json.dumps(json_payload)
        send_email_task(email_address=user.email, message=f'{user.first_name} your feed are ready{json_str}')

