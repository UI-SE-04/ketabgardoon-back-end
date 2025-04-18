from django.db import models


# from users.models import User

class Comment(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserCommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
