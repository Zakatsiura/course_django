from django.contrib import admin
from django.core.exceptions import ValidationError
from modeltranslation.admin import TranslationAdmin

from hr.models import (
    Department,
    Employee,
    Position,
)

from django.contrib import admin
from django.utils.safestring import mark_safe
from hr.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ['logo']
    readonly_fields = ['name', 'email', 'tax_code', 'logo_preview']

    list_display = ('name', 'email', 'tax_code', 'logo_preview')

    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="max-height: 100px;" />')
        return "No logo"
    logo_preview.short_description = "Logo"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_department')


@admin.register(Position)
class PositionAdmin(TranslationAdmin):
    list_display = ('id', 'title', 'department', 'is_manager')

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except ValidationError as e:
            form.add_error(None, e)
            super().save_model(request, obj, form, change)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('username', 'position', 'hire_date')
