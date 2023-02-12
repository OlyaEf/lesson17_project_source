# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

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
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# Экзепляры Schema для сер-ции и дес-ции в единственном объекте и во множественных объектах.
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# Устанавливаем Flask-RESTX. Создаем объект API и CBV для обработки GET-запроса
api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


# Роуты со значениями под наши сущности
@movies_ns.route('/')
class MovieView(Resource):
    """
    GET: Возвращает список всех фильмов, разделенный по страницам.
    Возвращает:
    - только фильмы с определенным режиссером по запросу типа /movies/?director_id=1;
    - только фильмы определенного жанра по запросу типа /movies/?genre_id=1.
    POST: Принимает новый movies в БД через метод POST
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
        movies = db.session.query(Movie).all()
        return movies_schema.dump(movies), 200

    def post(self):
        try:
            req_json = request.json
            new_movie = Movie(**req_json)
            db.session.add(new_movie)
            db.session.commit()
            return '', 201
        except Exception as e:
            return str(e), 404


@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    """
    GET: Возвращает подробную информацию о фильме.
    PUT: вносит изменение в фильм.
    DELETE: удаляет фильм.
    """
    def get(self, uid: int):
        try:
            movies = db.session.query(Movie).get(uid)
            return movie_schema.dump(movies), 200
        except Exception as e:
            return str(e), 404

    def put(self, uid: int):
        try:
            movie = db.session.query(Movie).get(uid)
            req_json = request.json
            movie.title = req_json.get('title')
            movie.description = req_json.get('description')
            movie.trailer = req_json.get('trailer')
            movie.year = req_json.get('year')
            movie.rating = req_json.get('rating')
            movie.genre_id = req_json.get('genre_id')
            movie.director_id = req_json.get('director_id')
            # если все прошло успешно, то выполняем добавление в нашу сессию
            db.session.add(movie)
            # коммит для сохранения изменений
            db.session.commit()
            # возвращаем пустую строчку и код 204 как ноу контент
            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, uid: int):  # Удаление записи
        # Вызываем запись по uid
        movie = db.session.query(Movie).get(uid)
        # Удаляем полученную запись
        db.session.delete(movie)
        # Сохраняем удаление
        db.session.commit()
        return '', 204


@directors_ns.route('/')
class DirectorView(Resource):
    """
    GET: Возвращает список всех режиссеров.
    POST: Добавляет реализацию методов POST для режиссера.
    """
    def get(self):
        try:
            directors = db.session.query(Director).all()
            return directors_schema.dump(directors), 200
        except Exception as e:
            return str(e), 404

    def post(self):
        try:
            req_json = request.json
            new_director = Director(**req_json)
            db.session.add(new_director)
            db.session.commit()
            return '', 201
        except Exception as e:
            return str(e), 404


@directors_ns.route('/<int:did>')
class DirectorView(Resource):
    """
    GET: Выводит режиссера по id.
    PUT: Добавляет реализацию методов PUT для режиссера.
    DELETE: Добавляет реализацию методов DELETE для режиссера.
    """
    def get(self, did: int):
        try:
            director = db.session.query(Director).get(did)
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, did: int):  # Замена записи
        try:
            director = db.session.query(Director).get(did)
            req_json = request.json
            director.name = req_json.get('name')
            db.session.add(director)
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, did: int):  # Удаление записи
        director = db.session.query(Director).get(did)
        db.session.delete(director)
        db.session.commit()
        return '', 204


@genres_ns.route('/')
class GenreView(Resource):
    """
    GET: Выводит всее жанры из БД.
    POST: Добавляет реализацию методов POST для жанра.
    """
    def get(self):
        try:
            genres = db.session.query(Genre).all()
            return genres_schema.dump(genres), 200
        except Exception as e:
            return str(e), 404

    def post(self):
        try:
            req_json = request.json
            new_genre = Genre(**req_json)
            db.session.add(new_genre)
            db.session.commit()
            return '', 201
        except Exception as e:
            return str(e), 404


@genres_ns.route('/<int:gid>')
class GenreView(Resource):
    """
    GET: Возвращает подробную информацию о фильме.
    PUT: Добавляет реализацию методов PUT для жанра.
    DELETE: Добавляет реализацию методов DELETE для жанра.
    """
    def get(self, gid: int):
        try:
            genre = db.session.query(Genre).get(gid)
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, gid: int):  # Замена записи
        try:
            genre = db.session.query(Genre).get(gid)
            req_json = request.json
            genre.name = req_json.get('name')
            db.session.add(genre)
            db.session.commit()
            return '', 204
        except Exception as e:
            return str(e), 404

    def delete(self, gid: int):  # Удаление записи
        genre = Genre.query.get(gid)
        db.session.delete(genre)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
