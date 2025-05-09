from django.contrib import admin

from comments.models import Comment, UserCommentLike

admin.site.register(Comment)
admin.site.register(UserCommentLike)