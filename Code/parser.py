import re
import spacy
from collections import Counter
import nltk
from nltk.corpus import wordnet


def is_concrete(lemma, pos, lang):
    hypernyms = []
    synsets = wordnet.synsets(lemma, pos=pos, lang=lang)
    for synset in synsets:
        for path in synset.hypernym_paths():
            hypernyms.append(path[2].name().split('.')[0])
    if not hypernyms:
        return None
    else:
        freq_sense = Counter(hypernyms).most_common(1)[0][0]
        if freq_sense == 'object':
            return True
        else:
            return False


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


def get_NdeN_nref(text):

    verses = re.findall(r'\d+[^\d]+>', text)
    kon_ru_fr = {verse: re.findall(r'(.+)>', verse)[0] for verse in verses}
    kon_ru_fr = {k: v for k, v in kon_ru_fr.items() if re.findall(r"([^\w]de[^\w])|[^\w]d'", v)}

    nlp = spacy.load("fr_core_news_sm")
    parsed_verses = [nlp(verse) for verse in kon_ru_fr.values()]

    nom_de_nom = []
    for verse in parsed_verses:
        for idx, token in enumerate(verse):
            w1 = token.head.head
            w2 = token.head
            if (token.pos_ == 'ADP' 
                and token.text in ['de', "d'"] 
                and w1.pos_ == 'NOUN' 
                and w2.pos_ == 'NOUN'
                and token.head.head.i == idx - 1):
                    if is_concrete(w1.lemma_, 'n', 'fra') and is_concrete(w2.lemma_, 'n', 'fra'):
                        if (w2.i == idx + 1 
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

with open('Contexts/Noun + de + noun (non-referential).txt', 'w', encoding='utf-8') as f:
    for verse in get_NdeN_nref(text):
        f.write(verse + '\n\n')