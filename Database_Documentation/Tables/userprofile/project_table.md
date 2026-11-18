
# Project Description and Project Media Models Documentation

## 1. Overview

These two models manage users' projects and their associated media files.

There are two models:

1. `ProjectDescription` – Stores project information such as title and description.
2. `ProjectMedia` – Stores media files (images and videos) associated with a project.

A user can create multiple projects, and each project can contain multiple media files.

---

# 2. ProjectDescription Model

## Model Code

```python
class ProjectDescription(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title
```

## 2.1 Field Explanation

### 1. id

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

- `UUIDField`: Stores a universally unique identifier.
- `primary_key=True`: Makes this field the primary key.
- `default=uuid.uuid4`: Automatically generates a UUID for every project.
- `editable=False`: Prevents editing through standard model forms.

Example UUID:

```text
b568e08b-4444-471a-a6a3-c6a2ac04d816
```

### 2. user

```python
user = models.ForeignKey(
    User,
    on_delete=models.CASCADE
)
```

This field establishes a relationship between the `ProjectDescription` model and the `User` model.

**Relationship: Many-to-One (User to ProjectDescription).**

- One user can create multiple projects.
- Each project belongs to exactly one user.
- `ForeignKey` creates a relationship using the primary key of the referenced User table.
- Django creates a database column named `user_id` to store the referenced user's ID.

#### What does `on_delete=models.CASCADE` mean?

If a user is deleted, all projects belonging to that user will also be deleted.

Example:

```text
User A
  |
  |------ Project 1
  |
  |------ Project 2
  |
  |------ Project 3
```

If User A is deleted, Project 1, Project 2, and Project 3 are also deleted.

### 3. title

```python
title = models.CharField(
    max_length=100,
    null=True,
    blank=True
)
```

- Stores the project title.
- `CharField` is used for short text.
- `max_length=100` allows up to 100 characters.
- `null=True` allows the database to store NULL.
- `blank=True` makes the field optional during form validation.

Example:

```text
CareerNest - Job Portal
```

### 4. description

```python
description = models.TextField(
    null=True,
    blank=True
)
```

- Stores detailed information about the project.
- `TextField` is suitable for longer text.
- `null=True` allows NULL values in the database.
- `blank=True` makes the field optional in forms.

Example:

```text
CareerNest is a job portal developed using Django.
It helps users find jobs and manage their professional profiles.
```

## 2.2 String Representation

```python
def __str__(self):
    return self.title
```

Returns the project title when the object is displayed.

Example:

```python
project = ProjectDescription.objects.get(id=project_id)

print(project)
```

Output:

```text
CareerNest - Job Portal
```

**Note:** Since `title` is optional, a safer implementation is:

```python
def __str__(self):
    return self.title or "Untitled Project"
```

---

# 3. ProjectMedia Model

## Model Code

```python
class ProjectMedia(models.Model):

    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    project = models.ForeignKey(
        ProjectDescription,
        on_delete=models.CASCADE,
        related_name='proj_des'
    )

    file = models.FileField(
        upload_to='static/project_media/'
    )

    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.media_type} for {self.project.title}"
```

## 3.1 Field Explanation

### 1. MediaType

```python
class MediaType(models.TextChoices):
    IMAGE = 'image', 'Image'
    VIDEO = 'video', 'Video'
```

This is an inner class that defines the available media types.

Django's `TextChoices` provides predefined choices for a model field.

Each choice contains two values:

```python
IMAGE = 'image', 'Image'
```

- `'image'`: Actual value stored in the database.
- `'Image'`: Human-readable label displayed in forms and admin.

Available choices:

| Stored Value | Display Label |
|---|---|
| `image` | Image |
| `video` | Video |

This prevents arbitrary media type values from being selected through Django's model forms.

### 2. id

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

- Uses UUID as the primary key.
- Automatically generates a unique ID.
- Cannot be edited through standard model forms.

### 3. project

```python
project = models.ForeignKey(
    ProjectDescription,
    on_delete=models.CASCADE,
    related_name='proj_des'
)
```

This field establishes a relationship between `ProjectMedia` and `ProjectDescription`.

**Relationship: Many-to-One (ProjectDescription to ProjectMedia).**

- One project can contain multiple media files.
- Each media file belongs to exactly one project.
- `ForeignKey` stores the referenced project's ID in the media table.
- Django creates a database column named `project_id`.

#### What does related_name='proj_des' mean?

`related_name` defines the reverse relationship name.

It allows us to access all media files belonging to a project directly from the project object.

Example:

```python
project = ProjectDescription.objects.get(id=project_id)

media_files = project.proj_des.all()
```

Here:

- `project.proj_des` accesses the related media manager.
- `.all()` retrieves all media records associated with that project.

Without `related_name`, Django would normally provide a reverse accessor named `projectmedia_set`.

#### What does on_delete=models.CASCADE mean?

If a project is deleted, all media records associated with that project will also be deleted from the database.

Example:

```text
Project 1
   |
   |------ Image 1
   |
   |------ Image 2
   |
   |------ Video 1
```

If Project 1 is deleted, its three associated ProjectMedia database records are also deleted.

**Important:** Deleting a database record does not automatically guarantee that the actual uploaded file is deleted from the storage system. File cleanup needs separate handling.

### 4. file

```python
file = models.FileField(
    upload_to='static/project_media/'
)
```

This field stores uploaded file information.

- `FileField` handles uploaded files.
- `upload_to` specifies the directory where uploaded files are stored.
- The database stores the file path, not the entire file content.

Example stored path:

```text
static/project_media/project_image.png
```

The actual file is stored in the configured file storage system.

### 5. media_type

```python
media_type = models.CharField(
    max_length=10,
    choices=MediaType.choices
)
```

- Stores the type of uploaded media.
- `CharField` stores short text.
- `max_length=10` allows the values `image` and `video`.
- `choices` restricts the available options.

Example database values:

```text
image
video
```

### 6. uploaded_at

```python
uploaded_at = models.DateTimeField(
    auto_now_add=True
)
```

- Stores the date and time when the media record is first created.
- `DateTimeField` stores date and time.
- `auto_now_add=True` automatically sets the timestamp during the initial creation.

Unlike `default=timezone.now`, `auto_now_add=True` is specifically intended to record the creation time.

---

## 3.2 String Representation

```python
def __str__(self):
    return f"{self.media_type} for {self.project.title}"
```

Returns a readable description of the media record.

Example:

```python
media = ProjectMedia.objects.first()

print(media)
```

Output:

```text
image for CareerNest - Job Portal
```

---

# 4. Relationship Between the Models

There are two ForeignKey relationships in these models.

## Relationship 1: User and ProjectDescription

```python
user = models.ForeignKey(
    User,
    on_delete=models.CASCADE
)
```

**One-to-Many relationship.**

- One user can have many projects.
- One project belongs to one user.

## Relationship 2: ProjectDescription and ProjectMedia

```python
project = models.ForeignKey(
    ProjectDescription,
    on_delete=models.CASCADE,
    related_name='proj_des'
)
```

**One-to-Many relationship.**

- One project can have many media files.
- One media file belongs to one project.

## Complete Relationship Diagram

```text
              USER TABLE
                  |
                  | 1
                  |
                  | Many
                  |
         PROJECT DESCRIPTION
                  |
                  | 1
                  |
                  | Many
                  |
             PROJECT MEDIA
```

More specifically:

```text
User
 |
 | 1 : Many
 |
ProjectDescription
 |
 | 1 : Many
 |
ProjectMedia
```

This structure allows a user to create multiple projects, and each project can contain multiple images and videos.

---

# 5. Example Database Structure

## User Table

| id | email |
|---|---|
| UUID-1 | user@example.com |

## ProjectDescription Table

| id | user_id | title |
|---|---|---|
| UUID-P1 | UUID-1 | CareerNest |
| UUID-P2 | UUID-1 | E-commerce Website |

Notice that `user_id` references the `id` of the User table.

## ProjectMedia Table

| id | project_id | file | media_type |
|---|---|---|---|
| UUID-M1 | UUID-P1 | career.png | image |
| UUID-M2 | UUID-P1 | dashboard.png | image |
| UUID-M3 | UUID-P1 | demo.mp4 | video |
| UUID-M4 | UUID-P2 | shop.png | image |

Notice that `project_id` references the `id` of the ProjectDescription table.

---

# 6. Accessing Related Objects

## Get all projects belonging to a user

```python
user = User.objects.get(email="user@example.com")

projects = ProjectDescription.objects.filter(user=user)
```

## Get the user who owns a project

```python
project = ProjectDescription.objects.get(id=project_id)

user = project.user
```

## Get all media belonging to a project

```python
project = ProjectDescription.objects.get(id=project_id)

media = project.proj_des.all()
```

## Get the project associated with a media file

```python
media = ProjectMedia.objects.get(id=media_id)

project = media.project
```

## Get the owner of a media file

```python
media = ProjectMedia.objects.get(id=media_id)

owner = media.project.user
```

---

# 7. Summary

| Model | Purpose |
|---|---|
| `ProjectDescription` | Stores project title, description, and owner. |
| `ProjectMedia` | Stores uploaded project images and videos. |

| Relationship | Type |
|---|---|
| User → ProjectDescription | One-to-Many |
| ProjectDescription → ProjectMedia | One-to-Many |

**In short:** A user can create multiple projects, and each project can contain multiple media files. ForeignKey relationships connect the tables, while `CASCADE` ensures dependent database records are deleted when their parent record is deleted.
