import re


def clean_kon(text):
    text = re.sub(r'([^\n\d])(\d+ )', r'\1\n\2', text)
    text = re.sub(r'([^\n])(\n.+\n\(.+\))', r'\1\n\2', text)
    text = re.sub(r'([\.»,;:!?])\w([» ]?\n)', r'\1\2', text)
    return text


def clean_rus(text):
    text = text.replace('', '').replace('', '')
    text = text.replace('\n\n\n\n', '\n\n').replace('\n\n\n', '\n\n')
    return text