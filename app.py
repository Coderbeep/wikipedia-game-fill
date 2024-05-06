from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
import click
from . import create_app
from models import Progress

app_data = {
    "name": "Peter's Starter Template for a Flask Web App",
    "description": "A basic Flask app using bootstrap for layout",
    "author": "Peter Simeth",
    "html_title": "Peter's Starter Template for a Flask Web App",
    "project_name": "Starter Template",
    "keywords": "flask, webapp, template, basic",
}

app = create_app()

@app.route("/service", methods=['GET', 'POST'])
def service():
    display_text = "The quick brown fox jumps over the lazy dog.".split()  # Your text goes here
    if request.method == 'POST':
        words = request.form.get('wordInput', '').split()  # Get words from form input

        guessed_word = ""
        
        for word_obj in display_text:
            if word_obj.lower() in words:
                guessed_word = word_obj
        
        if guessed_word:
            existing_word = Progress.query.filter_by(word=guessed_word).first()
            if not existing_word:
                new_word = Progress(word=guessed_word)
                db.session.add(new_word)
                db.session.commit()
                guessed_words.add(guessed_word)
                print('Word added to database', flush=True)
            else:
                print('Word already exists', flush=True)

        
        response = make_response(render_template("service.html", app_data=app_data, display_text=display_text, guessed_words=guessed_words))
        return response
    if request.method == 'GET':
        return render_template("service.html", app_data=app_data, display_text=display_text, guessed_words=guessed_words)
    
    
