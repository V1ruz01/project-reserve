from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import F, Q

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        abstract = True   


class RoomCategory(TimeStampedModel):
    """Категорія кімнати: стандарт, люкс тощо."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва")
    capacity = models.PositiveSmallIntegerField(default=1, verbose_name="Місткість, осіб")
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Ціна за ніч")
    description = models.TextField(blank=True, verbose_name="Опис")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        db_table = "room_category"                      
        verbose_name = "Категорія кімнати"               
        verbose_name_plural = "Категорії кімнат"        
        ordering = ["name"]                              
        indexes = [models.Index(fields=["name"])]       

    def __str__(self):
        return f"{self.name} ({self.capacity} ос.)"


class Room(TimeStampedModel):
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер кімнати")
    floor = models.PositiveSmallIntegerField(default=1, verbose_name="Поверх")
    category = models.ForeignKey(
        RoomCategory,
        on_delete=models.PROTECT,                        
        related_name="rooms",
        verbose_name="Категорія",
    )
    is_active = models.BooleanField(default=True, verbose_name="Доступна для бронювання")

    class Meta:
        db_table = "room"
        verbose_name = "Кімната"
        verbose_name_plural = "Кімнати"
        ordering = ["number"]
        indexes = [models.Index(fields=["category", "number"])]

    def __str__(self):
        return f"№{self.number} — {self.category.name}"


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Очікує"
    CONFIRMED = "confirmed", "Підтверджено"
    CANCELED = "canceled", "Скасовано"


class Booking(TimeStampedModel): 
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name="bookings", verbose_name="Кімната"
    )
    user = models.ForeignKey( 
        User, on_delete=models.PROTECT, related_name="bookings", verbose_name="Користувач"
    )
    check_in = models.DateField(verbose_name="Заїзд")
    check_out = models.DateField(verbose_name="Виїзд")
    status = models.CharField(
        max_length=10,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name="Статус",
    )
    comment = models.TextField(blank=True, verbose_name="Коментар")

    class Meta:
        db_table = "booking"
        verbose_name = "Бронювання"
        verbose_name_plural = "Бронювання"
        ordering = ["-created_at"]  
        constraints = [
            models.CheckConstraint(
                check=Q(check_out__gt=F("check_in")),
                name="check_out_gt_check_in",
            )
        ]
        indexes = [
            models.Index(fields=["room", "check_in", "check_out"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"Бронювання #{self.pk or '—'} — {self.room} ({self.check_in} → {self.check_out})"

    @property
    def nights(self) -> int: 
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0
 
    def clean(self):
        """Валідація даних перед збереженням (спрацьовує і в адмінці)."""
        super().clean()
 
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValidationError("Дата виїзду має бути пізніше дати заїзду.")
 
        if self.room and self.check_in and self.check_out:
            qs = Booking.objects.filter(
                room=self.room,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED], 
                check_in__lt=self.check_out,
                check_out__gt=self.check_in,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)   
            if qs.exists():
                raise ValidationError("Обраний період уже зайнятий для цієї кімнати.")

    def save(self, *args, **kwargs): 
        self.full_clean()
        return super().save(*args, **kwargs)