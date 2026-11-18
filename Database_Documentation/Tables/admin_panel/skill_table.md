
# Skill Model Documentation

## 1. Overview

The `Skill` model stores skills that users can add to their profiles, such as Python, Django, JavaScript, React, and PostgreSQL.

## 2. Model Code

```python
class Skill(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name
```

## 3. Field Explanation

| Field | Description |
|---|---|
| `id` | UUID primary key that uniquely identifies each skill. |
| `name` | Stores the skill name, with a maximum length of 100 characters. |
| `unique=True` | Prevents duplicate skill names in the database. |

### UUIDField

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

- `primary_key=True`: Makes this field the primary key.
- `default=uuid.uuid4`: Automatically generates a UUID.
- `editable=False`: Prevents editing through standard forms.

### CharField

```python
name = models.CharField(max_length=100, unique=True)
```

- `max_length=100`: Allows up to 100 characters.
- `unique=True`: Ensures each skill name is unique.

## 4. String Representation

```python
def __str__(self):
    return self.name
```

Returns the skill name when the object is displayed.

Example:

```python
skill = Skill.objects.create(name="Python")
print(skill)
```

Output:

```text
Python
```

## 5. Example Database Records

| id | name |
|---|---|
| UUID-1 | Python |
| UUID-2 | Django |
| UUID-3 | JavaScript |
| UUID-4 | React |
| UUID-5 | PostgreSQL |

## 6. Summary

The `Skill` model manages unique skill names using UUID primary keys. It can be connected to user profiles through a ManyToManyField, allowing users to have multiple skills and each skill to belong to multiple users.
