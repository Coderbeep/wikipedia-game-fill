from flask import render_template, request, jsonify
from .wiki_guess import WikipediaPage
import jinja2

from . import main
from .. import db
from ..models import Progress

# TODO: remove cookies somehow

page = WikipediaPage()
# page.get_random_article()

title = [x.word for x in page.title]
print(title, flush=True)
        

@main.route("/add_word", methods=['POST'])
def add_word():
    if not request.form['word']:
        return jsonify({'status': 'error'}),   400
    
    word = request.form['word'].strip().split()[0].lower()
    word = ''.join([x for x in word if x.isalnum()])
    
    if word:
        return jsonify({'status': 'added',
                        'result': page.get_word_result(word),
                        'word': word}),   200
        
    return jsonify({'status': 'error'}),   400


@main.route("/service", methods=['GET'])
def service():
    guessed_words = set()  # Fetch guessed words from the database
    page.reset_guessed()
    game_data = {'num_total': len([word for word in page.text if word.word not in page.delimiters]),
                 'num_guessed': 0}
    return render_template("service.html", display_title=page.title, 
                                            display_text=page.pars, 
                                            guessed_words=guessed_words,
                                            game_data=game_data)