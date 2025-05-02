from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('create-transaction/',views.create_transction,name='create-transction'),
    path('create-form/', views.create_transaction_form, name='create_transaction_form'),
]