import re
import spacy
from collections import Counter
from nltk.corpus import wordnet


def extract_verses(text: str) -> dict[str, str]:
    """
    Divides a parallel corpus into verses and then subdivides them into translations
    """
    verses = re.findall(r'\d+[^\d]+>', text)
    kon_ru_fr = {verse: re.findall(r'(.+)>', verse)[0] for verse in verses}

    return kon_ru_fr


def parse_verses(kon_ru_fr: dict[str, str]) -> list[str]:
    """
    Does morphosyntactic annotation of french verses
    """
    nlp = spacy.load("fr_core_news_sm")
    return[nlp(verse) for verse in kon_ru_fr.values()]


def filter_verses(kon_ru_fr: dict[str, str], target: dict[str, list[str]]) -> list[str]:
    """
    Filters multilingual verses based on the targed
    """
    filtered = []
    for k, v in kon_ru_fr.items():
        if v in target:
            highl_verse = k
            for constr in target[v]:
                highl_verse = highl_verse.replace(constr, constr.upper())
            filtered.append(highl_verse)

    return filtered


def is_concrete(lemma: str) -> bool:
    """
    Checks if french lemma is abstract or concrete
    """
    hypernyms = []
    synsets = wordnet.synsets(lemma, pos='n', lang='fra')

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
        

def build_NdeN(w1: str, w2: str, w3: str, w4: str) -> str: 
    """
    Builds an original construction from separate words
    """
    if not w4:
        constr = f'{w1} {w2} {w3}'
        if "d'" in constr:
            constr = constr.replace("d' ", "d'")

    else:
        constr = f'{w1} {w2}{w3} {w4}'
    
    return constr


def is_NdeN(w1: spacy.tokens.token.Token, 
            w2: spacy.tokens.token.Token, 
            w3: spacy.tokens.token.Token, 
            w4: spacy.tokens.token.Token) -> tuple[bool, str]:
    """
    Checks if the token sequence is "noun de (un) noun" construction 
    and if it does not include abstract lexic
    """
    if (w1.pos_ == 'NOUN'  
        and w2.text in ['de', "d'"] 
        and w3.pos_ == 'NOUN'):
        if is_concrete(w1.lemma_) and is_concrete(w3.lemma_):
            constr = build_NdeN(w1.text, w2.text, w3.text, None)

            return True, constr

    elif (w1.pos_ == 'NOUN' 
          and w2.text in ['de', "d'"] 
          and w3.lemma_ == 'un' 
          and w4.pos_ == 'NOUN'):
        if is_concrete(w1.lemma_) and is_concrete(w4.lemma_):
            constr = build_NdeN(w1.text, w2.text, w3.text, w4.text)
    
            return True, constr 
    
    return False, None


def get_NdeN(text: str) -> list[str]:
    """
    Extracts from the text verses with "noun de (un) noun" constructions
    """
    kon_ru_fr = extract_verses(text)
    kon_ru_fr = {k: v for k, v in kon_ru_fr.items() if re.findall(r"([^\w]de[^\w])|[^\w]d'", v)}
    parsed_verses = parse_verses(kon_ru_fr)

    NdeN_verses = {verse.text: [] for verse in parsed_verses}
    for verse in parsed_verses:
        for token in verse[:-3]:
            constr = is_NdeN(token,
                             verse[token.i + 1],
                             verse[token.i + 2],
                             verse[token.i + 3])
            if constr[0]:
                NdeN_verses[verse.text].append(constr[1])
    
    NdeN_verses = {k: v for k, v in NdeN_verses.items() if v}

    return filter_verses(kon_ru_fr, NdeN_verses)


def get_cop_det_nref(text: str):

    kon_ru_fr = extract_verses(text)
    parsed_verses = parse_verses(kon_ru_fr)

    cop_det_verses = []
    for verse in parsed_verses:
        for idx, token in enumerate(verse[:-1]):
            if token.pos_ == 'AUX' and verse[idx + 1].lemma_ == 'un':
                if verse.text not in cop_det_verses:
                    cop_det_verses.append(verse.text)

    return filter_verses(kon_ru_fr, cop_det_verses)