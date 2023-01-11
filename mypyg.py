def remove_character(source_string, *characters_to_remove, remove_non_alphanumeric=False):
    """Removes the remove_character from a given string and returns that string without those characters.
    If remove_non_alphanumeric is True, it will remove all non letter/number characters from the string,
    except spaces which are left untouched."""
    # If no settings are selected, then return the base string
    if not characters_to_remove and not remove_non_alphanumeric:
        return source_string

    if remove_non_alphanumeric:
        new_string = ""

        # For each character, check if it is alphanumeric, and if so, add it to the new string.
        for each_character in [*source_string]:
            if each_character.isalnum() or each_character == " ":
                new_string += each_character

        return new_string

    if characters_to_remove:
        new_string = ""

        for each_character in [*source_string]:
            if each_character not in characters_to_remove:
                new_string += each_character

        return new_string
