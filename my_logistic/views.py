from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from .models import Driver, Cars, Applications, Cargo, variant_for_status, variant_for_status_car
from .forms import DriversForm, CarsForm, ApplicationsForm, CargoForm, FulfilledApplicationsForm, YearForm, MonthForm
from django.contrib import auth


#Вывод всех водителей
def drivers(request):
    driver_list = Driver.objects.all()
    return render(request, 'my_logistic/drivers.html', {'driver_list': driver_list})


def drivers_detail(request, drivers_pk):
    driver_list = Driver.objects.get(pk=drivers_pk)
    return render(request, 'my_logistic/drivers_detail.html', {'driver_list': driver_list})


def del_drivers(request, del_drivers_pk):
    driver = Driver.objects.get(pk=del_drivers_pk)
    driver.delete()
    return redirect('drivers')


def edit_drivers(request, edit_pk):
    var = request.GET.get('param')
    driver_list = Driver.objects.get(pk=edit_pk)
    if request.method == 'POST':
        form = DriversForm(request.POST, request.FILES, instance=driver_list)
        if form.is_valid():
            form.save()
            return redirect('drivers_detail', drivers_pk=edit_pk)
    else:
        form = DriversForm(instance=driver_list)
    return render(request, 'my_logistic/drivers_detail.html', {'driver_list': driver_list, 'form': form, 'var': var})


def add_drivers(request):
    error = ''
    var = request.GET.get('param')
    driver_list = Driver.objects.all()
    if request.method == 'POST':
        form = DriversForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('drivers')
        else:
            error = 'Данная машина закреплена за другим водителем'
    else:
        form = DriversForm()
    return render(request, 'my_logistic/drivers_detail.html', {'form': form, 'var': var, 'driver_list': driver_list, 'error': error })

#вывод всех машин
def cars(request):
    cars_list = Cars.objects.all()
    return render(request, 'my_logistic/cars.html', {'cars_list': cars_list})


def edit_cars(request, cars_edit_pk):
    var = request.GET.get('param')
    cars_list = Cars.objects.all()
    edit_list = Cars.objects.get(pk=cars_edit_pk)
    if request.method == 'POST':
        form = CarsForm(request.POST, instance=edit_list)
        if form.is_valid():
            form.save()
            return redirect('cars')
    else:
        form = CarsForm(instance=edit_list)
    return render(request, 'my_logistic/cars.html', {'cars_list': cars_list, 'form': form, 'var': var})


def del_cars(request, del_cars_pk):
    apps = Applications.objects.filter(auto__pk=del_cars_pk)
    for app in apps:
        for cargo in app.cargos.all():
            cargo.free = True
            cargo.save()
        app.delete()
    Cars.objects.get(pk=del_cars_pk).delete()
    return redirect('cars')


def add_cars(request):
    #получение параметра из шаблона
    var = request.GET.get('param')
    cars_list = Cars.objects.all()
    if request.method == 'POST':
        form = CarsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cars')
    else:
        form = CarsForm()
    return render(request, 'my_logistic/cars.html', {'form': form, 'var': var, 'cars_list': cars_list})


#вывод всех заявок кроме executed=True
def applications(request):
    applications_list = Applications.objects.exclude(executed=True)
    return render(request, 'my_logistic/applications.html', {'applications_list': applications_list})


def add_applications(request):
    var = request.GET.get('param')
    applications_list = Applications.objects.exclude(executed=True)
    if request.method == 'POST':
        form = ApplicationsForm(request.POST)
        if form.is_valid():
            #получение очищенных данных
            auto = form.cleaned_data['auto']
            cargos = form.cleaned_data['cargos']
            #создание новое объекта заявок и добавление тода автомобиля
            application = Applications.objects.create(auto=auto)
            if auto.free == False:
                application.execution = variant_for_status[0]
                application.save()
            else:
                application.execution = variant_for_status[1]
                application.save()
                auto.free = False
                auto.save()
            #берем поочередно все грузы и если груз уже в статусе False, то мы получаем заявку с этим грузом и если
            # в этой заявке только 1 наш груз то мы удаляем эту заявку
            for cargo in cargos:
                if cargo.free == False:
                    carg = Applications.objects.get(cargos=cargo.pk)
                    if (carg.cargos.all()).count() == 1:
                        carg.delete()
                    else:
                        carg.cargos.remove(Cargo.objects.get(pk=cargo.pk))
                    application.cargos.add(cargo)
                else:
                    cargo.free = False
                    cargo.save()
                    application.cargos.add(cargo)
            for car in Cars.objects.all():
                if Applications.objects.filter(auto=car.pk).count() == 1:
                    status_app = Applications.objects.get(auto=car.pk)
                    status_app.execution = variant_for_status[1]
                    status_app.save()
                elif Applications.objects.filter(auto=car.pk).count() == 0:
                    car.free = True
                    car.save()
            return redirect('applications')
    else:
        form = ApplicationsForm()
    return render(request, 'my_logistic/applications.html', {'form': form, 'var': var, 'applications_list': applications_list})


def edit_applications(request, edit_applications_pk):
    var = request.GET.get('param')
    applications_list = Applications.objects.exclude(executed=True)
    edit_applications = Applications.objects.get(pk=edit_applications_pk)
    previous_car = Applications.objects.get(pk=edit_applications_pk)
    if request.method == 'POST':
        form = ApplicationsForm(request.POST, instance=edit_applications)
        if form.is_valid():
            auto = form.cleaned_data['auto']
            cargos = form.cleaned_data['cargos']
            if auto.free == True:
                edit_applications.execution = variant_for_status[1]
                edit_applications.save()
                auto.free = False
                auto.save()
            else:
                if previous_car.auto.pk == auto.pk:
                    edit_applications.execution = variant_for_status[1]
                    edit_applications.save()
                else:
                    edit_applications.execution = variant_for_status[0]
                    edit_applications.save()
            if previous_car.auto.pk != auto.pk:
                car = Cars.objects.get(pk=previous_car.auto.pk)
                if (Applications.objects.filter(auto=previous_car.auto.pk)).count() == 0:
                    car.free = True
                    car.save()
                else:
                    car.free = False
                    car.save()
            for old_cargo in previous_car.cargos.all():
                if old_cargo not in cargos:
                    if Applications.objects.filter(pk=old_cargo.pk).count() == 0:
                        old_cargo_status = Cargo.objects.get(pk=old_cargo.pk)
                        old_cargo_status.free = True
                        old_cargo_status.save()
            for car in Cars.objects.all():
                if Applications.objects.filter(auto=car.pk).count() == 1:
                    status_app = Applications.objects.get(auto=car.pk)
                    status_app.execution = variant_for_status[1]
                    status_app.save()
                elif Applications.objects.filter(auto=car.pk).count() == 0:
                    car.free = True
                    car.save()
            for cargo in cargos:
                if cargo.free == False:
                    carg = Applications.objects.get(cargos=cargo.pk)
                    if (carg.cargos.all()).count() == 1:
                        carg.delete()
                    else:
                        carg.cargos.remove(Cargo.objects.get(pk=cargo.pk))
                else:
                    cargo.free = False
                    cargo.save()
            form.save()
            return redirect('applications')
    else:
        form = ApplicationsForm(instance=edit_applications)
    return render(request, 'my_logistic/applications.html', {'form': form, 'var': var, 'applications_list': applications_list})

#добавление формы для отметки заявки как исполненной
def add_applicationsForm(request):
    var = request.GET.get('param')
    applications_list = Applications.objects.exclude(executed=True)
    if request.method == 'POST':
        form = FulfilledApplicationsForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data['number']
            app = Applications.objects.get(pk=number)
            app.executed = True
            app.save()
            for cargo in app.cargos.all():
                cargo.executed = True
                cargo.save()
            if Applications.objects.filter(executed=False, auto=app.auto).count() == 0:
                car = Cars.objects.get(pk=app.auto.pk)
                car.free = True
                car.save()
            else:
                status = Applications.objects.filter(executed=False, auto=app.auto).first()
                status.execution = variant_for_status[1]
                status.save()
            return redirect('applications')
    else:
        form = FulfilledApplicationsForm()
    return render(request, 'my_logistic/applications.html', {'form': form, 'var': var, 'applications_list': applications_list})


def del_applications(request, del_applications_pk):
    app = Applications.objects.get(pk=del_applications_pk)
    car_app = Applications.objects.filter(auto__pk=app.auto.pk, executed=False).order_by('pk')
    if car_app.count() == 1:
        car = Cars.objects.get(pk=app.auto.pk)
        car.free = True
        car.save()
    else:
        if car_app[0].pk == app.pk:
            car_app[1].execution = variant_for_status[1]
            car_app[1].save()
    for cargo in app.cargos.all():
        cargo.free = True
        cargo.save()
    app.delete()
    return redirect('applications')


def cargo(request):
    title = 'Грузы'
    cargo_list = Cargo.objects.all()
    return render(request, 'my_logistic/cargo.html', {'cargo_list': cargo_list, 'title': title})


def cargo_free(request):
    title = 'Недоставленные грузы'
    cargo_list = Cargo.objects.filter(free=True)
    return render(request, 'my_logistic/cargo.html', {'cargo_list': cargo_list, 'title': title})


def cargo_busy(request):
    title = 'Исполняемые грузы'
    cargo_list = Cargo.objects.filter(free=False, executed=False)
    return render(request, 'my_logistic/cargo.html', {'cargo_list': cargo_list, 'title': title})


def cargo_delivered(request):
    title = 'Доставленные грузы'
    cargo_list = Cargo.objects.filter(executed=True)
    return render(request, 'my_logistic/cargo.html', {'cargo_list': cargo_list, 'title': title})


def add_cargo(request):
    var = request.GET.get('param')
    cargo_list = Cargo.objects.all()
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cargo')
    else:
        form = CargoForm()
    return render(request, 'my_logistic/cargo.html', {'form': form, 'var': var, 'cargo_list': cargo_list})


def edit_cargo(request, edit_cargo_pk):
    var = request.GET.get('param')
    edit_cargo = Cargo.objects.get(pk=edit_cargo_pk)
    cargo_list = Cargo.objects.all()
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=edit_cargo)
        if form.is_valid():
            form.save()
            return redirect('cargo')
    else:
        form = CargoForm(instance=edit_cargo)
    return render(request, 'my_logistic/cargo.html', {'form': form, 'var': var, 'cargo_list': cargo_list})


def del_cargo(request, del_cargo_pk):
    application = Applications.objects.filter(cargos__pk=del_cargo_pk).first()
    #если заявка из которой собираемся удалять груз существует
    if application != None:
        #если груз был единственным то делаем авто свободным и удаляем заявку
        if application.cargos.all().count() == 1:
            car = application.auto
            car.free = True
            car.save()
            application.delete()
        #если грузов несколько то очищаем тот который будем удалять
        elif application.cargos.all().count() > 1:
            application.cargos.remove(Cargo.objects.get(pk=del_cargo_pk))
    Cargo.objects.get(pk=del_cargo_pk).delete()
    return redirect('cargo')


#Свободные автомобили
def free_car_report(request):
    title = 'Свободные автомобили'
    cars = Cars.objects.filter(free=True)
    return render(request, 'my_logistic/report_cars.html', {'cars': cars, 'title': title})


#Занятые автомобили
def busy_cars(request):
    title = 'Занятые автомобили'
    cars = Cars.objects.filter(free=False)
    return render(request, 'my_logistic/report_cars.html', {'cars': cars, 'title': title})


def cargo_in_auto(request, pk_auto):
    cargo_list = []
    title = 'Перевозимые грузы'
    apps = Applications.objects.filter(auto__pk=pk_auto)
    for app in apps:
        for j in app.cargos.filter(executed=False):
            cargo_list.append(j)
    return render(request, 'my_logistic/cargo.html', {'cargo_list': cargo_list, 'title': title})


def queue_of_applications_free(request):
    title = 'Заявки в очереди'
    apps = Applications.objects.filter(execution=variant_for_status[0], executed=False).order_by('auto', 'date_added')
    return render(request, 'my_logistic/report_applications.html', {'apps': apps, 'title': title})


def queue_of_applications_busy(request):
    title = 'Заявки выполняющиеся'
    apps = Applications.objects.filter(execution=variant_for_status[1], executed=False).order_by('auto', 'date_added')
    return render(request, 'my_logistic/report_applications.html', {'apps': apps, 'title': title})


def applications_delivered(request):
    title = 'Исполненные заявки'
    apps = Applications.objects.filter(executed=True)
    return render(request, 'my_logistic/report_applications.html', {'apps': apps, 'title': title})


def reports_year(request):
    ask = ''
    if request.method == 'POST':
        form = YearForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['data']
            request.session['year'] = data
            apps = Applications.objects.filter(date_added__year=data, executed=True)
            amount_cargo = 0
            profit = 0
            fuel_price = 0
            for app in apps:
                profit += app.cost
                fuel_price += app.fuel_cost
                for cargo in app.cargos.all():
                    amount_cargo += 1
            ask = f'Отчет за {data} год'
            count = apps.count()
            net_profit = profit - fuel_price
            return render(request, 'my_logistic/reports.html', {'ask': ask, 'count': count, 'amount_cargo': amount_cargo,
            'profit': profit, 'fuel_price': fuel_price, 'net_profit': net_profit})
    else:
        ask = 'Введите год'
        form = YearForm()
    return render(request, 'my_logistic/reports_form.html', {'form': form, 'ask': ask})


def reports_month(request):
    if request.method == 'POST':
        form = MonthForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['data']
            year = request.session['year']
            apps = Applications.objects.filter(date_added__year=year).filter(date_added__month=month, executed=True)
            amount_cargo = 0
            profit = 0
            fuel_price = 0
            for app in apps:
                profit += app.cost
                fuel_price += app.fuel_cost
                for cargo in app.cargos.all():
                    amount_cargo += 1
            ask = f'Отчет за {month} {year} года'
            count = apps.count()
            net_profit = profit - fuel_price
            return render(request, 'my_logistic/reports.html',
                          {'ask': ask, 'count': count, 'amount_cargo': amount_cargo,
                           'profit': profit, 'fuel_price': fuel_price, 'net_profit': net_profit})
    else:
        form = MonthForm()
    return render(request, 'my_logistic/reports_form.html', {'form': form})


def report_for_all_months(request):
    var = request.GET.get('param')
    report = {}
    year = request.session['year']
    for i in range(1, 13):
        apps = Applications.objects.filter(date_added__year=year).filter(date_added__month=str(i), executed=True)
        amount_cargo = 0
        profit = 0
        fuel_price = 0
        for app in apps:
            profit += int(app.cost)
            fuel_price += int(app.fuel_cost)
            for cargo in app.cargos.all():
                amount_cargo += 1
        count = apps.count()
        net_profit = int(profit - fuel_price)
        report[i] = [count, amount_cargo, profit, fuel_price, net_profit]
    return render(request, 'my_logistic/reports_for_month.html',
                          {'report': report, 'year': year, 'var': var})


def login(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user != None:
            auth.login(request, user)
            return redirect('applications')
        else:
            args['login_error'] = 'Логин либо пароль неверны'
            return render(request, 'my_logistic/login.html', {'args': args})
    else:
        return render(request, 'my_logistic/login.html')


def logout(request):
    auth.logout(request)
    return redirect('login')