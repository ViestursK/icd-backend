from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegistrationSerializer, UserSerializer

class RegisterView(APIView):
    """Handle user registration"""
    permission_classes = [AllowAny]
    def post(self, request):
        print(f"Registration request data: {request.data}")  # Log the incoming data
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Return user information after successful registration
            return Response({
                'id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
            
        print(f"Registration validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """Get authenticated user details or update user information"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return the authenticated user's details"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update the authenticated user's information"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
