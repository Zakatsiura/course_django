# Create your views here.
from django.shortcuts import render
from django.db.models import Q
from hr.models import Department, Position


def homework_querysets(request):
    context = {
        # Запит 1
        'departments_with_managers': Department.objects.filter(
            position__is_manager=True
        ).order_by('name').distinct(),

        # Запит 2
        'total_active_positions': Position.objects.filter(is_active=True).count(),

        # Запит 3
        'active_or_hr_positions': Position.objects.filter(
            Q(is_active=True) | Q(department__name="HR")
        ).select_related('department'),

        # Запит 4
        'department_names_with_managers': Department.objects.filter(
            position__is_manager=True
        ).values_list('name', flat=True).distinct(),

        # Запит 5
        'positions_titles_and_activity': Position.objects.order_by('title').values('title', 'is_active'),
    }

    return render(request, 'homework_querysets.html', context)
