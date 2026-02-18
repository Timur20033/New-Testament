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


def parallel(text_rus, text_kon):
    lines_rus = re.findall(r'\d+ (?:[^\d\n]+\n)+', text_rus)
    lines_kon = re.findall(r'\d+ (?:[^\d\n]+\n)+', text_kon)
    if len(lines_kon) == len(lines_rus):
        for idx, line_kon in enumerate(lines_kon):
            line_rus = lines_rus[idx]
            line_rus = re.sub('\d+', '', line_rus).strip()
            repl = line_kon + line_rus + '\n\n'
            text_kon = text_kon.replace(line_kon, repl, 1)
        return text_kon
    else:
        return f'{len(lines_rus)} != {len(lines_kon)}'
    