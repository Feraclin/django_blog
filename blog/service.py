from typing import List

from blog.models import Feed, CustomUser, Post



class FeedPost:

    @staticmethod
    def create_post(users_lst: List[CustomUser], post: Post) -> None:
        Feed.objects.bulk_create([Feed(recipient=user, post=post) for user in users_lst])

post_editor = FeedPost()
