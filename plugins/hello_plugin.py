from flask import Blueprint

# Register blueprint correctly
hello_blueprint = Blueprint('hello_blueprint', __name__)

@hello_blueprint.route('/hello')
def hello_view():
    return 'Hello from HelloView'

def init_app(app):
    print(f"Registering hello_blueprint with app...")
    app.register_blueprint(hello_blueprint)
