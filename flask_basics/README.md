# Comprehenssive Flask Guide

[Flask](https://flask.palletsprojects.com/en/2.3.x/) is a Web Development microframework built by
[Pallets Projects](https://palletsprojects.com/) whose main purpose was to build microservices in
python in a simple and comprehenssive manner.

Its underlying dependencies are the following owned libraries:

-   [Wekzeug](https://werkzeug.palletsprojects.com/), Python WSGI _(web server gateway interfase)_ that
    handles the network layer of Flask application on top of HTTP/TCP.
-   [Jinja](https://jinja.palletsprojects.com/), HTML templating engine for Python.
-   [Click](https://click.palletsprojects.com/), helper library to create Command Line Interfaces.

---

## Features

1.  Initialization

        from flask import Flask

        app = Flask(__name__)

        if __name__ == "__main__":
            app.run(host="127.0.0.1", port="5000")

1.  Routing _([reference](https://flask.palletsprojects.com/en/2.2.x/api/#flask.Flask.route))_

    -   Simple routing

            @app.route("/endpoint", methods=[...])
                def handler():
                # Process incoming data or validate
                # that requester is allowed to consume

                return result

    -   Parametrized routing

        > Supported types: `str`, `int`, `uuid`, `float`, `path`

                @app.route("/endpoint/<string:item_uuid>", methods=["..."])
                    def handler(item_uuid: str = None):

                    result = process_item(item_uuid, ...)
                    # Process incoming data or validate
                    # that requester is allowed to consume

                    return result

    -   Mixed routing

            @app.route("/endpoint", methods=["..."])
            @app.route("/endpoint/<string:item_uuid>", methods=["..."])
            def handler(item_uuid: str = None):
                result = process_one_or_many(item_uuid)

                return result

1.  Request Data _([reference](https://flask.palletsprojects.com/en/2.2.x/api/#flask.Request))_

        from flask import request

    -   Body

        -   Generic byte string `request.get_data`

        -   JSON as dictionary `request.get_json`

    -   Query Parameters _(as byte string)_ `request.query_string`

        -   Decoding query string

                from urllib import parse

                raw_qs: bytes = request.query_string
                qs_dict: dict = parse.parse_qs(raw_qs.decode())

    -   Form data `request.form`

        -   Read value

                username = request.form["username"]

        -   Files

                memory_obj = request.form["file"]
                file_content = memory_obj.read()

1.  Request Session Management _([reference](https://flask.palletsprojects.com/en/1.1.x/api/#sessions))_

    -   Configure application

            app = Flask(__name__)
            app.config.update({
                SECRET_KEY = "..."
            })

    -   Implementation sample

            from flask import Flask, session
            from uuid import uuid4

            app = Flask(__name__)
            app.config.update({
                SECRET_KEY = "..."
            })

            app.route("/")
            def handler():
                # Initializes a session UUID
                session["uuid"] = str(uuid4())
                result = service()
                return result

            def service(**kwargs):
                # Tracks and process the session UUID
                req_uuid = session["uuid"]
                return f"Request Identifier: {req_uuid}"

1.  Responses `jsonify`, `abort`

    -   Simple Responses

            from flask import jsonify

            app.route("/")
            def handler():
                response = jsonify(msg="sucess")
                response.status_code = 200
                return response

    -   Error Responses _[reference](https://flask.palletsprojects.com/en/2.2.x/api/#flask.abort)_

            from flask import jsonify, abort

            app.route("/")
            def handler():
                response = jsonify(msg="error")
                err.status_code = 500
                return abort(err)

    -   Redirects _([reference](https://flask.palletsprojects.com/en/2.2.x/api/#flask.redirect))_

            from flask import redirect

            app.route("/github")
            def handler():
                location = "https://github.com"
                return redirect(location)

1.  Blueprints _([reference](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Blueprint))_

    This feature allows to enhance routing and resource modularization across Flask applications.

    -   Blueprint definition

            # This is in: project/routes/default_route.py
            from flask import Blueprint

            router = Blueprint("router_name", __name__)

            @router.route(""):
            def handler():
                return "Hello world"

    -   Blueprint registration

            from flask import Flask
            from routes.default_route import router as default_router

            app = Flask(__name__)

            # Resource binding
            app.register_blueprint(default_router, url_prefix="default")

1.  Rendering

    -   Statics

        Setting up static files such as Javascript, CSS, and images resources requires to create
        a folder named `static` in the root path of the Flask application and refer to them
        through the `url_for` function within the `href`, e.g.

                <html>
                  <link rel="stylesheet" href="{{ url_for("static", filename="index.css") }}">
                  <script href="{{ url_for("static", filename="index.js") }}"></script>
                </html>

    -   Templates

        This feature allows to return preformatted HTML files that can handle dynamic
        values.

        It is required to have a `/templates` folder in the root of the application to
        allow the Flask instance to access them via file name, e.g.:

        -   Template:

                <!-- This is at: /templates/hello.html -->
                <html>
                  <script>
                    alert("Hello world {{ name }}");
                  </script>
                </html>

        -   Template binding:

                from flask import Flask, render_template

                app = Flask(__name__)

                @app.route("/")
                @app.route("/<string:name>")
                def handler(name: str = "unknown"):
                    return render_template("hello.html", name=name)

                if __name__ == "__main__":
                    app.run(debug=True)

    -   Conditional Template Rendering:

        -   Same template from above applying conditional statements:

                <html>
                  <script>
                    {% if name %}
                      alert("Hello world {{ name }}!");
                    {% else %}
                      alert("Hello world!");
                  </script>
                </html>

1.  Middlewares

    As it is important to build applications that provide full visibility or control request lifecycles,
    Flask app instances provide a series of middleware-oriented decorators that can be configured
    to listen requests **before reaching controllers** and **after response has been sent**, which can
    help in the following cases:

    -   Protect private resources
    -   Initialize request session logger references
    -   Redirect requests calling deprecated APIs
    -   etc...

    For example, the following middleware intends to redirect traffic trying to consume deprecated
    APIs and redirecting them to the proper one:

        from flask import redirect, request, abort


        def redirect_outdated_api_calls(
            app: Flask,
            deprecated_eps: list[str],
            redirects: dict
        ):
            """
            ::param app: Flask
                app = Flask(__name__)
                redirect_outdated_api_calls(app, ...)

            ::param deprecated_eps
                example: ["settings", "configurations", "..."]

            ::param redirects
                example: {
                    "settings": "v2/settings",
                    "configurations": "/app-configs",
                    ...
                }
            """
            @app.before_request
            def handler():
                ep = request.endpoint
                if ep in deprecated_eps:
                    location = redirect.get(ep)

                    if location:
                        return redirect(location)
                    return abort(code=404)

1.  Testing with pytest _([reference](https://flask.palletsprojects.com/en/2.2.x/testing/))_

    -   Fixture

            import pytest
            from app import app

            @pytest.fixture
            def client():
                return app.test_client()

    -   Test case

            import pytest
            from fixtures import client

            def test_get_request(client):
                response = client.get("/")

                assert response.status_code == 200
                assert response.is_json
                assert response.get_json() == dict(msg="success")

## Extensions

-   [FlaskREST+](https://flask-restplus.readthedocs.io/en/stable/)
-   [Flask-Mashmallow](https://flask-marshmallow.readthedocs.io/en/latest/)
-   [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/)
-   [Authlib / Flask OAuth Client](https://docs.authlib.org/en/latest/client/flask.html)

## Resources:

-   [Main documentation](https://flask.palletsprojects.com/en/2.3.x/)
