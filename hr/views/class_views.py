from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.views import View

from hr.forms import EmployeeForm
from hr.models import Employee

from django.shortcuts import render

from hr.forms import SalaryForm
from hr.calculate_salary import CalculateMonthRateSalary
from common.enums import WorkDayEnum


def user_is_superadmin(user) -> bool:
    return user.is_superuser


class EmployeeListView(View):
    def get(self, request):
        search = request.GET.get("search", "")
        employees = Employee.objects.all()

        if search:
            employees = employees.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(position__title__icontains=search),
            )

        context = {"employees": employees}
        return render(request, "employee_list.html", context)


class EmployeeCreateView(UserPassesTestMixin, View):
    def get(self, request):
        form = EmployeeForm()
        return render(request, "employee_form.html", {"form": form})

    def post(self, request):
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("employee_list"))
        return render(request, "employee_form.html", {"form": form})

    def test_func(self):
        return user_is_superadmin(self.request.user)


class EmployeeUpdateView(UserPassesTestMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        form = EmployeeForm(instance=employee)
        return render(request, "employee_form.html", {"form": form})

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect(reverse("employee_list"))
        return render(request, "employee_form.html", {"form": form})

    def test_func(self):
        return user_is_superadmin(self.request.user)


class EmployeeDeleteView(UserPassesTestMixin, View):
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        return render(request, "employee_confirm_delete.html", {"object": employee})

    def post(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return redirect(reverse("employee_list"))

    def test_func(self):
        return user_is_superadmin(self.request.user)


class SalaryCalculatorView(View):
    template_name = "salary_calculator.html"

    def get(self, request):
        form = SalaryForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SalaryForm(request.POST)
        calculated_salary = None
        detailed_salary = None

        if form.is_valid():
            employee = form.cleaned_data['employee']
            days_dict = {
                key: form.cleaned_data[key]
                for key in form.cleaned_data
                if key.startswith('day_')
            }

            calculator = CalculateMonthRateSalary(employee)
            calculated_salary = calculator.calculate_salary(days_dict)

            detailed_salary = {}
            for day_key, work_type in days_dict.items():
                daily_salary = 0
                if work_type == WorkDayEnum.WORKING_DAY.value:
                    daily_salary = calculator._daily_salary
                elif work_type == WorkDayEnum.SICK_DAY.value:
                    daily_salary = calculator._calculate_sick_daily_salary()
                detailed_salary[day_key] = {
                    "status": work_type,
                    "salary": daily_salary,
                }

        context = {
            "form": form,
            "calculated_salary": calculated_salary,
            "detailed_salary": detailed_salary,
        }
        return render(request, self.template_name, context)
