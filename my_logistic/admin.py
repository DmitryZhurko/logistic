from django.contrib import admin
from .models import Driver, Cars, Applications, Cargo


class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'age')


class CarsAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'registration_mark', 'color', 'free')


class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'auto', 'execution', 'executed')


class CargoAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance', 'route', 'weight', 'free', 'executed')


admin.site.register(Driver, DriverAdmin)
admin.site.register(Cars, CarsAdmin)
admin.site.register(Applications, ApplicationsAdmin)
admin.site.register(Cargo, CargoAdmin)
