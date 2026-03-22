import re
import spacy
from collections import Counter
from nltk.corpus import wordnet


class VerseManager:
    """
    Tool for searching necessary constructions: NdeN, COPunN, VunN, NdeMat, BodyPartdeN
    """
    def __init__(self, text: str) -> None:

        self.text = text
        self.kon_ru_fr = {}
        self.parsed_verses = {}
        self.target_verses = []
        self.filtered_verses = []


    def extract_verses(self) -> None:
        """
        Divides a parallel corpus into verses and then subdivides them into translations
        """
        verses = re.findall(r'\d+[^\d]+>', self.text)
        self.kon_ru_fr = {verse: re.findall(r'(.+)>', verse)[0] for verse in verses}


    def parse_verses(self) -> None:
        """
        Does morphosyntactic annotation of french verses
        """
        nlp = spacy.load("fr_core_news_sm")
        self.parsed_verses = [nlp(verse) for verse in self.kon_ru_fr.values()]


    def get_constructions(self, constr_type: str) -> None:
        """
        Extracts necessary constructions from the list of preprocessed verses
        """
        extractor = Extractor(self.parsed_verses)
        
        if constr_type == 'NdeN':
            self.target_verses = extractor.get_NdeN()

        if constr_type == 'COPunN':
            self.target_verses = extractor.get_COPunN()

        if constr_type == 'VunN':
            self.target_verses = extractor.get_VunN()

        if constr_type == 'NdeMat':
            self.target_verses = extractor.get_NdeMat()

        if constr_type == 'BodyPartdeN':
            self.target_verses = extractor.get_BodyPartdeN()
        
    
    def filter_verses(self) -> None:
        """
        Deletes those verses from database that do not contain a necessary construction
        """
        for k, v in self.kon_ru_fr.items():
            if v in self.target_verses:
                highl_verse = k
                for constr in self.target_verses[v]:
                    highl_verse = highl_verse.replace(constr, constr.upper())
                self.filtered_verses.append(highl_verse)

    
    def search(self, constr_type: str, file_name: str) -> None:
        """
        Searches for necessary constructions in the corpus
        by completing all the tasks above at once;
        then writes results in the file
        """
        self.extract_verses()
        self.parse_verses()
        self.get_constructions(constr_type)
        self.filter_verses()

        with open(f'Contexts/{file_name}.txt', 'w', encoding='utf-8') as f:
            f.write(f'NUMBER OF VERSES: {len(self.filtered_verses)}\n\n')
            
            for verse in self.filtered_verses:
                f.write(verse + '\n\n')


class Checker:
    """
    Checks if a token sequence is a particular type of construction
    """
    def __init__(self):

        with open('Code/materials.txt', 'r', encoding='utf-8') as f:
            self.materials = f.read().strip().split('\n')


    def is_concrete(self, lemma: str) -> bool:
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
            

    def is_body_part(self, lemma: str) -> bool:
        """
        Checks if a token is a body part
        """
        for i in wordnet.synsets(lemma, pos='n', lang='fra'):
            for path in i.hypernym_paths():
                if len(path) >= 5:
                    if 'body_part' == path[4].name().split('.')[0]:
                        return True
                
        return False
    

    def is_living_thing(self, lemma: str) -> bool:
        """
        Checks if a token designates a living creature
        """
        for synset in wordnet.synsets(lemma, pos='n', lang='fra'):
            for path in synset.hypernym_paths():
                
                if len(path) >= 5:
                    if path[4].name().split('.')[0] == 'living_thing':

                        return True
                    
        return False
    

    def is_BodyPartdeN(self,
                       w1: spacy.tokens.token.Token, 
                       w2: spacy.tokens.token.Token,
                       w3: spacy.tokens.token.Token,
                       w4: spacy.tokens.token.Token) -> tuple[bool, str]:
        """
        Checks if a token sequence is a BodyPartdeN construction
        """
        if (w1.pos_ == 'NOUN' 
            and self.is_body_part(w1.lemma_) 
            and w2.text not in ["du", "des"]
            and w2.lemma_ == 'de'):

            constr = ''

            if w3.lemma_ == 'un' and w4.pos_ == 'NOUN':
                if self.is_living_thing(w4.lemma_):
                    constr = f'{w1} {w2} {w3} {w4}'

            elif w3.pos_ == 'NOUN':
                if self.is_living_thing(w3.lemma_):
                    constr = f'{w1} {w2} {w3}'

            if "' " in constr:
                constr = constr.replace("' ", "'")

            if constr:
                return True, constr
        
        return False, None
        

    def is_NdeN(self,
                w1: spacy.tokens.token.Token, 
                w2: spacy.tokens.token.Token, 
                w3: spacy.tokens.token.Token, 
                w4: spacy.tokens.token.Token) -> tuple[bool, str]:
        """
        Checks if the token sequence is an NdeN construction 
        and if it does not include abstract nouns
        """
        if (w1.pos_ == 'NOUN'  
            and w2.text in ['de', "d'"] 
            and w3.pos_ == 'NOUN'):
            if self.is_concrete(w1.lemma_) and self.is_concrete(w3.lemma_):
                constr = f'{w1} {w2} {w3}'
                if "' " in constr:
                    constr = constr.replace("' ", "'")

                return True, constr

        elif (w1.pos_ == 'NOUN' 
            and w2.text in ['de', "d'"] 
            and w3.lemma_ == 'un' 
            and w4.pos_ == 'NOUN'):
            if self.is_concrete(w1.lemma_) and self.is_concrete(w4.lemma_):
                constr = f'{w1} {w2}{w3} {w4}'
        
                return True, constr 
        
        return False, None
    

    def is_COPunN(self,
                  verse: spacy.tokens.doc.Doc, 
                  w1: spacy.tokens.token.Token, 
                  w2: spacy.tokens.token.Token, 
                  w3: spacy.tokens.token.Token) -> tuple[bool, str]:
        """
        Checks if the token sequence is a COPunN construction 
        and if it does not include abstract nouns
        """
        if w1.pos_ == 'AUX' and w2.lemma_ == 'un' and w3.pos_ == 'NOUN':

            if self.is_concrete(w3.lemma_):

                if w2.i == w3.i - 1:
                    constr = f'{w1} {w2} {w3}'

                else:
                    wrds = ' '.join([verse[idx].text for idx in range(w2.i + 1, w3.i)])
                    constr = f'{w1} {w2} {wrds} {w3}'

                return True, constr
            
        return False, None
    

    def is_VunN(self,
                verse: spacy.tokens.doc.Doc, 
                w1: spacy.tokens.token.Token,
                w2: spacy.tokens.token.Token,
                w3: spacy.tokens.token.Token) -> tuple[bool, str]:
        """
        Checks if token sequence is a VunN construction
        """
        if (w1.pos_ == 'VERB' 
            and w1.pos_ != 'cop'
            and w2.text in ['un', 'une', 'des']
            and w3.pos_ == 'NOUN'):

            if self.is_concrete(w3.lemma_):
            
                if w3.i == w2.i + 1:
                    constr = f'{w1.text} {w2.text} {w3.text}'
                
                else:
                    wrds = ' '.join([verse[idx].text for idx in range(w2.i + 1, w3.i)])
                    constr = f'{w1} {w2} {wrds} {w3}'

                return True, constr
        
        return False, None
    

    def is_NdeMat(self,
               w1: spacy.tokens.token.Token,
               w2: spacy.tokens.token.Token,
               w3: spacy.tokens.token.Token) -> tuple[bool, str]:
        """
        Checks if a token sequence is an NdeMat construction
        """
        if (w1.pos_ == 'NOUN' 
            and w2.lemma_ == 'de'
            and w3.lemma_ in self.materials):

            constr = f'{w1} {w2} {w3}'
            if "' " in constr:
                constr = constr.replace("' ", "'")

            return True, constr
        
        return False, None
    

class Extractor:
    """
    Highlights different types of constructions in the list of preprocessed verses
    """
    def __init__(self, parsed_verses) -> None:

        self.parsed_verses = parsed_verses
        data = {verse.text: [] for verse in self.parsed_verses}
        self.NdeN = data
        self.COPunN = data
        self.VunN = data
        self.NdeMat = data
        self.BodyPartdeN = data


    def get_NdeN(self) -> dict[str,list[str]]:
        """
        Highlights NdeN constructions
        """
        checker = Checker()

        for verse in self.parsed_verses:
            for token in verse[:-3]:
                constr = checker.is_NdeN(token, verse[token.i + 1], verse[token.i + 2], verse[token.i + 3])
                if constr[0]:
                    self.NdeN[verse.text].append(constr[1])
        
        self.NdeN = {k: v for k, v in self.NdeN.items() if v}

        return self.NdeN


    def get_COPunN(self) -> dict[str,list[str]]:
        """
        Highlights COPunN constructons
        """
        checker = Checker()

        for verse in self.parsed_verses:
            for token in verse[:-1]:
                constr = checker.is_COPunN(verse, token, verse[token.i + 1], token.head)
                if constr[0]:
                    self.COPunN[verse.text].append(constr[1])
        
        self.COPunN = {k: v for k, v in self.COPunN.items() if v}

        return self.COPunN


    def get_VunN(self) -> dict[str,list[str]]:
        """
        Highlights VunN constructons
        """
        checker = Checker()

        for verse in self.parsed_verses:
            for token in verse[:-1]:
                constr = checker.is_VunN(verse, token, verse[token.i + 1], verse[token.i + 1].head)
                if constr[0]:
                    self.VunN[verse.text].append(constr[1])
        
        self.VunN = {k: v for k, v in self.VunN.items() if v}

        return self.VunN


    def get_NdeMat(self) -> dict[str,list[str]]:
        """
        Highlights NdeMat constructons
        """
        checker = Checker()

        for verse in self.parsed_verses:
            for token in verse[:-2]:
                constr = checker.is_NdeMat(token, verse[token.i + 1], verse[token.i + 2])
                if constr[0]:
                    self.NdeMat[verse.text].append(constr[1])

        self.NdeMat = {k: v for k, v in self.NdeMat.items() if v}

        return self.NdeMat
    

    def get_BodyPartdeN(self):

        checker = Checker()

        for verse in self.parsed_verses:
            for token in verse[:-3]:
                constr = checker.is_BodyPartdeN(token, 
                                                verse[token.i + 1], 
                                                verse[token.i + 2], 
                                                verse[token.i + 3])
                if constr[0]:
                    self.BodyPartdeN[verse.text].append(constr[1])

        self.BodyPartdeN = {k: v for k, v in self.BodyPartdeN.items() if v}

        return self.BodyPartdeN