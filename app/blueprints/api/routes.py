from flask import request
from app import db
from . import api
from app.models import User
from .auth import basic_auth, token_auth


@api.route('/token')
@basic_auth.login_required
def index():
    user = basic_auth.current_user()
    token = user.get_token()
    return {'token': token, 'token_exp': user.token_expiration}


# Endpoint to get a user by their ID
@api.route('/users/<user_id>', methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return {'error': f'User with the ID of {user_id} does not exist.'}, 404
    return user.to_dict()


# Endpoint to create a new user
@api.route('/users', methods=["POST"])
def create_user():
    # Check to see that the request body is JSON aka application/json content-type
    if not request.is_json:
        return {'error': 'Your request content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate that all of the required fields are present
    required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    # Get the data from the request body
    first = data.get('first_name')
    last = data.get('last_name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    # Check to see if there is already a user with that username and/or email
    check_user = db.session.execute(db.select(User).filter((User.username == username) | (User.email == email))).scalars().all()
    if check_user:
        return {'error': 'User with that username and/or email already exists'}, 400
    # Create a new user instance with the request data
    new_user = User(first_name=first, last_name=last, email=email, username=username, password=password)
    return new_user.to_dict(), 201
