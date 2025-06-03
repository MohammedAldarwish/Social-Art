from django.urls import path
from .views import LoginView, RegisterView, LogoutView, FollowUserView, MyProfileView, OtherProfileView, UserSearchView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("follow/", FollowUserView.as_view() , name="follow"),
    path("my-profile/", MyProfileView.as_view(), name="my-profile"),
    path("profile/<str:username>/", OtherProfileView.as_view(), name="other-profile"),
    
    #the search is for username 
    path("search/", UserSearchView.as_view(), name="user-search")
    
    
]