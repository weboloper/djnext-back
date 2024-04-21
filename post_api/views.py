from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment
from .serializers import PostListSerializer,PostDetailSerializer, PostCreateUpdateSerializer
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from .permissions import IsOwnerOrReadOnlyOrIsStaff, IsOwner, IsVerified
from .pagination import (PostPagePagination, PaginationHandlerMixin)
from django.http import Http404


class PostListAPIView(APIView, PaginationHandlerMixin):

    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PostPagePagination

                        
    def get(self, request, format=None, *args, **kwargs):
        instance = Post.objects.all()
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(PostListSerializer(page, many=True).data)
        else:
            serializer = PostListSerializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class PostDetailAPIView(APIView):

    permission_classes = [ IsOwnerOrReadOnlyOrIsStaff]

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        serializer = PostDetailSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Eğer gerekirse POST, PUT ve DELETE metotları da burada tanımlanabilir.

class PostCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVerified]
    def post(self, request, format=None):
        serializer = PostCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    