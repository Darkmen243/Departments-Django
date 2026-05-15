from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Department
from .serializers import DepartmentSerializer, DepartmentTreeSerializer, EmployeeSerializer
from .services import reassign_employees_and_delete


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()

    serializer_class = DepartmentSerializer

    def get_serializer_class(self):

        if self.action == "retrieve":
            return DepartmentTreeSerializer

        if self.action == "employees":
            return EmployeeSerializer

        return DepartmentSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="depth",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Tree depth (max 5)",
                required=False,
                default=1,
            ),
            OpenApiParameter(
                name="include_employees",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Include employees in response",
                required=False,
                default=True,
            ),
        ],
        responses=DepartmentTreeSerializer,
    )
    def retrieve(self, request, *args, **kwargs) -> Response:

        department = self.get_object()
        depth = min(int(request.GET.get("depth", 1)), 5)
        include_employees = (request.GET.get("include_employees", "true").lower() == "true")

        serializer = DepartmentTreeSerializer(
            department,
            context={
                "depth": depth,
                "include_employees":
                    include_employees,
            },
        )

        return Response({
            "department": {
                "id": department.id,
                "name": department.name,
                "created_at": department.created_at,
            },
            "employees":
                serializer.data.get("employees",[]),
            "children": serializer.data.get("children",[]),
        })

    @extend_schema(
        request=EmployeeSerializer,
        responses=EmployeeSerializer,
    )
    @action(detail=True, methods=["post"])
    def employees(self, request, pk: int | None = None) -> Response:
        department = self.get_object()
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(department=department)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="mode",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="cascade or reassign",
            ),
            OpenApiParameter(
                name="reassign_to_department_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Required when mode=reassign",
            ),
        ]
    )
    def destroy(self, request, *args, **kwargs) -> Response:

        department = self.get_object()

        mode = request.query_params.get("mode")

        if mode == "cascade":
            department.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        if mode == "reassign":
            reassign_to_id = request.query_params.get("reassign_to_department_id")

            if not reassign_to_id:
                return Response({"error": "reassign_to_department_id required"}, status=400)

            target_department = (get_object_or_404(Department,pk=reassign_to_id))

            reassign_employees_and_delete(department,target_department)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"error":"Invalid mode"},status=400)
