import re


def find_verses(text: str) -> list[str]:
    """
    Extracts verses from original texts indepedently from source language
    """
    return re.findall(r'\d+ (?:[^\d\n]+\n)+', text)


def parallel_kon_rus(text_rus: str, text_kon: str) -> str:
    """
    Creates a parallel Konabere-Russian corpus
    """
    lines_rus = find_verses(text_rus)
    lines_kon = find_verses(text_kon)

    if len(lines_kon) == len(lines_rus):
        for idx, line_kon in enumerate(lines_kon):
            line_rus = lines_rus[idx]
            line_rus = re.sub('\d+', '', line_rus).strip()
            repl = line_kon + line_rus + '\n\n'
            text_kon = text_kon.replace(line_kon, repl, 1)

        return text_kon
    
    else:

        return f'{len(lines_rus)} != {len(lines_kon)}'
    

def highlight_rus(par_text: str) -> str:
    """
    Puts < and > around Russian translations
    """
    lines_rus_kon = find_verses(par_text)

    for line in lines_rus_kon:
        sublines = line.strip().split('\n')
        kon = '\n'.join(sublines[:-1])
        rus = sublines[-1].strip()
        replacement = f'{kon}\n<{rus}>\n'
        par_text = par_text.replace(line, replacement)

    return par_text


def add_fr(par_text, fr_text) -> str:
    """
    Adds french translation to the bilingual corpus
    """
    lines_ru_kon = find_verses(par_text)
    lines_fr = find_verses(fr_text)

    if len(lines_ru_kon) == len(lines_fr):
        for idx, line_ru_kon in enumerate(lines_ru_kon):
            line_fr = re.sub('\d+ (.+)', r'\1', lines_fr[idx])
            replacement = re.sub('>', f'\n{line_fr.strip()}>', line_ru_kon)
            par_text = par_text.replace(line_ru_kon, replacement, 1)

        return par_text
    
    else:

        return f'{len(lines_ru_kon)} != {len(lines_fr)}'