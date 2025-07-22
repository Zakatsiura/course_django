from django.db.models.signals import pre_save
from django.dispatch import receiver
from hr.models import Department, Position
from hr.constants import MINIMUM_SALARY
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Department)
def capitalize_department_name(sender, instance, **kwargs):
    if instance.name:
        instance.name = instance.name.capitalize()


@receiver(pre_save, sender=Position)
def ensure_minimum_wage(sender, instance, **kwargs):
    if instance.monthly_rate < MINIMUM_SALARY:
        old_rate = instance.monthly_rate
        instance.monthly_rate = MINIMUM_SALARY
        logger.info(
            f"Заробітна плата для позиції '{instance.title}' була збільшена з {old_rate} до мінімального порогу {MINIMUM_SALARY}."
        )
