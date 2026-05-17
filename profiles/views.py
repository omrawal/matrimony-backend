from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

from .models import CustomUser, ProfileViewLog
from .serializers import ProfileViewLogSerializer, UserSerializer


class UserList(generics.ListCreateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = CustomUser.objects.exclude(is_superuser=True)
        user = self.request.user
        
        # If the viewing user is logged in and has configured a gender,
        # return only profiles of the opposite gender.
        if user.is_authenticated and user.gender:
            opposite_gender = 'female' if user.gender == 'male' else 'male'
            return queryset.filter(gender=opposite_gender)
            
        return queryset


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # The host user
        visitor = request.user       # The viewing user

        if visitor.is_authenticated and visitor != instance:
            # Upsert mechanic: updates timestamp if match exists, otherwise creates it
            ProfileViewLog.objects.update_or_create(
                visitor=visitor,
                host=instance,
                defaults={'timestamp': timezone.now()}
            )

        return super().retrieve(request, *args, **kwargs)

# New API endpoint view to read logs belonging to current user
class VisitorHistoryList(generics.ListAPIView):
    serializer_class = ProfileViewLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Fetch views received by the logged in host
        return ProfileViewLog.objects.filter(host=self.request.user)


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserLoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        logout(request)

        return Response({
            'status': 'Successfully logged out'
        }, status=status.HTTP_200_OK)