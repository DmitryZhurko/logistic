from django import forms
from django.core.exceptions import ValidationError
from .models import Driver, Cars, Applications, Cargo


class DriversForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'surname', 'age', 'car']


class CarsForm(forms.ModelForm):
    class Meta:
        model = Cars
        fields = ['brand', 'model', 'registration_mark', 'color', 'carrying', 'fuel_consumption']


class ApplicationsForm(forms.ModelForm):
    auto = forms.ModelChoiceField(queryset=Cars.objects.all())
    cargos = forms.ModelMultipleChoiceField(queryset=Cargo.objects.filter(executed=False))

    def clean_cargos(self):
        auto = self.cleaned_data.get('auto')
        cargos = self.cleaned_data.get('cargos')
        summa = 0
        for i in cargos:
            print(i.name)
            summa += i.weight
        if auto == None:
            print('авто равно нан')
            return cargos
        else:
            if summa > auto.carrying:
                print('грузоподъямность превышает')
                raise ValidationError('Грузоподъемность превышена')
            if len(cargos) == 1:
                print('груз 1')
                return cargos
            else:
                if cargos[0].route != cargos[1].route:
                    print('грузы имеют разный маршрут')
                    raise ValidationError('Грузы должны иметь одинаковый маршрут')

                else:
                    print('возврат груза')
                    return cargos

    class Meta:
        model = Applications
        fields = ['auto', 'cargos']


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['name', 'distance', 'route', 'weight']


class FulfilledApplicationsForm(forms.Form):
    number = forms.IntegerField()


class YearForm(forms.Form):
    data = forms.CharField()


class MonthForm(forms.Form):
    choice_month = (
        ('01', 'Январь'),
        ('02', 'Февраль'),
        ('03', 'Март'),
        ('04', 'Апрель'),
        ('05', 'Май'),
        ('06', 'Июнь'),
        ('07', 'Июль'),
        ('08', 'Август'),
        ('09', 'Сентябрь'),
        ('10', 'Октябрь'),
        ('11', 'Ноябрь'),
        ('12', 'Декабрь'),
    )
    data = forms.ChoiceField(widget=forms.Select, choices=choice_month, required=True)