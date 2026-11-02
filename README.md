# Deterministic A/B Testing with Python

A simple implementation of deterministic user bucketing for A/B testing using Python, UUIDs, and SHA-256 hashing.

The goal is to demonstrate how experimentation platforms can consistently assign users to different experiment variants without requiring a database lookup on every request.

## How It Works

Instead of randomly assigning users whenever they visit an application, we use deterministic hashing.

The same user ID and experiment key always produce the same hash, resulting in the same variant assignment, provided the experiment configuration remains unchanged.

For example:

```text
User UUID                              Variant
------------------------------------------------
550e8400-e29b-41d4-a716-446655440001   A
550e8400-e29b-41d4-a716-446655440002   B
550e8400-e29b-41d4-a716-446655440003   A
550e8400-e29b-41d4-a716-446655440004   B
```

The assignments are deterministic, not random.

## The Hashing Logic

We combine the experiment key and user ID:

```python
value = f"{EXPERIMENT_KEY}.{user_id}"
```

We then generate a SHA-256 hash:

```python
digest = hashlib.sha256(value.encode()).hexdigest()
```

Convert part of the hash into a normalized bucket between 0 and 1:

```python
bucket = int(digest[:8], 16) / 0xFFFFFFFF
```

Finally, determine the variant:

```python
variant = "A" if bucket < 0.5 else "B"
```

For a 50/50 experiment:

- Bucket below 0.5 → Variant A
- Bucket equal to or above 0.5 → Variant B

## Getting Started

### Requirements

- Python 3.8+
- No external dependencies

### Run

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/deterministic-ab-testing.git
cd deterministic-ab-testing
```

Run the script:

```bash
python main.py
```

## Example Implementation

```python
import hashlib

EXPERIMENT_KEY = "new-checkout"

def assign_variant(user_id: str) -> str:
    value = f"{EXPERIMENT_KEY}.{user_id}"

    digest = hashlib.sha256(value.encode()).hexdigest()

    bucket = int(digest[:8], 16) / 0xFFFFFFFF

    return "A" if bucket < 0.5 else "B"


user_id = "550e8400-e29b-41d4-a716-446655440001"

print(assign_variant(user_id))
```

## Experimenting with Different Traffic Splits

You can easily change the traffic allocation.

For example, an 80/20 split:

```python
return "A" if bucket < 0.8 else "B"
```

| Variant | Traffic allocation |
|---|---:|
| A | 80% |
| B | 20% |

Changing the experiment key also changes the bucketing namespace, meaning the same user can receive a different assignment in another experiment.

## Important: Deterministic Assignment vs. Sticky Assignment

These are two different concepts.

**Deterministic assignment**

The same user ID and experiment configuration produce the same variant every time.

**Sticky assignment**

Once a user has been assigned a variant, that assignment remains unchanged even if experiment configuration changes.

Deterministic hashing alone does not guarantee sticky assignments.

For production experimentation systems, you may want to persist assignments in a database using a unique constraint on:

```text
(experiment_id, user_id)
```

This protects existing assignments from changing when traffic allocation is modified and helps handle concurrent requests.

## What This Demonstrates

- Deterministic user bucketing
- Consistent experiment assignment across application instances
- Hash-based traffic distribution
- Experiment isolation using unique keys
- The difference between deterministic and persistent assignments

## A Note on Production Systems

This is an educational implementation designed to explain the underlying concept.

It is not an exact reproduction of PostHog's implementation. Production experimentation platforms also need to consider identity resolution, feature flag configuration consistency, exposure tracking, assignment persistence, and experiment lifecycle management.
