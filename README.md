# Deterministic A/B Testing with Python

A simple demonstration of deterministic user bucketing for A/B testing using Python, UUIDs, and SHA-256 hashing.

The goal is to understand how experimentation platforms assign users to different experiment variants consistently, without requiring a database lookup on every request.

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

The assignments are deterministic, not random on every request.

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

## Understanding Traffic Distribution

An important characteristic of deterministic hashing is that it provides a statistically balanced distribution over a sufficiently large population, not an exact distribution for every group of users.

Consider an experiment where 10 users enter a funnel with a configured 50/50 split.

You might get:

```text
User 1  -> A
User 2  -> A
User 3  -> A
User 4  -> B
User 5  -> A
User 6  -> A
User 7  -> A
User 8  -> A
User 9  -> B
User 10 -> A

Variant A: 8 users (80%)
Variant B: 2 users (20%)
```

This is valid behaviour.

Each user is independently assigned based on their deterministic hash. There is no coordination between assignments to ensure that every group of 10 users contains exactly five users in each variant.

### Why does this happen?

Hashing distributes users across buckets. It does not maintain a counter of how many users have already been assigned to each variant.

For a 50/50 allocation:

- Every user has an approximately equal probability of landing in either variant.
- Small populations can exhibit significant imbalances.
- As the population grows, the observed distribution generally approaches the configured allocation.

For example, a 50/50 split across 10,000 users is generally much closer to the expected distribution than a split across 10 users.

This is a consequence of random variation, not a hashing failure.

## The Drawback: Deterministic Hashing Does Not Guarantee Exact Allocation

If the business requirement is to ensure that exactly 50% of participants receive A and 50% receive B, deterministic hashing alone cannot satisfy that requirement.

It has no awareness of previous assignments.

Two possible approaches exist:

**1. Deterministic hashing**

Each user is independently bucketed using their identity and experiment key.

Advantages:
- No central coordination required.
- Consistent assignments across application servers.
- Highly scalable.
- No database write required for every assignment.

Disadvantages:
- No guarantee of an exact 50/50 distribution for small populations.
- Some experiments may experience temporary allocation imbalances.
- Changes to variant allocation boundaries can change existing users' assignments.

**2. Coordinated or block-based allocation**

Instead of independently hashing every user, the system coordinates assignments to maintain a desired distribution.

For example, with blocks of 10 participants:

```text
Block 1:
A: 5 users
B: 5 users

Block 2:
A: 5 users
B: 5 users

Block 3:
A: 5 users
B: 5 users
```

Within each block, assignments can be randomly permuted.

Advantages:
- Maintains a controlled allocation ratio within each completed block.
- Useful when balanced sample sizes are important.
- Reduces allocation imbalances in smaller experiments.

Disadvantages:
- Requires shared assignment state.
- Requires atomic allocation to handle concurrent requests.
- Introduces additional infrastructure and operational complexity.
- Incomplete blocks can still have temporary imbalances.
- Assignment order and block design require careful statistical consideration.

### Why not always enforce an exact 50/50 split?

Exact balancing is not automatically better for every experiment.

Random assignment is important for unbiased experimentation. Poorly implemented allocation mechanisms can introduce ordering effects or selection bias.

For most large-scale experimentation platforms, deterministic hashing is a practical trade-off between scalability, simplicity, and statistically balanced allocation.

## Deterministic Assignment vs. Sticky Assignment

These are two different concepts.

**Deterministic assignment**

The same user ID and experiment configuration produce the same variant every time.

**Sticky assignment**

Once a user has been assigned a variant, that assignment remains unchanged even if experiment configuration changes.

Deterministic hashing alone does not guarantee sticky assignments.

For production experimentation systems, assignments can be persisted in a database using a unique constraint on:

```text
(experiment_id, user_id)
```

This protects existing assignments from changing when traffic allocation is modified and helps handle concurrent requests.

## What Happens When Experiment Configuration Changes?

Suppose an experiment initially has:

```text
Variant A: 50%
Variant B: 50%
```

Later, the allocation changes:

```text
Variant A: 25%
Variant B: 75%
```

The hashing algorithm itself has not changed, but the bucket boundaries have.

Users previously assigned to A may now receive B.

This is an important consideration when designing long-running experiments.

Possible strategies include:

- Preserve existing assignments and only allocate newly eligible users.
- Create a new experiment version.
- Persist assignments and explicitly manage migrations.

## What This Demonstrates

- Deterministic user bucketing.
- Consistent experiment assignment across application instances.
- Hash-based traffic distribution.
- Experiment isolation using unique keys.
- Statistical distribution versus exact allocation.
- The difference between deterministic and persistent assignments.
- Trade-offs between stateless hashing and coordinated allocation.

## A Note on Production Systems

This is an educational implementation designed to explain the underlying concept.

It is not an exact reproduction of PostHog's implementation.

Production experimentation platforms must also consider:

- Identity resolution and anonymous-to-authenticated transitions.
- Feature flag configuration consistency across application servers.
- Assignment persistence.
- Exposure tracking and conversion attribution.
- Concurrent assignment requests.
- Experiment lifecycle and allocation changes.
- Statistical validity and sample-size requirements.

## Further Reading

- [PostHog – Feature Flags](https://posthog.com/docs/feature-flags)
- [PostHog – Experiments](https://posthog.com/docs/experiments)
- [PostHog GitHub Repository](https://github.com/PostHog/posthog)

## License

MIT License