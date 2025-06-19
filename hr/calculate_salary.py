from abc import ABC, abstractmethod
from math import ceil

from common.enums import WorkDayEnum
from hr.models import Employee


class AbstractSalaryCalculate(ABC):
    sick_days_multiplier = 0.6
    day_prefix = 'day_'

    def __init__(self, employee: Employee):
        self.employee = employee

    @abstractmethod
    def calculate_salary(self, days_dict: dict[str, str]):
        raise NotImplementedError()


class CalculateMonthRateSalary(AbstractSalaryCalculate):
    def __init__(self, employee: Employee):
        super().__init__(employee=employee)
        self._daily_salary = 0

    @staticmethod
    def _calculate_base_work_days(days_dict: dict[str, str]) -> int:
        return len(
            {
                day for day, work_type in days_dict.items()
                if work_type not in (WorkDayEnum.HOLIDAY.value, WorkDayEnum.WEEKEND.value)
            }
        )

    def _calculate_daily_salary(self, base_working_days: int) -> int:
        if base_working_days == 0 or not self.employee.position:
            return 0
        return ceil(self.employee.position.monthly_rate / base_working_days)

    @staticmethod
    def _calculate_monthly_working_days(days_dict: dict[str, str]) -> int:
        return len(
            {
                day for day, work_type in days_dict.items()
                if work_type == WorkDayEnum.WORKING_DAY.value
            }
        )

    @staticmethod
    def _calculate_monthly_sick_days(days_dict: dict[str, str]) -> int:
        return len(
            {
                day for day, work_type in days_dict.items()
                if work_type == WorkDayEnum.SICK_DAY.value
            }
        )

    def _calculate_sick_daily_salary(self) -> int:
        return ceil(self._daily_salary * self.sick_days_multiplier)

    def _calculate_sick_monthly_salary(self, days_dict: dict[str, str]) -> int:
        sick_days = self._calculate_monthly_sick_days(days_dict=days_dict)
        return self._calculate_sick_daily_salary() * sick_days

    def _calculate_working_monthly_salary(self, days_dict: dict[str, str]) -> int:
        working_days = self._calculate_monthly_working_days(days_dict=days_dict)
        return working_days * self._daily_salary

    def calculate_salary(self, days_dict: dict[str, str]) -> int:
        base_working_days = self._calculate_base_work_days(days_dict)

        self._daily_salary = self._calculate_daily_salary(base_working_days=base_working_days)

        working_days_salary = self._calculate_working_monthly_salary(days_dict=days_dict)
        sick_monthly_salary = self._calculate_sick_monthly_salary(days_dict=days_dict)

        salary = working_days_salary + sick_monthly_salary

        return min(salary, self.employee.position.monthly_rate if self.employee.position else 0)
