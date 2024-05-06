from . import db

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(80), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Progress {self.word}>'
