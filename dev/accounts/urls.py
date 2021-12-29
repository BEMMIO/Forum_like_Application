from django.urls import path
from .views import auth
from .views import invitation_view 

app_name = 'accounts'

urlpatterns = [
    # Accounts Authentication
    path('register/<str:hash_email>/<str:code>/',auth.register,name='register'),
    path('login/',auth.login,name='login'),
    path('logout/',auth.logout,name='logout'),


    # Invitation
    path('invitation/',invitation_view.create_invitation,name='create-invitation'),
]

