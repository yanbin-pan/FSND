import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db_refresh, setup_db, Actor, Movie
from flask_moment import Moment
from flask_migrate import Migrate
from auth import AuthError, requires_auth

AUTH0_DOMAIN = "fsnd-udacity-21.eu.auth0.com"
ALGORITHMS = ["RS256"]
API_AUDIENCE = "casting-agency"
CLIENT_ID = "y9Elth7FXI11Ec9UnbtxndfWd9Rly3TI"
CALLBACK_URL = "http://127.0.0.1:8080"

ROWS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    moment = Moment(app)
    setup_db(app)

    # CORS configuration
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    def paginate_results(request, selection):
        """Paginates and formats database queries
        Parameters:
        * <HTTP object> request, that may contain a "page" value
        * <database selection> selection of objects, queried from database

        Returns:
        * <list> list of dictionaries of objects, max. 10 objects
        """
        # Get page from request. If not given, default to 1
        page = request.args.get("page", 1, type=int)

        # Calculate start and end slicing
        start = (page - 1) * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE

        # Format selection into list of dicts and return sliced
        objects_formatted = [object_name.format() for object_name in selection]
        return objects_formatted[start:end]

    # -----------------------------------------
    # API ENDPOINTS
    # -----------------------------------------
    @app.route("/auth/url", methods=["GET"])
    def generate_auth_url():
        url = (
            f"https://{AUTH0_DOMAIN}/authorize"
            f"?audience={API_AUDIENCE}"
            f"&response_type=token&client_id="
            f"{CLIENT_ID}&redirect_uri="
            f"{CALLBACK_URL}"
        )
        return jsonify({"url": url})

    """Defining the /actors endpoints GET/POST/DELETE/PATCH"""

    def get_error_message(error, default_text):
        """Returns default error text or custom error message (if not applicable)
        *Input:
            * <error> system generated error message which contains a description message
            * <string> default text to be used as error message if Error has no specific message
        *Output:
            * <string> specific error message or default text(if no specific message is given)
        """
        try:
            # Return message contained in error, if possible
            return error.description["message"]
        except:
            # otherwise, return given default text
            return default_text

    # TODO include auth decorator
    @app.route("/actors", methods=["GET"])
    @requires_auth("read:actors")
    def get_actors(payload):
        """query the actors stored in the database"""

        actors = Actor.query.all()
        paginated_actors = paginate_results(request, actors)

        if len(paginated_actors) == 0:
            abort(404, {"message": "no actors found in database."})

        return jsonify({"success": True, "actors": paginated_actors})

    @app.route("/actors", methods=["POST"])
    @requires_auth("create:actors")
    def post_actors(payload):
        """insert a new actor in the db"""

        body = request.get_json()

        if not body:
            abort(400, {"message": "request does not contain a valid JSON body."})

        # extract the paramters from the request  body
        name = body.get("name", None)
        gender = body.get("gender", None)
        age = body.get("age", None)

        # abort if either parameter is not provided
        if not name:
            abort(422, {"message": "no name provided."})

        if not age:
            abort(422, {"message": "no age provided."})

        new_actor = Actor(name=name, gender=gender, age=age)
        new_actor.insert()

        return jsonify({"success": True, "created": new_actor.id})

    @app.route("/actors/<actor_id>", methods=["PATCH"])
    @requires_auth("edit:actors")
    def patch_actors(payload, actor_id):
        body = request.get_json()

        if not actor_id:
            abort(400, {"message": "add an actor id to the URL"})

        if not body:
            abort(400, {"message": "request body does not have a valid message"})

        # identify actor that needs editing
        actor_edit = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if not actor_edit:
            abort(404, {"message": "Actor with id:{} not found".format(actor_id)})

        # extract parameters from the request body
        name = body.get("name", actor_edit.name)
        gender = body.get("gender", actor_edit.gender)
        age = body.get("age", actor_edit.age)

        actor_edit.name = name
        actor_edit.gender = gender
        actor_edit.age = age

        actor_edit.update()

        return jsonify(
            {"success": True, "updated": actor_edit.id, "actor": [actor_edit.format()]}
        )

    @app.route("/actors/<actor_id>", methods=["DELETE"])
    @requires_auth("delete:actors")
    def delete_actor(payload, actor_id):
        if not actor_id:
            abort(400, {"message": "append the actor id to the URL request"})

        # indentify the actor to delete
        del_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        # if not match throw an error
        if not del_actor:
            abort(404, {"message": "actor not found"})

        del_actor.delete()

        return {"success": True, "deleted": actor_id}

    # -----------------------------------------
    # API ENDPOINTS
    # -----------------------------------------
    """Defining the /movies endpoints GET/POST/DELETE/PATCH"""

    @app.route("/movies", methods=["GET"])
    @requires_auth("read:movies")
    def get_movies(payload):
        """query the movies stored in the database"""

        movies = Movie.query.all()
        paginated_movies = paginate_results(request, movies)

        if len(paginated_movies) == 0:
            abort(404, {"message": "no movies found in database."})

        return jsonify({"success": True, "movies": paginated_movies})

    @app.route("/movies", methods=["POST"])
    @requires_auth("create:movies")
    def post_movies(payload):
        """insert a new movie in the db"""

        body = request.get_json()

        if not body:
            abort(400, {"message": "request does not contain a valid JSON body."})

        # extract the paramters from the request  body
        title = body.get("title", None)
        release_date = body.get("release_date", None)

        # abort if either parameter is not provided
        if not title:
            abort(422, {"message": "no title provided."})

        if not release_date:
            abort(422, {"message": "no release_date provided."})

        new_movie = Movie(title=title, release_date=release_date)
        new_movie.insert()

        return jsonify({"success": True, "created": new_movie.id})

    @app.route("/movies/<movie_id>", methods=["PATCH"])
    @requires_auth("edit:movies")
    def patch_movies(payload, movie_id):
        body = request.get_json()

        if not movie_id:
            abort(400, {"message": "add an movie id to the URL"})

        if not body:
            abort(400, {"message": "request body does not have a valid message"})

        # identify movie that needs editing
        movie_edit = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if not movie_edit:
            abort(404, {"message": "movie with id:{} not found".format(movie_id)})

        # extract parameters from the request body
        title = body.get("title", movie_edit.name)
        release_date = body.get("release_date", movie_edit.gender)

        movie_edit.title = title
        movie_edit.release_date = release_date

        movie_edit.update()

        return jsonify(
            {"success": True, "updated": movie_edit.id, "movie": [movie_edit.format()]}
        )

    @app.route("/movies/<movie_id>", methods=["DELETE"])
    @requires_auth("delete:movies")
    def delete_movie(payload, movie_id):
        if not movie_id:
            abort(400, {"message": "append the movie id to the URL request"})

        # indentify the movie to delete
        del_movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        # if not match throw an error
        if not del_movie:
            abort(404, {"message": "movie not found"})

        del_movie.delete()

        return {"success": True, "deleted": movie_id}

    # -----------------------------------------
    # ERRORS HANDLERS ENDPOINTS
    # -----------------------------------------
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 422,
                    "message": get_error_message(error, "unprocessable"),
                }
            ),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": get_error_message(error, "bad request"),
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def resource_not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": get_error_message(error, "resource not found"),
                }
            ),
            404,
        )

    @app.errorhandler(AuthError)
    def authentification_failed(AuthError):
        return (
            jsonify(
                {
                    "success": False,
                    "error": AuthError.status_code,
                    "message": AuthError.error["description"],
                }
            ),
            AuthError.status_code,
        )

    # After every endpoint has been created, return app
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
