from django.conf.urls.static import static
from django.urls import path

from logistic import settings
from .views import drivers, edit_drivers, cars, edit_cars, del_drivers, applications, add_applications,\
    add_cargo, add_drivers, del_cars, add_cars, cargo, edit_cargo, del_cargo, edit_applications, del_applications,\
    add_applicationsForm, free_car_report, busy_cars, cargo_in_auto, queue_of_applications_free, queue_of_applications_busy\
    ,reports_year, reports_month, report_for_all_months, cargo_free, cargo_busy, cargo_delivered, applications_delivered,\
    login, logout, drivers_detail

urlpatterns = [
    path('add_cargo', add_cargo, name='add_cargo'),
    path('', login, name='login'),
    path('logout', logout, name='logout'),
    path('drivers', drivers, name='drivers'),
    path('drivers_detail<int:drivers_pk>', drivers_detail, name='drivers_detail'),
    path('edit_drivers/<int:edit_pk>', edit_drivers, name='edit_drivers'),
    path('del_drivers/<int:del_drivers_pk>', del_drivers, name='del_drivers'),
    path('edit_cars/<int:cars_edit_pk>', edit_cars, name='edit_cars'),
    path('cars', cars, name='cars'),
    path('add_cars', add_cars, name='add_cars'),
    path('del_cars/<int:del_cars_pk>', del_cars, name='del_cars'),
    path('applications', applications, name='applications'),
    path('add_applications', add_applications, name='add_applications'),
    path('edit_applications/<int:edit_applications_pk>', edit_applications, name='edit_applications'),
    path('del_applications/<int:del_applications_pk>', del_applications, name='del_applications'),
    path('add_drivers', add_drivers, name='add_drivers'),
    path('cargo', cargo, name='cargo'),
    path('edit_cargo/<int:edit_cargo_pk>', edit_cargo, name='edit_cargo'),
    path('del_cargo/<int:del_cargo_pk>', del_cargo, name='del_cargo'),
    path('add_applicationsForm>', add_applicationsForm, name='add_applicationsForm'),
    path('free_car_report', free_car_report, name='free_car_report'),
    path('busy_cars', busy_cars, name='busy_cars'),
    path('cargo_in_auto/<int:pk_auto>', cargo_in_auto, name='cargo_in_auto'),
    path('queue_of_applications_free', queue_of_applications_free, name='queue_of_applications_free'),
    path('queue_of_applications_busy', queue_of_applications_busy, name='queue_of_applications_busy'),
    path('applications_delivered', applications_delivered, name='applications_delivered'),
    path('reports_year', reports_year, name='reports_year'),
    path('reports_month', reports_month, name='reports_month'),
    path('report_for_all_months', report_for_all_months, name='report_for_all_months'),
    path('cargo_free', cargo_free, name='cargo_free'),
    path('cargo_busy', cargo_busy, name='cargo_busy'),
    path('cargo_delivered', cargo_delivered, name='cargo_delivered'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)