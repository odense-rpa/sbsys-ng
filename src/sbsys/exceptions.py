class SbsysError(Exception):
    """Base exception for SbSys API errors."""


class SbsysAuthenticationError(SbsysError):
    """Token acquisition failed."""


class SbsysNotFoundError(SbsysError):
    """Resource not found (person, case, template, etc.)."""


class SbsysValidationError(SbsysError):
    """Invalid input (bad CPR, missing required field, etc.)."""
