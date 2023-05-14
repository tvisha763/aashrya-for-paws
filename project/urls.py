from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('addShelter', views.addShelter, name="addShelter"),
    path('donate', views.donate, name="donate"),
    path('findShelter', views.findShelter, name="findShelter"),
    path('donated', views.donated, name="donated"),
    path('addDog', views.addDog, name="addDog"),
    path('shelterDogs/<int:shelter_id>/', views.shelterDogs, name="shelterDogs"),
    path('dogDetails/<int:dog_id>/', views.dogDetails, name="dogDetails"),
    path('deleteShelter', views.deleteShelter, name="deleteShelter"),
    path('adopted', views.adopted, name="adopted"),
    path('euthanized', views.euthanized, name="euthanized"),
]