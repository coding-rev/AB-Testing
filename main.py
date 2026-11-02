
import hashlib
import uuid

EXPERIMENT_KEY = "new-checkout"

def assign_variant(user_id: str) -> str:
    # Combine experiment key and user ID
    value = f"{EXPERIMENT_KEY}.{user_id}"

    # Generate deterministic hash
    digest = hashlib.sha256(value.encode()).hexdigest()

    # Convert hash to an integer between 0 and 1
    bucket = int(digest[:8], 16) / 0xFFFFFFFF

    # 50/50 traffic split
    return "A" if bucket < 0.5 else "B"


# Generate 10 reproducible UUIDs
user_ids = [
    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"user-{i}"))
    for i in range(1, 11)
]

for user_id in user_ids:
    print(f"{user_id} -> Variant {assign_variant(user_id)}")
