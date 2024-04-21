from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Custom permission to check if the user is owner of the object. 
    """
    message = "You can not delete another user"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        print(obj, request.user)
        return obj == request.user

class IsVerified(BasePermission):
    """
    Custom permission to check if the user is owner of the object. 
    """
    message = "You must verify your email."

    def has_permission(self, request, view):
 
        return request.user.is_verified



class IsOwnerOrReadOnlyOrIsStaff(BasePermission):
    """
    Custom permission to check if the user is owner of the object. 
    """
    message = "You must be the owner of this object."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
        # if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        if request.user.is_staff:
            return True
        return obj.author == request.user

