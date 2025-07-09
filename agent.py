import re

def remove_char(text: str, char: str) -> str:
    return text.replace(char, "")

def replace_word(text: str, old: str, new: str) -> str:
    return re.sub(rf'\b{re.escape(old)}\b', new, text)

def capitalize_sentences(text: str) -> str:
    # Capitalize the first letter of each sentence
    return re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

def process_command(text: str, command: str) -> str:
    # Simple rule-based command parsing
    command = command.lower()
    if "remove" in command and "," in command:
        return remove_char(text, ",")
    if "replace" in command and "with" in command:
        # Example: Replace 've' with 'ile'
        import re
        match = re.search(r"replace '(.*?)' with '(.*?)'", command)
        if match:
            old, new = match.group(1), match.group(2)
            return replace_word(text, old, new)
    if "capitalize" in command and "sentence" in command:
        return capitalize_sentences(text)
    # Default: return original text
    return text 