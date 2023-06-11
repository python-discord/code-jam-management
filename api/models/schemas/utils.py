def discord_ids_must_be_snowflake(field_to_check: int) -> int:
    """Ensure the ids are valid Discord snowflakes."""
    if field_to_check and field_to_check.bit_length() > 64:
        raise ValueError("Field must fit within a 64 bit int.")
    return field_to_check
