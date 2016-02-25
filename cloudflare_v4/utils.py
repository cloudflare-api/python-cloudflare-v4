def sanitize_secrets(secrets):
    redacted_phrase = 'REDACTED'

    secrets_copy = secrets.copy()
    if 'password' in secrets_copy:
        secrets_copy['password'] = redacted_phrase
    elif 'X-Auth-Key' in secrets_copy:
        secrets_copy['X-Auth-Key'] = redacted_phrase

    return secrets_copy
