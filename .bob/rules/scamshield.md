# Bob Coding Rules — ScamShield Project

These rules apply to all code written in this project.

## 1. Type Hints

Every function and method **must** include full Python type hints for all
parameters and return values.

```python
# Good
def classify_message(text: str) -> dict:
    ...

# Bad
def classify_message(text):
    ...
```

## 2. Test for Every Tool

Every tool module in `tools/` **must** have a corresponding test file in
`tests/`. Tests are named `test_<tool_name>.py`.

## 3. Synthetic Data Only

All test fixtures, evaluation datasets, and example inputs **must** use
synthetic (made-up) data.

- ✅ Synthetic names, phone numbers, email addresses, account numbers
- ❌ Real personal data (names, addresses, national IDs, real phone numbers)
- ❌ Real credentials, API keys, passwords, tokens

## 4. Never Include Real Personal Data or Credentials

No file in this repository may contain:
- Real names, addresses, or identification numbers
- Real phone numbers or email addresses belonging to actual people
- Passwords, API keys, secrets, or tokens of any kind
- The contents of `.env` must never be read or printed in code or logs

## 5. Every Tool Returns Plain JSON

Every tool function must return a plain Python `dict` (serialisable to JSON
with `json.dumps`). No custom objects, no exceptions as return values.

```python
# Good
return {"flagged": True, "reason": "urgency_language", "score": 0.9}

# Bad
return ScamResult(flagged=True)
```
