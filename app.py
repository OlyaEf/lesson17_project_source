# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from create_data import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# Готовим схему для сериализации и десериализации через маршмалоу
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


# Экзепляры MovieSchema для сер-ции и дес-ции в единственном объекте и во множественных объектах.
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

# Устанавливаем Flask-RESTX. Создаем объект API и CBV для обработки GET-запроса
api = Api(app)
movies_ns = api.namespace('movies')


# Роуты со значениями под наши сущности
@movies_ns.route('/')
class MovieView(Resource):
    """
    Возвращает список всех фильмов, разделенный по страницам.
    """
    def get(self):
        try:
            movies = db.session.query(Movie).all()
            return movies_schema.dump(movies), 200
        except Exception as e:
            return str(e), 404


@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    """
    Возвращает подробную информацию о фильме.
    """
    def get(self, uid: int):
        try:
            movies = db.session.query(Movie).get(uid)
            return movie_schema.dump(movies), 200
        except Exception as e:
            return str(e), 404


@movies_ns.route('/')
class MovieView(Resource):
    """
    Возвращает:
     - только фильмы с определенным режиссером по запросу типа /movies/?director_id=1;
     - только фильмы определенного жанра  по запросу типа /movies/?genre_id=1.
    """
    def get(self):
        dir_id = request.values.get('director_id')
        gen_id = request.values.get('genre_id')
        if dir_id:
            try:
                movies_by_director = db.session.query(Movie).filter(Movie.director_id == dir_id).all()
                return movies_schema.dump(movies_by_director), 200
            except Exception as e:
                return str(e), 404
        if gen_id:
            try:
                movies_by_genre = db.session.query(Movie).filter(Movie.genre_id == gen_id).all()
                return movies_schema.dump(movies_by_genre), 200
            except Exception as e:
                return str(e), 404


@movies_ns.route('/')
class MovieView(Resource):
    """
    Возвращает только фильмы с определенным режиссером и жанром по запросу типа /movies/?director_id=2&genre_id=4.
    """
    def get(self):
        dir_id = request.args.get('director_id')
        gen_id = request.args.get('genre_id')
        if dir_id and gen_id:
            try:
                movies_by_dir_gen = db.session.query(Movie).filter(Movie.director_id == dir_id, Movie.genre_id == gen_id).all()
                return movies_schema.dump(movies_by_dir_gen), 200
            except Exception as e:
                return str(e), 404


@movies_ns.route('/', methods=['POST'])
class MovieView(Resource):
    """
    Добавьте реализацию методов `POST` для режиссера.
    Добавьте реализацию методов `PUT` для режиссера.
    Добавьте реализацию методов `DELETE` для режиссера.
    """
    def post(self):
        directors = request.json
        new_directors = Movie(**directors)
        with db.session.begin():
            db.session.add(new_directors)
        return '', 201


if __name__ == '__main__':
    app.run(debug=True)
