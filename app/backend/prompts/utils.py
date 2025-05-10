def inject_variables(text: str, variables: dict) -> str:
    """
    Injects variables into a text containing placeholders.

    Args:
    text (str): The input text containing placeholders in the format <variable>.
    variables (dict): A dictionary of key-value pairs where keys are variable names and values are their corresponding values.

    Returns:
    str: The text with placeholders replaced by their corresponding values.
    """
    for key, value in variables.items():
        placeholder = f"<{key}>"
        text = text.replace(placeholder, str(value))
    return text
