import re
import spacy


def get_cop_det(text):

    verses = re.findall(r'\d+[^\d]+>', text)
    kon_ru_fr = {verse: re.findall(r'(.+)>', verse)[0] for verse in verses}
    
    nlp = spacy.load("fr_core_news_sm")
    parsed_verses = [nlp(verse) for verse in kon_ru_fr.values()]

    cop_det_verses = []
    for verse in parsed_verses:
        for idx, token in enumerate(verse[:-1]):
            if token.dep_ == 'cop' and verse[idx+1].text.lower() in ['un', 'une']:
                if verse.text not in cop_det_verses:
                    cop_det_verses.append(verse.text)

    tr_verses = []
    for k, v in kon_ru_fr.items():
        if v in cop_det_verses:
            tr_verses.append(k)

    return tr_verses


def get_nom_de_nom(text):

    verses = re.findall(r'\d+[^\d]+>', text)
    kon_ru_fr = {verse: re.findall(r'(.+)>', verse)[0] for verse in verses}
    kon_ru_fr = {k: v for k, v in kon_ru_fr.items() if re.findall(r"([^\w]de[^\w])|[^\w]d'", v)}

    nlp = spacy.load("fr_core_news_sm")
    parsed_verses = [nlp(verse) for verse in kon_ru_fr.values()]

    nom_de_nom = []
    for verse in parsed_verses:
        for idx, token in enumerate(verse):
            if (token.pos_ == 'ADP' 
                and token.text in ['de', "d'"] 
                and token.head.pos_ == 'NOUN' 
                and token.head.head.pos_ == 'NOUN'
                and token.head.head.i == idx - 1):
                if (token.head.i == idx + 1 
                    and verse not in nom_de_nom):
                    nom_de_nom.append(verse.text)
                elif (verse[idx + 1].lemma_ == 'un' 
                        and verse not in nom_de_nom):
                    nom_de_nom.append(verse.text)

    nom_de_nom_verses = []
    for k, v in kon_ru_fr.items():
        if v in nom_de_nom:
            nom_de_nom_verses.append(k)

    return nom_de_nom_verses


with open('Parallel corpus/Konabere-Russian-French/United books/New Testament.txt', 'r', encoding='utf-8') as f:
    text = f.read()

with open('Contexts/nom_de_nom.txt', 'w', encoding='utf-8') as f:
    for verse in get_nom_de_nom(text):
        f.write(verse + '\n\n')


