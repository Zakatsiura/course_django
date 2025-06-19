import calendar
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ChoiceField

from common.enums import WorkDayEnum
from hr.models import Employee

WorkDayChoices = [(tag.value, tag.value) for tag in WorkDayEnum]


class SalaryForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    def __init__(self, *args, **kwargs):
        super(SalaryForm, self).__init__(*args, **kwargs)

        self.today = date.today()
        _, self.num_days = calendar.monthrange(self.today.year, self.today.month)

        for day in range(1, self.num_days + 1):
            weekday = calendar.weekday(self.today.year, self.today.month, day)
            weekday_name = calendar.day_name[weekday]
            field_name = f'day_{day}'

            if weekday >= 5:
                self.fields[field_name] = ChoiceField(
                    label=f'{day} - {weekday_name}',
                    choices=[(WorkDayEnum.WEEKEND.value, WorkDayEnum.WEEKEND.value)],
                    initial=WorkDayEnum.WEEKEND.value,
                )
            else:
                self.fields[field_name] = ChoiceField(
                    label=f'{day} - {weekday_name}',
                    choices=WorkDayChoices,
                    initial=WorkDayEnum.WORKING_DAY.value,
                )

    def clean_employee(self):
        employee = self.cleaned_data.get('employee')
        if not employee:
            raise ValidationError("Поле 'Робітник' обов’язкове для заповнення.")
        return employee

    def clean(self):
        cleaned_data = super().clean()
        sick_days = 0
        holiday_days = 0

        for day in range(1, self.num_days + 1):
            field_name = f'day_{day}'
            value = cleaned_data.get(field_name)

            if value == WorkDayEnum.SICK_DAY.value:
                sick_days += 1
            elif value == WorkDayEnum.HOLIDAY.value:
                holiday_days += 1

        if sick_days > 5:
            raise ValidationError(f"Кількість лікарняних днів ({sick_days}) не може перевищувати 5.")

        if holiday_days > 3:
            raise ValidationError(f"Кількість днів відпочинку ({holiday_days}) не може перевищувати 3.")

        return cleaned_data


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('username', 'first_name', 'last_name', 'email', 'position')
