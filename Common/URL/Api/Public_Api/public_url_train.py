from django.urls import path
from Common.VIEW.Api.Public_Api import public_api_train_view

urlpatterns = [

path('api/create_train_booking', public_api_train_view.create_train_booking),
path('api/search_train_booking', public_api_train_view.get_train_booking),

]