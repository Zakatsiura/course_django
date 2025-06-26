from django.core.management.base import BaseCommand
from hr.models import Employee


class Command(BaseCommand):
    help = 'Activates all employees by setting is_active=True'

    def handle(self, *args, **kwargs):
        employees = Employee.objects.filter(is_active=False)
        count = employees.count()

        employees.update(is_active=True)

        self.stdout.write(
            self.style.SUCCESS(f'Activated {count} employees who were inactive.')
        )
