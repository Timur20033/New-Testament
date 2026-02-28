import re


def clean_kon(text: str) -> str:
    """
    Cleans the original Konabere New Testament
    """
    text = re.sub(r'([^\n\d])(\d+ )', r'\1\n\2', text)
    text = re.sub(r'([^\n])(\n.+\n\(.+\))', r'\1\n\2', text)
    text = re.sub(r'([\.»,;:!?])\w([» ]?\n)', r'\1\2', text)
    return text


def clean_rus(text: str) -> str:
    """
    Cleans the original Russian New Testament
    """
    text = text.replace('', '').replace('', '')
    text = text.replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n')
    return text