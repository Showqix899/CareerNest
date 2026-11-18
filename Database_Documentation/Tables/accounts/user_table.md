
# User Model Documentation

## 1. Overview

The `User` model is a custom Django authentication model.

Instead of using Django's default username-based authentication, this model uses email addresses as the login identifier.

It uses:

- `AbstractBaseUser` for core authentication functionality.
- `PermissionsMixin` for Django's permission system.
- `UserManager` for custom user creation methods.
- UUID as the primary key.

---

## 2. Imports

```python
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
import uuid
from django.utils import timezone
```

| Import | Purpose |
|---|---|
| `models` | Provides Django model fields. |
| `AbstractBaseUser` | Provides password and authentication functionality. |
| `PermissionsMixin` | Provides groups and permission support. |
| `BaseUserManager` | Base class for creating a custom manager. |
| `uuid` | Generates unique identifiers. |
| `timezone` | Provides timezone-aware date and time. |

---

## 3. UserManager

A manager is used to perform database-related operations for a model.

We create a custom manager to control how normal users and superusers are created.

### 3.1 create_user()

```python
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extrafield):

        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(email=email, **extrafield)

        user.set_password(password)

        user.save(using=self._db)

        return user
```

**Step-by-step explanation:**

1. `email`: Receives the user's email address.
2. `password`: Receives the user's password.
3. `**extrafield`: Receives additional fields such as full name and phone.
4. `if not email`: Checks whether an email was provided.
5. `normalize_email()`: Normalizes the email domain to lowercase.
6. `self.model()`: Creates a User object in memory.
7. `set_password()`: Hashes the password before saving.
8. `save()`: Saves the user into the database.
9. `return user`: Returns the created user object.

**Example:**

```python
User.objects.create_user(
    email="showqi@example.com",
    password="strongpassword",
    full_name="Mahmud Showqi"
)
```

### 3.2 create_superuser()

```python
def create_superuser(self, email, password=None, **extrafields):

    extrafields.setdefault('is_staff', True)
    extrafields.setdefault('is_superuser', True)

    return self.create_user(
        email,
        password,
        **extrafields
    )
```

This method creates an administrator account.

**Important fields:**

| Field | Meaning |
|---|---|
| `is_staff` | Allows access to the Django admin site, subject to permissions. |
| `is_superuser` | Grants all permissions. |

`setdefault()` assigns a default value only if the key does not already exist.

Finally, it calls `create_user()` to reuse the existing user creation logic.

---

## 4. Custom User Model

```python
class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(unique=True)

    full_name = models.CharField(max_length=150)

    phone = models.CharField(
        max_length=11,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
```

---

## 5. Model Inheritance

```python
class User(AbstractBaseUser, PermissionsMixin):
```

The User model inherits from two Django classes.

### 5.1 AbstractBaseUser

Provides core authentication functionality.

It includes:

- Password field.
- Password hashing.
- `set_password()`.
- `check_password()`.
- `last_login`.

Example:

```python
user.set_password("mypassword")

user.check_password("mypassword")
```

Output:

```text
True
```

### 5.2 PermissionsMixin

Provides Django's authorization functionality.

It includes:

- `is_superuser`
- `groups`
- `user_permissions`
- Permission checking methods.

It allows our custom user model to work with Django's built-in permission system.

---

## 6. Field Documentation

### 6.1 UUID Primary Key

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

| Option | Explanation |
|---|---|
| `UUIDField` | Stores a UUID value. |
| `primary_key=True` | Makes this field the primary key. |
| `default=uuid.uuid4` | Automatically generates a UUID. |
| `editable=False` | Prevents editing through standard forms. |

Example UUID:

```text
b568e08b-4444-471a-a6a3-c6a2ac04d816
```

**Why UUID?**

- Avoids exposing simple sequential IDs.
- Provides globally unique identifiers.
- Useful in distributed applications.

### 6.2 Email

```python
email = models.EmailField(unique=True)
```

- Stores the user's email address.
- `EmailField` provides email format validation.
- `unique=True` prevents duplicate email values.

Email is used as the login identifier.

### 6.3 Full Name

```python
full_name = models.CharField(max_length=150)
```

- Stores the user's full name.
- `CharField` stores short text.
- `max_length=150` limits the length to 150 characters.

### 6.4 Phone

```python
phone = models.CharField(
    max_length=11,
    null=True,
    blank=True
)
```

- Stores the user's phone number.
- `max_length=11` allows up to 11 characters.
- `null=True` allows SQL NULL in the database.
- `blank=True` allows the field to be empty during form validation.

Phone numbers are stored as strings because they are identifiers, not mathematical values.

### 6.5 is_active

```python
is_active = models.BooleanField(default=False)
```

- Indicates whether the account is active.
- Defaults to `False`.
- Useful for email verification and account activation.

Inactive users are normally prevented from authenticating by Django's default authentication backend.

### 6.6 is_staff

```python
is_staff = models.BooleanField(default=False)
```

- Controls access to the Django admin site.
- Defaults to `False`.
- Staff users must also have the necessary permissions to access admin functionality.

### 6.7 date_joined

```python
date_joined = models.DateTimeField(default=timezone.now)
```

- Stores the user's registration date and time.
- `DateTimeField` stores date and time.
- `timezone.now` provides the current timezone-aware datetime.

We use `timezone.now` without parentheses so Django calls it when a new record is created.

---

## 7. Custom Manager Registration

```python
objects = UserManager()
```

This registers our custom manager with the User model.

Now we can call:

```python
User.objects.create_user(...)
```

And:

```python
User.objects.create_superuser(...)
```

---

## 8. USERNAME_FIELD

```python
USERNAME_FIELD = 'email'
```

This tells Django which field should be used as the unique login identifier.

Since we use email authentication, we specify `email` instead of `username`.

**Important:** It must be a string, not a tuple.

Correct:

```python
USERNAME_FIELD = 'email'
```

Incorrect:

```python
USERNAME_FIELD = 'email',
```

---

## 9. REQUIRED_FIELDS

```python
REQUIRED_FIELDS = ['full_name']
```

Defines additional fields Django should ask for when running:

```bash
python manage.py createsuperuser
```

Django will ask for:

- Email
- Full name
- Password

The email does not need to be included in `REQUIRED_FIELDS` because it is already defined in `USERNAME_FIELD`.

---

## 10. __str__() Method

```python
def __str__(self):
    return self.email
```

Returns a readable representation of the User object.

Example:

```python
user = User.objects.get(email="showqi@example.com")

print(user)
```

Output:

```text
showqi@example.com
```

---

## 11. User Creation Workflow

Example:

```python
user = User.objects.create_user(
    email="showqi@example.com",
    password="StrongPassword123",
    full_name="Mahmud Showqi",
    phone="01812345678"
)
```

### Internal workflow

```text
Application calls create_user()
              |
              v
       Validate email
              |
              v
       Normalize email
              |
              v
       Create User object
              |
              v
       Hash the password
              |
              v
       Save to database
              |
              v
       Return User object
```

Because `is_active` defaults to `False`, the account must be activated before normal login if the authentication backend checks this flag.

---

## 12. Example Database Record

| Field | Example |
|---|---|
| id | b568e08b-4444-471a-a6a3-c6a2ac04d816 |
| email | showqi@example.com |
| full_name | Mahmud Showqi |
| phone | 01812345678 |
| password | Django-generated password hash |
| is_active | False |
| is_staff | False |
| is_superuser | False |
| date_joined | Current date and time |
| last_login | NULL |

Some fields, such as `password`, `last_login`, and `is_superuser`, come from the inherited Django classes.

---

## 13. Creating Users and Superusers

### Normal user

```python
User.objects.create_user(
    email="user@example.com",
    password="userpassword",
    full_name="Example User"
)
```

### Superuser

Run this command:

```bash
python manage.py createsuperuser
```

With Docker:

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 14. Important Implementation Notes

1. Keep `USERNAME_FIELD` as a string.
2. Validate `is_staff` and `is_superuser` inside `create_superuser()`.
3. Require a password in `create_user()` if passwordless accounts are not supported.
4. Remember that `normalize_email()` lowercases only the domain portion.
5. Since `is_active=False` by default, implement an account activation process.
6. Run migrations after changing model fields.

### Migration commands

```bash
python manage.py makemigrations
python manage.py migrate
```

With Docker:

```bash
docker compose exec web python manage.py makemigrations

docker compose exec web python manage.py migrate
```

---

## 15. Summary

| Component | Responsibility |
|---|---|
| UserManager | Controls user creation. |
| create_user() | Creates normal users. |
| create_superuser() | Creates administrator accounts. |
| AbstractBaseUser | Provides authentication functionality. |
| PermissionsMixin | Provides permission support. |
| UUIDField | Provides unique primary keys. |
| USERNAME_FIELD | Defines email as the login identifier. |
| REQUIRED_FIELDS | Defines extra superuser prompts. |
| __str__() | Returns email as the readable user representation. |

**In short:** This custom User model replaces Django's default username-based authentication with email-based authentication, UUID identifiers, password hashing, and Django's built-in permission system.
