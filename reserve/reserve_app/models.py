from django.db import models
from django.contrib.auth.models import User
from django.db.models import F, Q


# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated')

    class Meta:
        abstract = True


class RoomCategory(TimeStampedModel):
    name = models.CharField(unique=True, max_length=100, verbose_name='Name')
    capacity = models.PositiveSmallIntegerField(default=1, verbose_name='Capacity')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price Per Night')
    description = models.TextField(blank=True, verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Active') 
    #i perefered to not to do something original xd

    class Meta:
        db_table = 'room_category'
        verbose_name = 'Room Category'
        verbose_name_plural = 'Room Categories'
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return f'{self.name} ({self.capacity} oc.)' #own creationw


class Room(TimeStampedModel): #hääääääääää??
    floor = models.PositiveSmallIntegerField(default=1, verbose_name='Floor')
    number = models.CharField(max_length=10, unique=True, verbose_name="Room's number")
    category = models.ForeignKey(
        RoomCategory,
        on_delete = models.PROTECT,
        related_name='rooms',
        verbose_name='Category',
    )
    is_active = models.BooleanField(default=True, verbose_name='Avalilable For Reserving')

    class Meta:
        db_table = 'room'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['number']
        indexes = [models.Index(fields=['category', 'number'])]

    def __str__(self):
        return f'#{self.number} - {self.category.name}'


class BookingStatus(models.TextChoices):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELED = 'canceled'


class Booking(TimeStampedModel):
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name='bookings', verbose_name='Room'
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='bookings', verbose_name='User'
    )
    check_in = models.DateField(verbose_name='Anfahren')
    check_out = models.DateField(verbose_name='Ausfahren')
    status = models.CharField(
        max_length=10,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name='Status'
    )

    def __str__(self):
        return f'{self.user.username} - {self.room}'


    class Meta:
        db_table = 'booking'
        verbose_name = 'Reserving'
        verbose_name_plural = 'Reserving'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['check_in', 'check_out'])]