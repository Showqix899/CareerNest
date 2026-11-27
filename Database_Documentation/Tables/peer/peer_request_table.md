# PeerRequest Model Documentation

## 1. Overview

The `PeerRequest` model stores a connection request sent from one user to another, along with its status (pending, accepted, or reject).

It uses:

- `User` (custom email-based user model) as a foreign key for both `sender` and `receiver`.
- UUID as the primary key.
- `TextChoices` for the request status.
- A unique constraint and indexes for data integrity and performance.

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
class PeerRequest(models.Model):

    class STATUS(models.TextChoices):
        pending = "pending", "Pending"
        accepted = "accepted", "Accepted"
        reject = "reject", "Reject"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_peer_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_peer_requests")
    status = models.CharField(
        max_length=20,
        choices=STATUS.choices,
        default=STATUS.pending,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_sender_receiver"
            )
        ]
        indexes = [
            models.Index(fields=["receiver", "status"]),
            models.Index(fields=["sender", "status"]),
        ]

    def __str__(self):
        return f"{self.sender.full_name} sent peer request to {self.receiver.full_name}"
```

---

## 4. STATUS Choices

```python
class STATUS(models.TextChoices):
    pending = "pending", "Pending"
    accepted = "accepted", "Accepted"
    reject = "reject", "Reject"
```

| Member | Stored value | Display label |
|---|---|---|
| `pending` | `"pending"` | Pending |
| `accepted` | `"accepted"` | Accepted |
| `reject` | `"reject"` | Reject |

Usage:

```python
PeerRequest.STATUS.pending
PeerRequest.objects.filter(status=PeerRequest.STATUS.pending)
```

---

## 5. Field Documentation

### 5.1 UUID Primary Key

```python
id = models.UUIDField(primary_key=True, default=uuid.uuid4)
```

| Option | Explanation |
|---|---|
| `UUIDField` | Stores a UUID value. |
| `primary_key=True` | Makes this field the primary key. |
| `default=uuid.uuid4` | Automatically generates a UUID. |

### 5.2 sender

```python
sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_peer_requests")
```

- The user who sends the request.
- `on_delete=models.CASCADE` deletes the request if the user is deleted.
- `related_name="sent_peer_requests"` allows `user.sent_peer_requests.all()`.

### 5.3 receiver

```python
receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_peer_requests")
```

- The user who receives the request.
- `related_name="received_peer_requests"` allows `user.received_peer_requests.all()`.

### 5.4 status

```python
status = models.CharField(max_length=20, choices=STATUS.choices, default=STATUS.pending)
```

- Stores the current state of the request.
- `choices` restricts the allowed values in forms and serializers.
- Defaults to `pending`.

### 5.5 created_at

```python
created_at = models.DateTimeField(auto_now_add=True)
```

- Set once, when the request is created.

### 5.6 updated_at

```python
updated_at = models.DateTimeField(auto_now=True)
```

- Updated automatically every time the record is saved.

---

## 6. Meta Options

### 6.1 UniqueConstraint

```python
models.UniqueConstraint(fields=["sender", "receiver"], name="unique_sender_receiver")
```

- A user cannot send more than one request to the same receiver.
- Enforced at the database level.
- Violations raise `IntegrityError`.

### 6.2 Indexes

```python
models.Index(fields=["receiver", "status"])
models.Index(fields=["sender", "status"])
```

| Index | Speeds up |
|---|---|
| `receiver` + `status` | Incoming requests, e.g. all pending requests for a user. |
| `sender` + `status` | Outgoing requests, e.g. all pending requests a user has sent. |

---

## 7. __str__() Method

```python
def __str__(self):
    return f"{self.sender.full_name} sent peer request to {self.receiver.full_name}"
```

Example output:

```text
Mahmud Showqi sent peer request to Abdullah
```

Note: this accesses `sender` and `receiver`, which can cause extra queries when listing objects (for example in the admin). Use `select_related("sender", "receiver")` to avoid this.

---

## 8. Request Workflow

```text
User A sends request to User B
              |
              v
 PeerRequest created (status = pending)
              |
      +-------+--------+
      |                |
      v                v
  B accepts         B rejects
      |                |
      v                v
status = accepted   status = reject
```

---

## 9. Example Queries

### Pending requests received by a user

```python
PeerRequest.objects.filter(
    receiver=request.user,
    status=PeerRequest.STATUS.pending
).select_related("sender").order_by("-created_at")
```

### Pending requests sent by a user

```python
PeerRequest.objects.filter(
    sender=request.user,
    status=PeerRequest.STATUS.pending
).select_related("receiver").order_by("-created_at")
```

### Accepting a request

```python
peer_request.status = PeerRequest.STATUS.accepted
peer_request.save(update_fields=["status", "updated_at"])
```

---

## 10. Example Database Record

| Field | Example |
|---|---|
| id | 3f1c2a9e-8d54-4c1b-9a77-2b6f0e5d1a10 |
| sender | b568e08b-4444-471a-a6a3-c6a2ac04d816 |
| receiver | 9c7e1d22-1f3a-4e8b-a0b4-6d2c8f7a5e33 |
| status | pending |
| created_at | Current date and time |
| updated_at | Current date and time |

---

## 11. Important Implementation Notes

1. `UniqueConstraint` only blocks duplicates in the same direction. A to B and B to A are both allowed, so check for a reverse request before creating one.
2. Nothing prevents a user from sending a request to themselves. Validate `sender != receiver` in the serializer or add a `CheckConstraint`.
3. A rejected request still occupies the unique `(sender, receiver)` pair, so the sender cannot send again unless you reuse or delete the old record.
4. Use `select_related("sender", "receiver")` when listing, to avoid N+1 queries.
5. Consider adding `editable=False` to the UUID `id`, as in the `User` model.
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

## 12. Summary

| Component | Responsibility |
|---|---|
| STATUS | Defines allowed request states. |
| sender / receiver | Link the request to the two users. |
| UniqueConstraint | Prevents duplicate requests in the same direction. |
| Index | Speeds up lookups by receiver/sender and status. |
| created_at / updated_at | Track when the request was created and last changed. |
| related_name | Provides reverse access from the `User` model. |

**In short:** `PeerRequest` tracks the lifecycle of a connection request between two users (pending, accepted, reject).