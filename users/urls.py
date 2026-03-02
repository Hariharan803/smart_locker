from django.urls import path
from .views import RegisterUserView, MyTokenObtainPairView, MyTokenRefreshView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
]