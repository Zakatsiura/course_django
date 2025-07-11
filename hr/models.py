from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    address = models.CharField(max_length=200, verbose_name=_('Address'))
    email = models.EmailField(verbose_name=_('Email'))
    tax_code = models.CharField(max_length=200, verbose_name=_('Tax Code'))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and Company.objects.exists():
            raise ValidationError(_('There can be only one Company instance'))
        return super(Company, self).save(*args, **kwargs)


class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Parent Department'),
    )

    def __str__(self):
        return self.name


class Position(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    department = models.ForeignKey('Department', on_delete=models.CASCADE, verbose_name=_('Department'))
    is_manager = models.BooleanField(default=False, verbose_name=_('Is Manager'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    job_description = models.CharField(max_length=500, default='', verbose_name=_('Job Description'))
    monthly_rate = models.IntegerField(default=0, verbose_name=_('Monthly Rate'))

    def save(self, *args, **kwargs):
        if self.is_manager:
            existing_manager = (
                Position.objects.filter(department=self.department, is_manager=True)
                .exclude(id=self.id)
                .exists()
            )
            if existing_manager:
                raise ValidationError(
                    _('Manager already exists in the %(department)s department.') % {
                        'department': self.department.name
                    }
                )
        super(Position, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Employee(AbstractUser):
    hire_date = models.DateField(null=True, blank=True, verbose_name=_('Hire Date'))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('Birth Date'))
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Position'))
    phone_number = models.CharField(max_length=151, default='', verbose_name=_('Phone Number'))

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.position or ""}'


class MonthlySalary(models.Model):
    month_year = models.DateField(verbose_name=_('Month and Year'))
    salary = models.IntegerField(verbose_name=_('Salary'))
    bonus = models.IntegerField(null=True, blank=True, verbose_name=_('Bonus'))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Employee'))
    paid = models.BooleanField(default=False, verbose_name=_('Paid'))
    paid_date = models.DateField(verbose_name=_('Paid Date'))
