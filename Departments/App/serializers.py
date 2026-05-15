from rest_framework import serializers
from .models import Department, Employee
from .services import validate_no_cycle


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee

        fields = (
            "id",
            "full_name",
            "position",
            "hired_at",
            "created_at",
        )

        read_only_fields = ("id", "created_at")

    def validate_full_name(self, value: str) -> str:

        value = value.strip()

        if not value:
            raise serializers.ValidationError("Full name cannot be empty")

        return value

    def validate_position(self, value: str) -> str:

        value = value.strip()

        if not value:
            raise serializers.ValidationError("Position cannot be empty")

        return value


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department

        fields = (
            "id",
            "name",
            "parent",
            "created_at",
        )

        read_only_fields = ("id", "created_at")

    def validate_name(self, value: str) -> str:

        value = value.strip()

        if not value:
            raise serializers.ValidationError("Name cannot be empty")

        return value

    def validate(self, attrs):

        department = self.instance

        if department:
            new_parent = attrs.get("parent", department.parent)

            validate_no_cycle(department, new_parent)

        return attrs


class DepartmentTreeSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    children = serializers.SerializerMethodField()

    class Meta:
        model = Department

        fields = (
            "id",
            "name",
            "created_at",
            "employees",
            "children",
        )

    def get_employees(self, obj: Department):

        include_employees = self.context.get("include_employees", True)

        if not include_employees:
            return []

        employees = obj.employees.all().order_by("full_name")

        return EmployeeSerializer(employees, many=True).data

    def get_children(self, obj: Department):

        depth = self.context.get("depth", 1)

        if depth <= 0:
            return []

        serializer = DepartmentTreeSerializer(
            obj.children.all(),
            many=True,
            context={
                "depth": depth - 1,
                "include_employees":
                    self.context.get(
                        "include_employees",
                        True,
                    ),
            },
        )

        return serializer.data
