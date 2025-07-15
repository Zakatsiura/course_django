from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.core.cache import cache, caches
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    tax_code = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)

    def __str__(self):
        return self.name

    @cached_property
    def position_count(self):
        return self.position_set.filter(is_active=True).count()

    def save(self, *args, **kwargs):
        if not self.pk and Company.objects.exists():
            raise ValidationError("There can be only one Company instance")
        return super(Company, self).save(*args, **kwargs)


class Department(models.Model):
    name = models.CharField(max_length=200)
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Position(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    job_description = models.CharField(verbose_name=_("Job Description"), max_length=500, default="")
    monthly_rate = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.is_manager:
            existing_manager = (
                Position.objects.filter(
                    department=self.department,
                    is_manager=True,
                )
                .exclude(id=self.id)
                .exists()
            )
            if existing_manager:
                raise ValidationError(
                    f"Manager already exists in the {self.department.name} department.",
                )
        super(Position, self).save(*args, **kwargs)
        cache.delete('total_position_count')  # очищення кешу при зміні

    def delete(self, *args, **kwargs):
        super(Position, self).delete(*args, **kwargs)
        cache.delete('total_position_count')  # очищення кешу при видаленні

    def __str__(self):
        return self.title

    @cached_property
    def total_positions(self):
        key = 'total_position_count'
        total = cache.get(key)
        if total is None:
            total = Position.objects.count()
            cache.set(key, total, 300)  # кеш на 5 хвилин
        return total


class Employee(AbstractUser):
    hire_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    position = models.ForeignKey(
        "Position",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=151, default="")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True, help_text='PDF, DOC, or DOCX')

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.position or ""}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        print(caches['my_key']._cache.keys())
        print(cache._cache.keys())

        caches['my_key'].clear()
        print(caches['my_key']._cache.keys())
        # On Redis
        # cache.delete_pattern("pattern_*")

        cache.delete(f'employee_{self.id}')

    def delete(self, *args, **kwargs):
        cache.delete(f'employee_{self.pk}')
        super().delete(*args, **kwargs)


class MonthlySalary(models.Model):
    month_year = models.DateField()
    salary = models.IntegerField()
    bonus = models.IntegerField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField()