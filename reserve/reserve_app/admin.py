from django.contrib import admin
from .models import Booking, Room, RoomCategory


@admin.register(RoomCategory)
class RoomCategAdmin(admin.ModelAdmin):
    list_display = ("name", "short_content")
    search_fields = ("name")

    def short_content(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"


class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "short_content")
    search_fields = ("number")
    filter_horizontal = ("floor")

    def short_content(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"


admin.site.register(Room, RoomAdmin)


@admin.register(Booking)
class BookAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "status")
    list_filter = ("room", "status")
    search_fields = ("room", "user")
    filter_horizontal = ("user",)


