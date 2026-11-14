from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from .serializers import RegisterSerializer,ListSerializer,ChangePasswordSerializer
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.response import Response
from rest_framework import status

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserDetail(RetrieveAPIView):
    serializer_class=ListSerializer
    permission_class=[IsAuthenticated]
    def get_object(self):
        return self.request.user
        
class UpdateProfile(UpdateAPIView):
    serializer_class=ListSerializer
    permission_classes=[IsAuthenticated]
    def get_object(self):
        return self.request.user
    def perform_update(self,serializer):
        serializer.save()
        print(f"{self.request.user.username} performed update")

class changePassword(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_pass = serializer.validated_data['old_password']
            new_pass = serializer.validated_data['new_password']
            if not user.check_password(old_pass):
                return Response(
                    {'message': 'Old password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(new_pass)
            user.save()
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

from rest_framework_simplejwt.tokens import RefreshToken
class LogoutView(APIView):
    permissions_classes=[IsAuthenticated]
    def post(self,request,view):
        try:
            refresh_token=request.data.get('refresh')
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                    {"message": "Logout successfully"},
                    status=status.HTTP_200_OK
                )
        except:
            return Response({'message':"Enter valid Token"},status=status.HTTP_400_BAD_GATEWAY)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Artist,User,Follow
from django.shortcuts import get_object_or_404
# Logics for Following and Unfollowing Artists

@login_required
@require_POST
def follow(request,artist_id):
    # artist=Artist.objects.get(id=artist_id)
    artist=get_object_or_404(Artist,id=artist_id)
    user=request.user
    follow,created=Follow.objects.get_or_create({'artist':artist,'listener':user})
    return JsonResponse({'message':'Followed'})

from rest_framework import status
@login_required
@require_POST
def unfollow(request,artist_id):
    if request.user.role!='Listener':
        return JsonRequest({'message':'you are not Listener'},status=status.HTTP_401_UNAUTHORIZED)
    artist=get_object_or_404(
        ArtistProfile,
        id=artist_id
    )
    delete_count,_=Follow.objects.get(user=request.user,artist=artist).delete()
    return JsonResponse({'message':'Unfollowed Sucesfully'})













    


    