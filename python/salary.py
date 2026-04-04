from datetime import datetime
import pytest


class Salary:
    def __init__(self):
        self.staff = {}
        self.salaries_per_hour = {}
        self.clock_in_timestamp = {}
        self.clock_out_timestamp = {}

    def add_staff(self, name: str, salary_per_hour: float) -> None:
        if not isinstance(name, str) or not isinstance(salary_per_hour, float):
            raise ValueError(
                f"Name must be a string and salary_per_hour must be a float, got {name} and {salary_per_hour}"
            )
        self.staff[name] = name
        self.salaries_per_hour[name] = salary_per_hour
        self.clock_in_timestamp[name] = None
        self.clock_out_timestamp[name] = None

    def clock_in(self, name: str, timestamp: datetime) -> None:
        if name not in self.staff:
            raise ValueError(f"Staff {name} not found")
        self.clock_in_timestamp[name] = datetime.strptime(
            timestamp, "%Y-%m-%d %H:%M:%S"
        )

    def clock_out(self, name: str, timestamp: datetime) -> None:
        if name not in self.staff:
            raise ValueError(f"Staff {name} not found")
        self.clock_out_timestamp[name] = datetime.strptime(
            timestamp, "%Y-%m-%d %H:%M:%S"
        )

    def get_salary(self, name: str) -> float:
        if name not in self.staff:
            return ValueError(f"Staff {name} not found")
        time_worked = self.clock_out_timestamp[name] - self.clock_in_timestamp[name]
        return self.salaries_per_hour[name] * (time_worked.total_seconds() / 3600)


if __name__ == "__main__":
    salary = Salary()
    salary.add_staff("John", 10)
    salary.clock_in("John", "2026-03-24 10:00:00")
    salary.clock_out("John", "2026-03-24 18:00:00")
    print(salary.get_salary("John"))


def test_raise_add_staff_incorrect_args():
    salary = Salary()
    with pytest.raises(ValueError):
        salary.add_staff(10, "Amir")


def test_raise_type_error_for_clock_in():
    salary = Salary()
    salary.add_staff("Amir", 10.0)

    assert salary.clock_in("Amir", "2026-03-24 10:00:00") == None


def test_raise_type_error_for_clock_out():
    salary = Salary()
    salary.add_staff("Amir", 10.0)  # 10.0 not 10
    with pytest.raises(ValueError, match="Staff Unknown not found"):
        salary.clock_in("Unknown", "2026-03-24 18:00:00")
