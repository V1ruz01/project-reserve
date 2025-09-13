from django.urls import path
from . import views


app_name = 'reserve_app'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('bookings/', views.my_booking, name='my_bookings'),
    path('bookings/<int:pk>', views.booking_cancel, name='booking_cancel'),
]


