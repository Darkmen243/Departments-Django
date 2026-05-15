from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Department, Employee


def validate_no_cycle(department: Department, new_parent: Department | None) -> None:
    if not new_parent:
        return

    if department.id == new_parent.id:
        raise ValidationError("Department cannot be a parent of itself")

    current = new_parent
    while current:
        if current.id == department.id:
            raise ValidationError("Cycle detected")
        current = current.parent


def validate_reassign(department: Department, target_department: Department) -> None:
    if department.id == target_department.id:
        raise ValidationError("Cannot reassign employees to same department")

    current = target_department
    while current:
        if current.id == department.id:
            raise ValidationError("Cannot reassign employees into deleting subtree")

        current = current.parent


@transaction.atomic
def reassign_employees_and_delete(department: Department,target_department: Department) -> None:
    validate_reassign(department,target_department)
    Employee.objects.filter(department=department).update(department=target_department)
    department.delete()
