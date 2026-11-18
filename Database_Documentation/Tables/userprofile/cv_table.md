# `CV` Model Documentation

The `CV` model is used to store and manage curriculum vitae (resume) files uploaded by users in the application.

## Model Overview

- **Model Name:** `CV`
- **Database Table:** `<app_name>_cv`
- **Primary Key:** `UUID` (Universally Unique Identifier)

---

## Fields & Attributes

| Field Name | Data Type | Constraints & Options | Description |
| :--- | :--- | :--- | :--- |
| **`id`** | `UUIDField` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` | A unique, non-editable UUID used as the primary key instead of a standard auto-incrementing integer. |
| **`user`** | `ForeignKey` | `to=User`, `on_delete=models.CASCADE`, `related_name='cvs'` | Links the CV to a specific user account. |
| **`file`** | `FileField` | `upload_to='static/cvs'` | Stores the uploaded CV document inside the `static/cvs` directory. |
| **`title`** | `CharField` | `max_length=150` | A descriptive title or label for the CV (e.g., *"Software Engineer Resume 2026"*). |
| **`created_at`** | `DateTimeField` | `auto_now_add=True` | Automatically records the exact date and time when the CV was first uploaded. |

---

## Relationships

### `User` $\leftrightarrow$ `CV` (One-to-Many)

- **Relationship Type:** **One-to-Many** (`User` has many `CV`s; each `CV` belongs to one `User`).
- **Deletion Behavior (`CASCADE`):** If a `User` record is deleted from the database, all `CV` records associated with that user will automatically be deleted as well.
- **Reverse Access (`related_name='cvs'`):** You can retrieve all CVs belonging to a specific user directly from a `User` instance.

```
+----------------+          1 : N          +----------------+
|      User      | ----------------------> |       CV       |
+----------------+                         +----------------+
| id             |                         | id (UUID)      |
| username       |                         | user_id (FK)   |
| email          |                         | file           |
| ...            |                         | title          |
+----------------+                         | created_at     |
                                           +----------------+
```

---

## Usage Examples

### 1. Creating a New CV
```python
from django.contrib.auth import get_user_model
from .models import CV

User = get_user_model()
user = User.objects.get(username="john_doe")

new_cv = CV.objects.create(
    user=user,
    title="Backend Developer CV",
    file="path/to/resume.pdf"
)
```

### 2. Fetching All CVs for a Specific User
Using the `related_name='cvs'`:
```python
# Get all CVs uploaded by the user
user_cvs = user.cvs.all()

for cv in user_cvs:
    print(f"{cv.title} - Uploaded on {cv.created_at}")
```

### 3. Accessing the Owner from a CV Instance
```python
cv = CV.objects.first()
owner_username = cv.user.username
```