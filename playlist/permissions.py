from rest_framework.permissions import BasePermission, SAFE_METHODS

class MusicPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        elif request.method in ('PATCH', 'DELETE'):
            return request.user.is_staff or request.user.is_superuser
        elif request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return False
        
class IsPlayListOwner(BasePermission):
    def has_object_permission(self,request,view,obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user==obj.user
