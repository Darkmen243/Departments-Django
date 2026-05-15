from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["parent", "name"],name="unique_department_name_per_parent")]

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Employee(models.Model):
    department = models.ForeignKey(Department, related_name="employees", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    hired_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.full_name = self.full_name.strip()
        self.position = self.position.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
