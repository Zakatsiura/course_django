from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from hr.calculate_salary import CalculateMonthRateSalary
from hr.models import (
    Employee,
    Position,
)
from hr.pagination import SmallSetPagination
from hr.permissions import IsNotRussianEmail, HasPositionPermission
from hr.pydantic_models import WorkingDays
from hr.serializers import (
    EmployeeSerializer,
    PositionSerializer,
    SalarySerializer,
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Provide CRUD viewset for Employee.
    """
    queryset = Employee.objects.all().order_by()
    serializer_class = EmployeeSerializer
    pagination_class = SmallSetPagination
    permission_classes = [IsNotRussianEmail, HasPositionPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(position__title__icontains=search) |
                Q(email__icontains=search),
            )
        return queryset

    @action(detail=True, methods=['get'])
    def position_count(self, request, pk=None):
        employee = self.get_object()
        count = Employee.objects.filter(position=employee.position).count()
        return Response({'position_count': count})


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class SalaryCalculatorView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = SalarySerializer(data=request.data)
        if serializer.is_valid():
            calculator = CalculateMonthRateSalary(employee=serializer.validated_data['employee'])
            month_days = WorkingDays(
                working=serializer.validated_data['working_days'],
                sick=serializer.validated_data['sick_days'],
                holiday=serializer.validated_data['holiday_days'],
                vacation=serializer.validated_data['vacation_days'],
            )

            salary = calculator.calculate_salary(month_days=month_days)
            return Response({'salary': salary})

        return Response(serializer.errors, status=400)
