from typing import List

from blog.models import Feed, CustomUser, Post


class FeedPost:

    @staticmethod
    def create_post(users_lst: List[CustomUser], post: Post) -> None:
        for user in users_lst:
            feed_post = Feed(recipient=user,
                             post=post)
            feed_post.save()

    @staticmethod
    def postslist(user: CustomUser) -> List[Post]:
        return Feed.objects.filter(recipient=user)


post_editor = FeedPost()
