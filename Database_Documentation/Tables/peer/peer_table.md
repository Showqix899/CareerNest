# Peer Model Documentation

## 1. Overview

The `Peer` model stores an established connection between two users. A `Peer` record is created when a `PeerRequest` is accepted.

It uses:

- `User` (custom email-based user model) as a foreign key for both `sender` and `receiver`.
- UUID as the primary key.
- `related_name` to access connections from the `User` side.

---

## 2. Imports

```python
from accounts.models import User
from django.db import models
import uuid
```

| Import | Purpose |
|---|---|
| `User` | Custom user model used for `sender` and `receiver`. |
| `models` | Provides Django model fields. |
| `uuid` | Generates unique identifiers. |

---

## 3. Model Code

```python
class Peer(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peers_as_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peers_as_receiver")
    responded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.full_name} is connected to {self.receiver.full_name}"
```

---

## 4. Field Documentation

### 4.1 UUID Primary Key

```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4)
```

| Option | Explanation |
|---|---|
| `UUIDField` | Stores a UUID value. |
| `primary_key=True` | Makes this field the primary key. |
| `default=uuid.uuid4` | Automatically generates a UUID. |

### 4.2 sender

```python
sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peers_as_sender")
```

- The user who originally sent the peer request.
- `on_delete=models.CASCADE` deletes the connection if the user is deleted.
- `related_name="peers_as_sender"` allows `user.peers_as_sender.all()`.

### 4.3 receiver

```python
receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peers_as_receiver")
```

- The user who accepted the request.
- `related_name="peers_as_receiver"` allows `user.peers_as_receiver.all()`.

### 4.4 responded_at

```python
responded_at = models.DateTimeField(auto_now_add=True)
```

- Set once, when the record is created (the moment the request was accepted).
- Not updated on later saves.

---

## 5. __str__() Method

```python
def __str__(self):
    return f"{self.sender.full_name} is connected to {self.receiver.full_name}"
```

Example output:

```text
Mahmud Showqi is connected to Abdullah
```

Note: this accesses `sender` and `receiver`, which can cause extra queries when listing objects. Use `select_related("sender", "receiver")` to avoid this.

---

## 6. Relationship Overview

```text
User ──< Peer >── User
```

| Access | Meaning |
|---|---|
| `user.peers_as_sender` | Connections where the user sent the original request. |
| `user.peers_as_receiver` | Connections where the user accepted the request. |

A user's full peer list is the union of both.

---

## 7. How a Peer Is Created

```text
PeerRequest (status = pending)
              |
              v
      Receiver accepts
              |
              v
 PeerRequest.status = accepted
              |
              v
     Peer record created
```

```python
from django.db import transaction

with transaction.atomic():
    peer_request.status = PeerRequest.STATUS.accepted
    peer_request.save(update_fields=["status", "updated_at"])
    Peer.objects.create(sender=peer_request.sender, receiver=peer_request.receiver)
```

`transaction.atomic()` makes the status update and the `Peer` creation succeed or fail together.

---

## 8. Example Queries

### All peers of a user (either direction)

```python
from django.db.models import Q

Peer.objects.filter(
    Q(sender=request.user) | Q(receiver=request.user)
).select_related("sender", "receiver").order_by("-responded_at")
```

### Check if two users are already connected

```python
Peer.objects.filter(
    Q(sender=user_a, receiver=user_b) | Q(sender=user_b, receiver=user_a)
).exists()
```

### Remove a connection

```python
Peer.objects.filter(
    Q(sender=user_a, receiver=user_b) | Q(sender=user_b, receiver=user_a)
).delete()
```

---

## 9. Example Database Record

| Field | Example |
|---|---|
| id | 7a4d9b10-52c3-4f6e-8b21-0e9d3c6a7f88 |
| sender | b568e08b-4444-471a-a6a3-c6a2ac04d816 |
| receiver | 9c7e1d22-1f3a-4e8b-a0b4-6d2c8f7a5e33 |
| responded_at | Current date and time |

---

## 10. Important Implementation Notes

1. A peer connection is mutual, but it is stored as one row with a sender and a receiver. Always query both directions with `Q(sender=...) | Q(receiver=...)`.
2. There is no unique constraint, so duplicate connections are possible. Consider a `UniqueConstraint` on `["sender", "receiver"]`, and check the reverse pair before creating.
3. There are no indexes. Add indexes on `sender` and `receiver` if the table grows.
4. Always filter by the current user, otherwise every user sees all connections.
5. Use `select_related("sender", "receiver")` when listing, to avoid N+1 queries.
6. `responded_at` is `auto_now_add`, so it records only the creation time.
7. Consider adding `editable=False` to the UUID `id`, as in the `User` model.
8. Run migrations after changing model fields.

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

## 11. Summary

| Component | Responsibility |
|---|---|
| Peer | Stores an accepted connection between two users. |
| sender / receiver | Link the connection to the two users. |
| responded_at | Records when the connection was created. |
| related_name | Provides reverse access from the `User` model. |
| __str__() | Returns a readable description of the connection. |

**In short:** `Peer` represents an established connection between two users, created after a `PeerRequest` is accepted.