from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, EmailSubmissionSerializer, EmailVerificationSerializer, CustomUserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
class EmailSubmissionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            return Response({"message": "email is sent", "email": user.email}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "verification code is valid", "email": serializer.validated_data['email']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCompletionView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email, is_temporary=True, is_email_verified=False)
        except CustomUser.DoesNotExist:
            return Response({"error": "temporary user not found or email is not verified of not exists"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            user = serializer.update(user, serializer.validated_data)
            return Response({
                "message": "sign up was successful",
                "user": CustomUserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)