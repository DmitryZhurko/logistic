from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from .filters import diesel, petrol

colors = [
    ('black', 'black'), ('white', 'white'), ('red', 'red'), ('blue', 'blue'), ('green', 'green')]

variant_for_status = [
    'в очереди', 'выполняется'
]

variant_for_status_car = [
    'в рейсе', 'свободна'
]

tupe_fuel = (
    ('дизель', 'дизель'),
    ('бензин', 'бензин'),

)

class Cars(models.Model):
    brand = models.CharField(max_length=50, verbose_name='марка')
    model = models.CharField(max_length=50, verbose_name='модель')
    registration_mark = models.CharField(max_length=50, verbose_name='регистрационный знак')
    color = models.CharField(max_length=50, choices=colors, verbose_name='цвет')
    carrying = models.IntegerField(verbose_name='грузоподъемность в кг')
    free = models.BooleanField(verbose_name='свободен или в рейсе', default=True)
    fuel_consumption = models.FloatField(verbose_name='расход топлива')
    fuel_type = models.CharField(max_length=50, choices=tupe_fuel, verbose_name='тип топлива')

    def __str__(self):
        return f'{self.model}'

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'


class Driver(models.Model):
    name = models.CharField(max_length=40, verbose_name='имя')
    surname = models.CharField(max_length=40, verbose_name='фамилия')
    patronymic = models.CharField(max_length=40, verbose_name='отчество')
    day_of_birth = models.DateField(max_length=8, verbose_name='дата рождения')
    address = models.CharField(max_length=40, verbose_name='адрес')
    photos = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='фото', default='/photos/avatar.jpg')
    car = models.OneToOneField('Cars', verbose_name='водитель', on_delete=models.SET_NULL, blank=True, null=True, related_name='driver')

    @property
    def age(self):
        return (datetime.now().date().year - self.day_of_birth.year)

    def __str__(self):
        return f'{self.surname}'

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'


class Applications(models.Model):
    auto = models.ForeignKey('Cars', on_delete=models.SET_NULL,  blank=True, null=True, verbose_name='машина', related_name='applications')
    cargos = models.ManyToManyField('Cargo',  verbose_name='груз')
    date_added = models.DateTimeField(auto_now=True, verbose_name='дата принятия заявки')
    execution = models.CharField(max_length=50, verbose_name='статус')
    executed = models.BooleanField(verbose_name='заявка доставлена либо нет', default=False)

    @property
    def cost(self):
        fuel = self.auto.fuel_type
        if fuel == 'бензин':
            fuel = petrol
        else:
            fuel = diesel
        result_weight = 0
        for i in self.cargos.all():
            result_weight += i.weight
        cost_distance = (self.cargos.first().distance / self.auto.fuel_consumption) * fuel
        cost_weight = result_weight * 0.04
        return cost_distance + cost_weight

    @property
    def fuel_cost(self):
        fuel = self.auto.fuel_type
        if fuel == petrol:
            fuel = 2
        else:
            fuel = diesel
        cost_distance = (self.cargos.first().distance / self.auto.fuel_consumption) * fuel
        return cost_distance

    def __str__(self):
        return f'{self.auto.free}{self.cargos.name}'

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class Cargo(models.Model):
    name = models.CharField(max_length=50, verbose_name='имя')
    distance = models.IntegerField(verbose_name='расстояние, км')
    route = models.CharField(max_length=200, verbose_name='маршрут')
    weight = models.IntegerField(verbose_name='вес в кг')
    free = models.BooleanField(verbose_name='свободен или в рейсе', default=True)
    executed = models.BooleanField(verbose_name='груз доставлен', default=False)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Груз'
        verbose_name_plural = 'Грузы'