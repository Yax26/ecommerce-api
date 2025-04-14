from django.urls import path

from .views import Registration, Logout, Login, ResetPassword


app_name = "customer"

urlpatterns = [

    path("registration/", Registration.as_view()),

    path("logout/", Logout.as_view()),

    path("login/", Login.as_view()),

    path("resetpassword/", ResetPassword.as_view()),


]
