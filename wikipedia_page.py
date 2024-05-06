import wikipediaapi
import os
from rich import print
import re
from sentence_transformers import SentenceTransformer, util
import spacy
from pyinflect import getAllInflections
import inflect

# Idea:
# 1. Get the pluaral form of the word (noun)
# 2. Something is wrong with the paragraph (to reproduce, run Computer_science page on wikipedia. first sentence of the second paragraph is in the first paragraph )

p = inflect.engine()
nlp = spacy.load('en_core_web_sm')

def get_conjugated_forms(word):
    other_forms = set()
    doc = nlp(word)
    if doc[0].pos_ == "VERB":
        forms = getAllInflections(word, pos_type="V")
        for key, value in forms.items():
            other_forms.add(value[0])

    other_forms.add(p.plural(word))
    
    return other_forms
        
model = SentenceTransformer('all-MiniLM-L6-v2')
        
def split(delimiters, string, maxsplit=0):
    import re
    regex_pattern = '|'.join(map(re.escape, delimiters))
    string_without_brackets = re.sub(r'\[[^\]]*\]', '', string) # To remove the adnotations
    splitted = re.split(regex_pattern, string_without_brackets, maxsplit)
    return [x for x in splitted if x]

def split_with_delimiters(delimiters, string):
    regex_pattern = '|'.join(map(re.escape, delimiters))
    string = re.sub(r'\[[^\]]*\]', '', string) # To remove the adnotations
    return re.findall(rf'(?:(?:[{regex_pattern}])|\b\w+\b)', string)



class WikipediaPage():
    def __init__(self):
        delimiters = [" ", ",", ".","?", "!", ":", ";", 
                      "(", ")","{", "}", "<", ">", "-", "_", "–", "\"", "'"]

        wiki = wikipediaapi.Wikipedia('coolbot@example.org','en')
        self.page = wiki.page("Computer_science")
        
        self.paragraphs = self.page.summary.split("\n")
        self.text = list()
        self.pars = list()
        
        for paragraph in self.paragraphs:
            splitted = split_with_delimiters(delimiters, paragraph)
            words = [Word(x) if x not in delimiters else Word(x, True) for x in splitted]
            self.pars.append(words)
            self.text.extend(words)
            
        self.embeddings = model.encode(list(map(str, self.text)), convert_to_tensor=True)
    
    def display_article(self):
        for paragraph in self.pars:
            print("".join([str(x) for x in paragraph]))
            print()
    
    
class Word():
    def __init__(self, word, guessed = False):
        self.word : str = word
        self.guessed : bool = guessed
        self.most_similar_word : str = None
        self.most_similar_score : float = 0.
    
    def update_similarity(self, word, score):
        if self.most_similar_score < score:
            self.most_similar_score = score
            self.most_similar_word = word
    
    def setGuessed(self, bool_value : bool = True):
        self.guessed = bool_value
    
    def __str__(self):
        return self.word
    
    def __repr__(self):
        if self.guessed:
            return f"[green]{self.word}[/green]"
        elif self.most_similar_word:
            return f"[yellow]{self.most_similar_word}[{str(len(self.word))}][/yellow]"
        else:
            return "_"*len(self.word)
        


if __name__ == '__main__':
    page = WikipediaPage()

    page.display_article()
    # print(page.page.summary)
    
    # while True:
    #     user_word = input()
    #     embedded = model.encode([user_word], convert_to_tensor = True)
    #     cosine_score = util.cos_sim(embedded, page.embeddings)

    #     other_forms = get_conjugated_forms(user_word)
        
    #     for i, word in enumerate(page.text):
    #         if word.guessed:
    #             continue
    #         if cosine_score[0][i].item() > 0.999 or word.word.lower() in other_forms:
    #             word.setGuessed()
    #             continue
    #         if cosine_score[0][i].item() > 0.65:
    #             word.update_similarity(user_word, cosine_score[0][i].item())
    #             continue
        
    #     os.system('cls')
    #     page.display_article()