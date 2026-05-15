# Departments API

## Stack

- Django
- Django REST Framework
- PostgreSQL
- Docker
- Docker Compose

---

# Run project

```bash
docker-compose up --build
```

---

# Apply migrations

```bash
docker-compose exec web python manage.py migrate
```

---

# Create superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

---

# API docs

http://localhost:8000/docs/

---

# Endpoints

## Create department
```bash
POST /api/departments/
```
## Create employee
```bash
POST /api/departments/{id}/employees/
```
## Get department tree
```bash
GET /api/departments/{id}/?depth=3
```
## Update department
```bash
PATCH /api/departments/{id}/
```
## Delete department
```bash
DELETE /api/departments/{id}/?mode=cascade

DELETE /api/departments/{id}/?mode=reassign&reassign_to_department_id=2
```
