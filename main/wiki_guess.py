import wikipediaapi
import inflect
import spacy
import re
from sentence_transformers import SentenceTransformer, util
from pyinflect import getAllInflections
import os

p = inflect.engine()
nlp = spacy.load('en_core_web_sm')

def split_abbreviation(string):
    return re.split(r'(?:(\d+)([a-zA-Z]+))', string)

def split_with_delimiters(delimiters, string):
    regex_pattern = '|'.join(map(re.escape, delimiters))
    string = re.sub(r'\[[^\]]*\]', '', string) # To remove the adnotations
    parts = re.findall(rf'(?:(?:[{regex_pattern}])|\b\w+\b)', string)

    final_parts = []
    for part in parts:
        final_parts.extend(split_abbreviation(part))
    return [part for part in final_parts if part]


def get_article_name():
    import random
    file_path = os.path.join(os.path.dirname(__file__), "list_of_articles.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        articles = file.readlines()
    return random.choice(articles).strip().replace(" ", "_")


class Word():
    def __init__(self, word, guessed = False) -> None:
        self.word : str = word
        self.guessed : bool = guessed
        self.most_similar_word: str = None
        self.most_similar_score: float = 0
    
    @staticmethod
    def get_conjugated_forms(word):
        other_forms = set()
        doc = nlp(word)
        if doc[0].pos_ == "VERB":
            forms = getAllInflections(word, pos_type="V")
            for key, value in forms.items():
                other_forms.add(value[0])
        elif word == 'be':
            for value in getAllInflections("be").values():
                other_forms.update(set(value))

        other_forms.add(p.plural(word))
        return other_forms
    
    def setGuessed(self, bool_value : bool = True) -> None:
        self.guessed = bool_value
        
    def update_similarity(self, word, score) -> bool:
        if score > self.most_similar_score:
            self.most_similar_score = score
            self.most_similar_word = word
            return True
        return False 
    
    def isdigit(self):
        return self.word.isdigit()
    
    def __len__(self):
        return len(self.word)
    
    def __str__(self) -> str:
        return self.word

class WikipediaPage():
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.delimiters = [" ", ",", ".","?", "!", ":", ";", 
                      "(", ")","{", "}", "<", ">", "-", "_", "–", "\"", "'"]

        wiki = wikipediaapi.Wikipedia('coolbot@example.org','en')
        self.page = wiki.page("Social_structure")
    
        self.title = split_with_delimiters(self.delimiters, self.page.title.replace("_", " "))
        self.paragraphs = WikipediaPage.split_into_paragraphs(self.page.summary)
        self.text = list()
        self.pars = list()
        
        self.title = [Word(x) if x not in self.delimiters else Word(x, True) for x in self.title]
        self.text.extend(self.title)
        
        for paragraph in self.paragraphs:
            splitted = split_with_delimiters(self.delimiters, paragraph)
            words = [Word(x) if x not in self.delimiters else Word(x, True) for x in splitted]
            self.pars.append(words)
            self.text.extend(words)
            
        self.embeddings = self.model.encode(list(map(str, self.text)), convert_to_tensor=True)
    
    @staticmethod
    def split_into_paragraphs(text: str):
        return re.split(r'(?<=\.)(?=[A-Z])|\n', text)
    
    def get_random_article(self):
        wiki = wikipediaapi.Wikipedia('Wikiguess wikiguess@example.org', 'en')
        while True:
            self.page = wiki.page(get_article_name())
            if self.page.exists():
                break
        self.title = split_with_delimiters(self.delimiters, self.page.title.replace("_", " "))
        self.paragraphs = WikipediaPage.split_into_paragraphs(self.page.summary)
        self.text = list()
        self.pars = list()
        
        self.title = [Word(x) if x not in self.delimiters else Word(x, True) for x in self.title]
        self.text.extend(self.title)
        
        for paragraph in self.paragraphs:
            splitted = split_with_delimiters(self.delimiters, paragraph)
            words = [Word(x) if x not in self.delimiters else Word(x, True) for x in splitted]
            self.pars.append(words)
            self.text.extend(words)
        
        self.embeddings = self.model.encode(list(map(str, self.text)), convert_to_tensor=True)
    
    def reset_guessed(self) -> None:
        for word in self.text:
            if word.word not in self.delimiters:
                word.setGuessed(False)
            word.most_similar_score = 0
            word.most_similar_word = None
    
    def get_word_result(self, word: str) -> dict:
        if word.isdigit():
            return self.get_word_result_number(int(word))
        return self.get_word_result_letters(word)
    
    def get_word_result_letters(self, word: str) -> dict:
        user_word_embed = self.model.encode([word], convert_to_tensor=True)
        cosine_score = util.cos_sim(user_word_embed, self.embeddings)
        
        other_forms = Word.get_conjugated_forms(word)
        result = dict()
        
        for i, text_word in enumerate(self.text):
            if text_word.guessed or text_word.isdigit():
                continue
            if cosine_score[0][i].item() > 0.999 or text_word.word.lower() in other_forms:
                result[i] = text_word.word
                text_word.setGuessed() 
                continue
            if cosine_score[0][i].item() > 0.55:
                if text_word.update_similarity(word, float(cosine_score[0][i].item())):
                    result[i] = round(cosine_score[0][i].item(), 2)
                continue
        print(result, flush=True)
        return result
    
    def get_word_result_number(self, word: str) -> dict:
        result = dict()
        
        for i, text_word in enumerate(self.text):
            if text_word.guessed or not text_word.isdigit():
                continue
            if word == text_word.word or abs(word - int(text_word.word)) == 0:
                result[i] = text_word.word
                text_word.setGuessed()
                continue
            if len(text_word) == len(str(word)) and text_word.update_similarity(word, 10 / abs(word - int(text_word.word))):
                result[i] = float(10 / abs(word - int(text_word.word)))
        print(result, flush=True)
        return result
        
    
    def display_article(self):
        for paragraph in self.pars:
            print("".join([str(x) for x in paragraph]))
            print()
    
if __name__ == "__main__":
    # wiki = WikipediaPage()
    delimiters = [" ", ",", ".","?", "!", ":", ";", 
                      "(", ")","{", "}", "<", ">", "-", "_", "–", "\"", "'"]
    text = "The expense of resources during the Roman–Persian Wars ultimately proved catastrophic for both empires. The prolonged and escalating warfare of the 6th and 7th centuries left them exhausted and vulnerable in the face of the sudden emergence and expansion of the Rashidun Caliphate, whose forces invaded both empires only a few years after the end of the last Roman–Persian war. Benefiting from their weakened condition, the Rashidun armies swiftly conquered the entire Sasanian Empire, and deprived the Eastern Roman Empire of its territories in the Levant, the Caucasus, Egypt, and the rest of North Africa. Over the following centuries, more of the Eastern Roman Empire came under Muslim rule."

    
    splitted = split_with_delimiters(delimiters, text)
    for x in splitted:
        print(len(x), x)