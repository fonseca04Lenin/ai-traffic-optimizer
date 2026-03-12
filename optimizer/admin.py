from django.contrib import admin
from .models import Driver, Job, Route, RouteStop


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 0
    readonly_fields = ('stop_order',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_type', 'max_daily_distance', 'is_available', 'created_at')
    list_filter = ('vehicle_type', 'is_available')
    search_fields = ('name', 'phone')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'address', 'service_type', 'priority', 'status', 'driver', 'created_at')
    list_filter = ('priority', 'status', 'service_type')
    search_fields = ('customer_name', 'address')
    autocomplete_fields = ('driver',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'driver', 'stop_count', 'total_distance_km', 'estimated_duration_mins', 'created_at')
    inlines = [RouteStopInline]

    def stop_count(self, obj):
        return obj.stop_count()
    stop_count.short_description = 'Stops'


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('route', 'stop_order', 'job')
