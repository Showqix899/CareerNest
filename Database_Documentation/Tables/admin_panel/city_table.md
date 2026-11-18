
# City Model Documentation

## 1. Overview

The `City` model stores city names that can be associated with user profiles.

## 2. Model Code

```python
class City(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
```

## 3. Field Explanation

| Field | Description |
|---|---|
| `id` | UUID primary key that uniquely identifies each city. |
| `name` | Stores the city name, with a maximum length of 100 characters. |

### UUIDField

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

- `primary_key=True`: Makes this field the primary key.
- `default=uuid.uuid4`: Automatically generates a unique UUID.
- `editable=False`: Prevents editing through standard forms.

### CharField

```python
name = models.CharField(max_length=100)
```

- `max_length=100`: Allows up to 100 characters.
- Stores the city name.

## 4. String Representation

```python
def __str__(self):
    return self.name
```

Returns the city name when the object is displayed.

Example:

```python
city = City.objects.create(name="Chittagong")
print(city)
```

Output:

```text
Chittagong
```

## 5. Example Database Records

| id | name |
|---|---|
| UUID-1 | Chittagong |
| UUID-2 | Dhaka |
| UUID-3 | Cox's Bazar |
| UUID-4 | Sylhet |
| UUID-5 | Rajshahi |

## 6. Summary

The `City` model stores city information using UUID primary keys. It can be connected to the `UserProfile` model through a ForeignKey, allowing multiple user profiles to belong to the same city.
