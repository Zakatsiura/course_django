from modeltranslation.translator import register, TranslationOptions
from hr.models import Department, Position

@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Position)
class PositionTranslationOptions(TranslationOptions):
    fields = ('title', 'job_description')

