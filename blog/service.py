from typing import Iterator

from blog.models import Feed, CustomUser, Post


class FeedPost:

    @staticmethod
    def create_post(users_lst: Iterator[CustomUser], post: Post) -> None:
        tasks = []
        for user in users_lst:
            tasks.append(Feed(recipient=user, post=post))
            if len(tasks) >= 1000:
                Feed.objects.bulk_create(tasks)
                tasks.clear()
        if tasks:
            Feed.objects.bulk_create(tasks)


post_editor = FeedPost()
