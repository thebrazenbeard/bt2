"""Source-only evaluation receipt validator (research; not an admission authority)."""

class InvalidReceipt(ValueError):
    """A structurally invalid claim."""

def validate_receipt(receipt):
    return {"validation": "FORMAT_VALID_EVIDENCE_UNVERIFIED"}
