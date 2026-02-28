import re
import spacy
from collections import Counter
from nltk.corpus import wordnet


def extract_verses(text):
    verses = re.findall(r'\d+[^\d]+>', text)
    kon_ru_fr = {verse: re.findall(r'(.+)>', verse)[0] for verse in verses}
    return kon_ru_fr


def parse_verses(kon_ru_fr):
    nlp = spacy.load("fr_core_news_sm")
    return[nlp(verse) for verse in kon_ru_fr.values()]


def filter_verses(kon_ru_fr, filter):
    filtered_verses = []
    for k, v in kon_ru_fr.items():
        if v in filter:
            filtered_verses.append(k)
    return filtered_verses


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


def get_cop_det_nref(text):

    kon_ru_fr = extract_verses(text)
    parsed_verses = parse_verses(kon_ru_fr)

    cop_det_verses = []
    for verse in parsed_verses:
        for idx, token in enumerate(verse[:-1]):
            if token.pos_ == 'AUX' and verse[idx + 1].lemma_ == 'un':
                if verse.text not in cop_det_verses:
                    cop_det_verses.append(verse.text)

    return filter_verses(kon_ru_fr, cop_det_verses)


def get_NdeN_nref(text):

    kon_ru_fr = extract_verses(text)
    kon_ru_fr = {k: v for k, v in kon_ru_fr.items() if re.findall(r"([^\w]de[^\w])|[^\w]d'", v)}
    parsed_verses = parse_verses(kon_ru_fr)

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

    return filter_verses(kon_ru_fr, nom_de_nom)


text = "Car la prédication de la croix est une folie pour ceux qui périssent; mais pour nous qui sommes sauvés, elle est une puissance de Dieu."
nlp = spacy.load("fr_core_news_sm")
doc = nlp(text)
constructions = []
for idx, token in enumerate(doc[:-1]):
    if token.pos_ == 'AUX' and doc[idx + 1].lemma_ == 'un':
        if doc.text not in constructions:
            constructions.append(' '.join([token.text, doc[idx + 1].text]))

print(constructions)





