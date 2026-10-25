"""The application boundary. Receives an authenticated main-store principal, never trusts client-supplied IDs for authority, and runs one database transaction per command."""
