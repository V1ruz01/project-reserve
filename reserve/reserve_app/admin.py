from django.contrib import admin
from .models import RoomCategory, Room, Booking

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ("user", "check_in", "check_out", "status")
    show_change_link = True
    raw_id_fields = ("user", "room")

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "price_per_night", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "category", "floor", "is_active")
    list_filter = ("category", "is_active", "floor")
    search_fields = ("number",)
    list_editable = ("is_active",)
    inlines = [BookingInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "check_in", "check_out", "nights", "status", "created_at")
    list_filter = ("status", "room", "check_in", "user")
    search_fields = ("user__username", "user__email", "room__number")
    date_hierarchy = "check_in"
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user", "room")
