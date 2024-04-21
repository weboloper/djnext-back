from django.urls import path
from .views import (
    PostListAPIView, PostDetailAPIView, PostCreateAPIView
)

app_name = "posts"

urlpatterns = [
    path("", PostListAPIView.as_view(), name="list_post"),
    # path("protected", ListPostProtectedAPIView.as_view(), name="list_post_protected"),
    path("create/", PostCreateAPIView.as_view(), name="create_post"),
    # path("slug/<str:slug>/", DetailPostBySlugAPIView.as_view(), name="post_detail_by_slug"),
    path("<int:pk>/", PostDetailAPIView.as_view(), name="post_detail"),
    # path("<int:pk>/comment/", ListCommentAPIView.as_view(), name="list_comment"),
    # path(
    #     "<int:pk>/comment/create/",
    #     CreateCommentAPIView.as_view(),
    #     name="create_comment",
    # ),
    # path(
    #     "<int:pk>/comment/<int:id>/",
    #     DetailCommentAPIView.as_view(),
    #     name="comment_detail",
    # ),
]