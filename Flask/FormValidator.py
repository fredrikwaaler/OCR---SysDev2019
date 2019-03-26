def validate_new_name(new_name):
    errors = []
    if new_name.strip() == "":
        errors.append("New name cannot be empty.")
    if not new_name.isalpha():
        errors.append("New name must be only letters")

    return len(errors) == 0, errors

