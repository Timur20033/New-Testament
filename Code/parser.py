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