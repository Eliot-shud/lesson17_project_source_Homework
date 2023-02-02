# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

""" вызов API, работа через неймспейсы"""
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


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

#----------------------Сериализация моделей-----------------------------------------------

class DirectorSchema(Schema):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()
    director_name = fields.Pluck(DirectorSchema, "name")
    genre_name = fields.Pluck(GenreSchema, "name")


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

#----------------------Movies views---------------------------------


@movie_ns.route('/')
class MoviesViews(Resource):

    def get(self):
        query_movies = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            query_movies = query_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            query_movies = query_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(query_movies.all()), 200


    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "User Created", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):

    def get(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "User not found", 404
        return movie_schema.dump(movie), 200

    def put(self, uid: int):
        up_rows = db.session.query(Movie).filter(Movie.id == uid).update(request.json)

        if up_rows != 1:
            return "update rows", 400

        db.session.commit()

        return "", 204

    def delete(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "User not found", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204

#----------------------------Director views--------------------------------------

@director_ns.route('/')
class DirectorsViews(Resource):

    def get(self):
        all_directors = db.session.query(Director)
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        db.session.add(new_director)
        db.session.commit()
        return "Director created", 201


@director_ns.route('/<int:uid>')
class DirectorsViews(Resource):

    def get(self, uid: int):
        try:
            director = Director.query.get(Director).get(uid)
            return director_schema.dump(director), 200
        except Exception:
            return str(Exception), 404

    def put(self, uid: int):
        director = Director.query.get(Director).get(uid)
        req_json = request.json
        if "name" in req_json:
            director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        director = db.session.query(Director).get(uid)
        if not director:
            return "Director not found", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204

#-------------------------Genre views----------------------------------

@genre_ns.route('/')
class GenreViews(Resource):

    def get(self):
        all_genres = db.session.query(Genre)
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)

        db.session.add(new_genre)
        db.session.commit()
        return "Genre created", 201


@genre_ns.route('/<int:uid>')
class GenresViews(Resource):

    def get(self, uid: int):
        try:
            genre = Genre.query.get(Genre).get(uid)
            return genre_schema.dump(genre), 200
        except Exception:
            return str(Exception), 404

    def put(self, uid: int):
        genre = Genre.query.get(Genre).get(uid)
        req_json = request.json
        if "name" in req_json:
            genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "Genre not found", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204



if __name__ == '__main__':
    app.run(debug=True)
