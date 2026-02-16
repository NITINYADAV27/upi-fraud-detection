# Fraud Decision Strategy

## Decision: ALLOW
Used when:
- Account age is high
- Transaction amount matches history
- No abnormal behavior detected

Rationale:
Low risk, normal user behavior.

---

## Decision: STEP_UP_AUTH
Used when:
- First-time beneficiary
- Medium transaction velocity
- Slightly abnormal amount

Rationale:
Transaction may be genuine but needs confirmation.

---

## Decision: BLOCK
Used when:
- New account
- High geo risk
- Multiple failed PIN attempts
- Abnormally high amount

Rationale:
High probability of fraud; immediate action required.
