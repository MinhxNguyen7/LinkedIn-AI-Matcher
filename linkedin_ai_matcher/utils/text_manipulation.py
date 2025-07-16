import re


def extract_tag_content(text: str, tag: str) -> str:
    """
    Extracts the content of a specific HTML-like tag from a given text.

    Args:
        text (str): The input text containing content.
        tag (str): The tag to extract content from, not including brackets.

    Returns:
        str: The content within the specified tag, or an empty string if the tag is not found.
    """
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"

    pattern = re.compile(rf"{start_tag}(.*?){end_tag}", re.DOTALL)
    match = pattern.search(text)

    return match.group(1).strip() if match else ""


def normalize_markup(markup: str, tab_size: int = 1) -> str:
    """
    Normalize HTML-like markup with proper tab indentation and whitespace cleanup.

    Args:
        markup: The markup string to normalize
        tab_size: Number of tabs to use for each indentation level

    Returns:
        Normalized markup string with proper indentation and cleaned whitespace
    """
    if not markup.strip():
        return ""

    # Remove leading/trailing whitespace from the entire string
    markup = markup.strip()

    # Split content by tags to handle inline vs block content
    # Find all tags and text content
    parts = re.split(r"(<[^>]+>)", markup)
    parts = [part.strip() for part in parts if part.strip()]  # Remove empty parts

    normalized_lines: list[str] = []
    indent_level = 0

    for part in parts:
        # Check if this is a closing tag
        if part.startswith("</"):
            indent_level = max(0, indent_level - 1)
            indented_line = "\t" * (indent_level * tab_size) + part
            normalized_lines.append(indented_line)
        # Check if this is an opening tag
        elif part.startswith("<"):
            indented_line = "\t" * (indent_level * tab_size) + part
            normalized_lines.append(indented_line)
            indent_level += 1
        # This is text content
        else:
            indented_line = "\t" * (indent_level * tab_size) + part
            normalized_lines.append(indented_line)

    return "\n".join(normalized_lines)
