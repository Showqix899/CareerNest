
# UserProfile Model Documentation

## 1. Overview

The `UserProfile` model stores additional information about a user.

The main `User` model handles authentication details, such as email and password, while `UserProfile` stores professional and personal information.

It includes:

- Profile picture
- Address
- City
- Skills
- Experience
- Creation and update timestamps

The model has relationships with three other models:

1. `User` – One-to-One relationship.
2. `City` – one to one.
3. `Skill` – Many-to-Many relationship.

---

## 2. Model Code

```python
class UserProfile(models.Model):

    id = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profiles"
    )

    profile_pic = models.FileField(
        upload_to='static/profile_pic',
        null=True,
        blank=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='cities'
    )

    Skills = models.ManyToManyField(
        Skill,
        related_name="skills"
    )

    experiance = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s profile"
```

---

## 3. Field Explanation

### 3.1 id

```python
id = models.UUIDField(
    unique=True,
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

- `UUIDField`: Stores a universally unique identifier.
- `unique=True`: Ensures the value is unique.
- `primary_key=True`: Makes it the primary key.
- `default=uuid.uuid4`: Automatically generates a UUID.
- `editable=False`: Prevents editing through standard forms.

Example:

```text
b568e08b-4444-471a-a6a3-c6a2ac04d816
```

Note: `primary_key=True` already implies uniqueness, so `unique=True` is redundant.

### 3.2 user

```python
user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="profiles"
)
```

This establishes a One-to-One relationship between `UserProfile` and `User`.

**Relationship: One-to-One**

- One user can have only one profile.
- One profile belongs to exactly one user.
- Django creates a `user_id` column in the UserProfile table.
- `user_id` references the primary key of the User table.

#### What does OneToOneField mean?

Unlike a ForeignKey, which allows multiple records to reference the same user, OneToOneField enforces uniqueness.

Example:

```text
USER TABLE
    |
    | 1
    |
    | 1
    |
USER PROFILE TABLE
```

A user cannot have multiple UserProfile records through this relationship.

#### What does related_name="profiles" mean?

It defines the reverse relationship name.

We can access a user's profile using:

```python
user = User.objects.get(email="user@example.com")

profile = user.profiles
```

Instead of using Django's default reverse accessor.

#### What does on_delete=models.CASCADE mean?

If a user is deleted, their associated profile is also deleted.

---

### 3.3 profile_pic

```python
profile_pic = models.FileField(
    upload_to='static/profile_pic',
    null=True,
    blank=True
)
```

Stores the user's profile picture.

- `FileField`: Handles uploaded files.
- `upload_to`: Specifies the upload directory.
- `null=True`: Allows NULL in the database.
- `blank=True`: Makes the field optional in forms.

Example uploaded file:

```text
static/profile_pic/profile.png
```

The database stores the file path, not the actual file content.

### 3.4 address

```python
address = models.TextField(
    null=True,
    blank=True
)
```

Stores the user's address.

- `TextField`: Stores longer text.
- `null=True`: Allows NULL in the database.
- `blank=True`: Allows an empty value in forms.

Example:

```text
Agrabad, Chittagong, Bangladesh
```

### 3.5 city

```python
city = models.ForeignKey(
    City,
    on_delete=models.CASCADE,
    related_name='cities'
)
```

Establishes a ForeignKey relationship between `UserProfile` and `City`.

**Relationship: Many-to-One (City to UserProfile).**

- One city can have multiple user profiles.
- Each user profile belongs to one city.
- Django creates a `city_id` column in the UserProfile table.
- `city_id` references the primary key of the City table.

#### Relationship example

```text
CITY TABLE
    |
    | 1
    |
    | Many
    |
USER PROFILE TABLE
```

Example:

```text
Chittagong
    |
    |------ User Profile 1
    |
    |------ User Profile 2
    |
    |------ User Profile 3

Dhaka
    |
    |------ User Profile 4
    |
    |------ User Profile 5
```

Multiple users can belong to the same city.

#### What does related_name='cities' mean?

It defines the reverse relationship name.

We can access all profiles belonging to a city:

```python
city = City.objects.get(name="Chittagong")

profiles = city.cities.all()
```

Here:

- `city.cities` accesses the related UserProfile manager.
- `.all()` retrieves all profiles associated with that city.

#### What does on_delete=models.CASCADE mean?

If a city is deleted, all UserProfile records associated with that city will also be deleted.

**Important:** If you want to preserve user profiles when deleting a city, consider using `SET_NULL` with `null=True` instead.

---

### 3.6 Skills

```python
Skills = models.ManyToManyField(
    Skill,
    related_name="skills"
)
```

Establishes a Many-to-Many relationship between `UserProfile` and `Skill`.

**Relationship: Many-to-Many**

- One user profile can have multiple skills.
- One skill can belong to multiple user profiles.
- Django automatically creates an intermediate/junction table.
- The intermediate table stores the IDs of the related UserProfile and Skill records.

#### Why ManyToManyField?

Suppose a user has three skills:

```text
User Profile 1
    |
    |------ Python
    |
    |------ Django
    |
    |------ PostgreSQL
```

Another user can also have Python and Django.

```text
Python
   |
   |------ User Profile 1
   |
   |------ User Profile 2
   |
   |------ User Profile 3
```

This is why ManyToManyField is appropriate.

#### How does the intermediate table work?

Django automatically creates a junction table similar to this:

**UserProfile_Skills**

| id | userprofile_id | skill_id |
|---|---|---|
| 1 | Profile-1 | Skill-1 |
| 2 | Profile-1 | Skill-2 |
| 3 | Profile-1 | Skill-3 |
| 4 | Profile-2 | Skill-1 |

The table connects profiles with their skills.

You do not need to create this intermediate table manually.

#### What does related_name="skills" mean?

It defines the reverse relationship name on the Skill model.

Example:

```python
skill = Skill.objects.get(name="Python")

profiles = skill.skills.all()
```

This retrieves all user profiles that have Python as a skill.

#### Adding skills to a profile

```python
profile = UserProfile.objects.get(user=user)

python = Skill.objects.get(name="Python")
django = Skill.objects.get(name="Django")

profile.Skills.add(python, django)
```

#### Getting all skills of a profile

```python
profile = UserProfile.objects.get(user=user)

skills = profile.Skills.all()
```

#### Removing a skill

```python
profile.Skills.remove(python)
```

#### Removing all skills

```python
profile.Skills.clear()
```

**Important:** Removing a skill from a profile deletes the relationship from the intermediate table. It does not delete the actual Skill record.

---

### 3.7 experiance

```python
experiance = models.TextField(
    null=True,
    blank=True
)
```

Stores the user's professional experience.

- `TextField`: Supports longer text.
- `null=True`: Allows NULL in the database.
- `blank=True`: Makes the field optional in forms.

Example:

```text
2 years of experience in Python and Django development.
Worked on REST APIs and PostgreSQL databases.
```

### 3.8 created_at

```python
created_at = models.DateTimeField(auto_now_add=True)
```

- Stores the profile creation date and time.
- `auto_now_add=True` automatically sets the timestamp when the profile is first created.
- It does not automatically change during later updates.

### 3.9 updated_at

```python
updated_at = models.DateTimeField(auto_now=True)
```

- Stores the latest update date and time.
- `auto_now=True` updates the timestamp whenever the model is saved.

---

## 4. Complete Relationship Explanation

The UserProfile model has three important relationships.

### Relationship 1: User and UserProfile

```python
user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="profiles"
)
```

**One-to-One**

- One user has one profile.
- One profile belongs to one user.

### Relationship 2: City and UserProfile

```python
city = models.ForeignKey(
    City,
    on_delete=models.CASCADE,
    related_name='cities'
)
```

**One-to-Many**

- One city can have many profiles.
- One profile belongs to one city.

### Relationship 3: Skill and UserProfile

```python
Skills = models.ManyToManyField(
    Skill,
    related_name="skills"
)
```

**Many-to-Many**

- One profile can have many skills.
- One skill can belong to many profiles.
- Django creates an intermediate table automatically.

---

## 5. Complete Relationship Diagram

```text
                  USER
                    |
                    | 1 : 1
                    |
               USER PROFILE
                    |
          __________|__________
          |                   |
          |                   |
       ForeignKey         ManyToMany
          |                   |
          |                   |
         CITY               SKILL
          |                   |
          |                   |
     One City has        One Skill can
     many profiles       belong to many
                         profiles
```

Another representation:

```text
USER (1)
   |
   | OneToOne
   |
USER PROFILE
   |
   | ForeignKey
   |
CITY (1)

USER PROFILE
   |
   | ManyToMany
   |
SKILL
```

---

## 6. Example Database Structure

### User Table

| id | email |
|---|---|
| UUID-1 | user1@example.com |
| UUID-2 | user2@example.com |

### City Table

| id | name |
|---|---|
| CITY-1 | Chittagong |
| CITY-2 | Dhaka |

### Skill Table

| id | name |
|---|---|
| SKILL-1 | Python |
| SKILL-2 | Django |
| SKILL-3 | React |

### UserProfile Table

| id | user_id | city_id | address |
|---|---|---|---|
| PROFILE-1 | UUID-1 | CITY-1 | Agrabad |
| PROFILE-2 | UUID-2 | CITY-2 | Mirpur |

### UserProfile_Skills (Intermediate Table)

| userprofile_id | skill_id |
|---|---|
| PROFILE-1 | SKILL-1 |
| PROFILE-1 | SKILL-2 |
| PROFILE-2 | SKILL-1 |
| PROFILE-2 | SKILL-3 |

This structure allows both users to have Python while maintaining separate profile records.

---

## 7. Accessing Related Data

### Get a user's profile

```python
user = User.objects.get(email="user1@example.com")

profile = user.profiles
```

### Get the city of a profile

```python
profile = UserProfile.objects.get(user=user)

city = profile.city
```

### Get all profiles in a city

```python
city = City.objects.get(name="Chittagong")

profiles = city.cities.all()
```

### Get all skills of a profile

```python
profile = UserProfile.objects.get(user=user)

skills = profile.Skills.all()
```

### Get all profiles with a particular skill

```python
skill = Skill.objects.get(name="Python")

profiles = skill.skills.all()
```

### Get the user from a profile

```python
profile = UserProfile.objects.get(id=profile_id)

user = profile.user
```

---

## 8. Important Implementation Notes

1. `OneToOneField` ensures one profile per user.
2. `ForeignKey` allows multiple profiles to belong to the same city.
3. `ManyToManyField` allows multiple skills per profile and multiple profiles per skill.
4. Django automatically creates the intermediate table for ManyToManyField.
5. `related_name` defines how to access related objects in reverse.
6. `CASCADE` deletes dependent database records when the referenced record is deleted.
7. Consider using `MEDIA_ROOT` and `MEDIA_URL` for uploaded profile pictures instead of storing user uploads inside the static files directory.
8. Consider renaming `Skills` to `skills` and `experiance` to `experience` to follow Python naming conventions.

---

## 9. Summary

| Field | Relationship / Type | Purpose |
|---|---|---|
| `id` | UUIDField | Unique profile identifier. |
| `user` | OneToOneField | Connects one profile to one user. |
| `profile_pic` | FileField | Stores the profile picture path. |
| `address` | TextField | Stores the user's address. |
| `city` | ForeignKey | Connects a profile to a city. |
| `Skills` | ManyToManyField | Connects profiles with multiple skills. |
| `experiance` | TextField | Stores professional experience. |
| `created_at` | DateTimeField | Records profile creation time. |
| `updated_at` | DateTimeField | Records the latest profile update time. |

**In short:** UserProfile extends the main User model with profile information. It uses OneToOneField to connect a user to one profile, ForeignKey to connect many profiles to one city, and ManyToManyField to connect multiple profiles with multiple skills.

# UserProfile Model Documentation

## 1. Overview

The `UserProfile` model stores additional information about a user.

The main `User` model handles authentication details, such as email and password, while `UserProfile` stores professional and personal information.

It includes:

- Profile picture
- Address
- City
- Skills
- Experience
- Creation and update timestamps

The model has relationships with three other models:

1. `User` – One-to-One relationship.
2. `City` – Many-to-One relationship (ForeignKey).
3. `Skill` – Many-to-Many relationship.

---

## 2. Model Code

```python
class UserProfile(models.Model):

    id = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profiles"
    )

    profile_pic = models.FileField(
        upload_to='static/profile_pic',
        null=True,
        blank=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='cities'
    )

    Skills = models.ManyToManyField(
        Skill,
        related_name="skills"
    )

    experiance = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s profile"
```

---

## 3. Field Explanation

### 3.1 id

```python
id = models.UUIDField(
    unique=True,
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

- `UUIDField`: Stores a universally unique identifier.
- `unique=True`: Ensures the value is unique.
- `primary_key=True`: Makes it the primary key.
- `default=uuid.uuid4`: Automatically generates a UUID.
- `editable=False`: Prevents editing through standard forms.

Example:

```text
b568e08b-4444-471a-a6a3-c6a2ac04d816
```

Note: `primary_key=True` already implies uniqueness, so `unique=True` is redundant.

### 3.2 user

```python
user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="profiles"
)
```

This establishes a One-to-One relationship between `UserProfile` and `User`.

**Relationship: One-to-One**

- One user can have only one profile.
- One profile belongs to exactly one user.
- Django creates a `user_id` column in the UserProfile table.
- `user_id` references the primary key of the User table.

#### What does OneToOneField mean?

Unlike a ForeignKey, which allows multiple records to reference the same user, OneToOneField enforces uniqueness.

Example:

```text
USER TABLE
    |
    | 1
    |
    | 1
    |
USER PROFILE TABLE
```

A user cannot have multiple UserProfile records through this relationship.

#### What does related_name="profiles" mean?

It defines the reverse relationship name.

We can access a user's profile using:

```python
user = User.objects.get(email="user@example.com")

profile = user.profiles
```

Instead of using Django's default reverse accessor.

#### What does on_delete=models.CASCADE mean?

If a user is deleted, their associated profile is also deleted.

---

### 3.3 profile_pic

```python
profile_pic = models.FileField(
    upload_to='static/profile_pic',
    null=True,
    blank=True
)
```

Stores the user's profile picture.

- `FileField`: Handles uploaded files.
- `upload_to`: Specifies the upload directory.
- `null=True`: Allows NULL in the database.
- `blank=True`: Makes the field optional in forms.

Example uploaded file:

```text
static/profile_pic/profile.png
```

The database stores the file path, not the actual file content.

### 3.4 address

```python
address = models.TextField(
    null=True,
    blank=True
)
```

Stores the user's address.

- `TextField`: Stores longer text.
- `null=True`: Allows NULL in the database.
- `blank=True`: Allows an empty value in forms.

Example:

```text
Agrabad, Chittagong, Bangladesh
```

### 3.5 city

```python
city = models.ForeignKey(
    City,
    on_delete=models.CASCADE,
    related_name='cities'
)
```

Establishes a ForeignKey relationship between `UserProfile` and `City`.

**Relationship: Many-to-One (City to UserProfile).**

- One city can have multiple user profiles.
- Each user profile belongs to one city.
- Django creates a `city_id` column in the UserProfile table.
- `city_id` references the primary key of the City table.

#### Relationship example

```text
CITY TABLE
    |
    | 1
    |
    | Many
    |
USER PROFILE TABLE
```

Example:

```text
Chittagong
    |
    |------ User Profile 1
    |
    |------ User Profile 2
    |
    |------ User Profile 3

Dhaka
    |
    |------ User Profile 4
    |
    |------ User Profile 5
```

Multiple users can belong to the same city.

#### What does related_name='cities' mean?

It defines the reverse relationship name.

We can access all profiles belonging to a city:

```python
city = City.objects.get(name="Chittagong")

profiles = city.cities.all()
```

Here:

- `city.cities` accesses the related UserProfile manager.
- `.all()` retrieves all profiles associated with that city.

#### What does on_delete=models.CASCADE mean?

If a city is deleted, all UserProfile records associated with that city will also be deleted.

**Important:** If you want to preserve user profiles when deleting a city, consider using `SET_NULL` with `null=True` instead.

---

### 3.6 Skills

```python
Skills = models.ManyToManyField(
    Skill,
    related_name="skills"
)
```

Establishes a Many-to-Many relationship between `UserProfile` and `Skill`.

**Relationship: Many-to-Many**

- One user profile can have multiple skills.
- One skill can belong to multiple user profiles.
- Django automatically creates an intermediate/junction table.
- The intermediate table stores the IDs of the related UserProfile and Skill records.

#### Why ManyToManyField?

Suppose a user has three skills:

```text
User Profile 1
    |
    |------ Python
    |
    |------ Django
    |
    |------ PostgreSQL
```

Another user can also have Python and Django.

```text
Python
   |
   |------ User Profile 1
   |
   |------ User Profile 2
   |
   |------ User Profile 3
```

This is why ManyToManyField is appropriate.

#### How does the intermediate table work?

Django automatically creates a junction table similar to this:

**UserProfile_Skills**

| id | userprofile_id | skill_id |
|---|---|---|
| 1 | Profile-1 | Skill-1 |
| 2 | Profile-1 | Skill-2 |
| 3 | Profile-1 | Skill-3 |
| 4 | Profile-2 | Skill-1 |

The table connects profiles with their skills.

You do not need to create this intermediate table manually.

#### What does related_name="skills" mean?

It defines the reverse relationship name on the Skill model.

Example:

```python
skill = Skill.objects.get(name="Python")

profiles = skill.skills.all()
```

This retrieves all user profiles that have Python as a skill.

#### Adding skills to a profile

```python
profile = UserProfile.objects.get(user=user)

python = Skill.objects.get(name="Python")
django = Skill.objects.get(name="Django")

profile.Skills.add(python, django)
```

#### Getting all skills of a profile

```python
profile = UserProfile.objects.get(user=user)

skills = profile.Skills.all()
```

#### Removing a skill

```python
profile.Skills.remove(python)
```

#### Removing all skills

```python
profile.Skills.clear()
```

**Important:** Removing a skill from a profile deletes the relationship from the intermediate table. It does not delete the actual Skill record.

---

### 3.7 experiance

```python
experiance = models.TextField(
    null=True,
    blank=True
)
```

Stores the user's professional experience.

- `TextField`: Supports longer text.
- `null=True`: Allows NULL in the database.
- `blank=True`: Makes the field optional in forms.

Example:

```text
2 years of experience in Python and Django development.
Worked on REST APIs and PostgreSQL databases.
```

### 3.8 created_at

```python
created_at = models.DateTimeField(auto_now_add=True)
```

- Stores the profile creation date and time.
- `auto_now_add=True` automatically sets the timestamp when the profile is first created.
- It does not automatically change during later updates.

### 3.9 updated_at

```python
updated_at = models.DateTimeField(auto_now=True)
```

- Stores the latest update date and time.
- `auto_now=True` updates the timestamp whenever the model is saved.

---

## 4. Complete Relationship Explanation

The UserProfile model has three important relationships.

### Relationship 1: User and UserProfile

```python
user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="profiles"
)
```

**One-to-One**

- One user has one profile.
- One profile belongs to one user.

### Relationship 2: City and UserProfile

```python
city = models.ForeignKey(
    City,
    on_delete=models.CASCADE,
    related_name='cities'
)
```

**One-to-Many**

- One city can have many profiles.
- One profile belongs to one city.

### Relationship 3: Skill and UserProfile

```python
Skills = models.ManyToManyField(
    Skill,
    related_name="skills"
)
```

**Many-to-Many**

- One profile can have many skills.
- One skill can belong to many profiles.
- Django creates an intermediate table automatically.

---

## 5. Complete Relationship Diagram

```text
                  USER
                    |
                    | 1 : 1
                    |
               USER PROFILE
                    |
          __________|__________
          |                   |
          |                   |
       ForeignKey         ManyToMany
          |                   |
          |                   |
         CITY               SKILL
          |                   |
          |                   |
     One City has        One Skill can
     many profiles       belong to many
                         profiles
```

Another representation:

```text
USER (1)
   |
   | OneToOne
   |
USER PROFILE
   |
   | ForeignKey
   |
CITY (1)

USER PROFILE
   |
   | ManyToMany
   |
SKILL
```

---

## 6. Example Database Structure

### User Table

| id | email |
|---|---|
| UUID-1 | user1@example.com |
| UUID-2 | user2@example.com |

### City Table

| id | name |
|---|---|
| CITY-1 | Chittagong |
| CITY-2 | Dhaka |

### Skill Table

| id | name |
|---|---|
| SKILL-1 | Python |
| SKILL-2 | Django |
| SKILL-3 | React |

### UserProfile Table

| id | user_id | city_id | address |
|---|---|---|---|
| PROFILE-1 | UUID-1 | CITY-1 | Agrabad |
| PROFILE-2 | UUID-2 | CITY-2 | Mirpur |

### UserProfile_Skills (Intermediate Table)

| userprofile_id | skill_id |
|---|---|
| PROFILE-1 | SKILL-1 |
| PROFILE-1 | SKILL-2 |
| PROFILE-2 | SKILL-1 |
| PROFILE-2 | SKILL-3 |

This structure allows both users to have Python while maintaining separate profile records.

---

## 7. Accessing Related Data

### Get a user's profile

```python
user = User.objects.get(email="user1@example.com")

profile = user.profiles
```

### Get the city of a profile

```python
profile = UserProfile.objects.get(user=user)

city = profile.city
```

### Get all profiles in a city

```python
city = City.objects.get(name="Chittagong")

profiles = city.cities.all()
```

### Get all skills of a profile

```python
profile = UserProfile.objects.get(user=user)

skills = profile.Skills.all()
```

### Get all profiles with a particular skill

```python
skill = Skill.objects.get(name="Python")

profiles = skill.skills.all()
```

### Get the user from a profile

```python
profile = UserProfile.objects.get(id=profile_id)

user = profile.user
```

---

## 8. Important Implementation Notes

1. `OneToOneField` ensures one profile per user.
2. `ForeignKey` allows multiple profiles to belong to the same city.
3. `ManyToManyField` allows multiple skills per profile and multiple profiles per skill.
4. Django automatically creates the intermediate table for ManyToManyField.
5. `related_name` defines how to access related objects in reverse.
6. `CASCADE` deletes dependent database records when the referenced record is deleted.
7. Consider using `MEDIA_ROOT` and `MEDIA_URL` for uploaded profile pictures instead of storing user uploads inside the static files directory.
8. Consider renaming `Skills` to `skills` and `experiance` to `experience` to follow Python naming conventions.

---

## 9. Summary

| Field | Relationship / Type | Purpose |
|---|---|---|
| `id` | UUIDField | Unique profile identifier. |
| `user` | OneToOneField | Connects one profile to one user. |
| `profile_pic` | FileField | Stores the profile picture path. |
| `address` | TextField | Stores the user's address. |
| `city` | ForeignKey | Connects a profile to a city. |
| `Skills` | ManyToManyField | Connects profiles with multiple skills. |
| `experiance` | TextField | Stores professional experience. |
| `created_at` | DateTimeField | Records profile creation time. |
| `updated_at` | DateTimeField | Records the latest profile update time. |

**In short:** UserProfile extends the main User model with profile information. It uses OneToOneField to connect a user to one profile, ForeignKey to connect many profiles to one city, and ManyToManyField to connect multiple profiles with multiple skills.
