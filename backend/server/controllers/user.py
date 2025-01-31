from flask import request, jsonify, session
from server import db
from server.models import User  # Import the User model
from server.apis.utils import serialize
from server.controllers.token import generate_token, is_expired

# Create a route to login a new user
def login_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not ((username or email) and password):
            return jsonify({"error": "Missing data"}), 400

        user = User.query.filter_by(email=email).first()

        if user is None or user.check_password(password) is False:
            return jsonify({"error": "Invalid credentials"}), 400
        
        serialized_data = serialize(user)

        # create session 
        session["user_id"] = serialized_data["user_id"]
        session["role_id"] = serialized_data["role_id"]
        session["username"] = serialized_data["username"]
        session["email"] = serialized_data["email"]
        session["verified"] = serialized_data["verified"]

        # delete password data
        del serialized_data["password_hash"]
        del serialized_data["role_id"]
        
        return jsonify(serialized_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# Create a route to create a new user
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not (username and email and password):
            return jsonify({"error": "Missing data"}), 400

        user = User(username=username, email=email, password=password, role_id=1)

        db.session.add(user)
        db.session.commit()

        token = generate_token(user_id=user.user_id)

        # send mail
        from server.apis.send_mail import send_email
        send_email(email_receiver=email, subject="Confirm Accout", body=f'Please confirm account if you want to use our services. http://localhost:3000/users/verify/{token.token}')

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# Create a route to retrieve all users
def get_users():
    users = User.query.all()
    serialized_data = serialize(users)

    for user in serialized_data:
        del user["password_hash"]
        del user["role_id"]

    return jsonify(serialized_data), 200



# Create a route to retrieve a specific user by ID
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    serialized_data = serialize(user)
    del serialized_data['password_hash']
    del serialized_data['role_id']

    return jsonify(serialized_data), 200


# Create a route to update a user by ID
def update_user(id):
    try:
        data = request.get_json()
        user = User.query.get(id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = user.set_password(data['password'])
        if 'role_id' in data:
            user.role_id = data['role_id']

        serialized_data = serialize(user)

        # update sessions
        session["user_id"] = serialized_data["user_id"]
        session["role_id"] = serialized_data["role_id"]
        session["username"] = serialized_data["username"]
        session["email"] = serialized_data["email"]
        session["verified"] = serialized_data["verified"]

        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# Create a route to retrieve a specific user by ID
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    serialized_data = serialize(user)
    del serialized_data['password_hash']
    del serialized_data['role_id']

    return jsonify(serialized_data), 200


# Create a route to verify user by token
def verify_user(token=None):
    try:
        if token is None:
            return jsonify({"error": "User not found"}), 404
        
        # check if token exists and it hasn't expired
        token = is_expired(token=token)
        
        user = User.query.get(token.user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.verified = True

        db.session.commit()

        serialized_data = serialize(user)

        # update sessions
        session["user_id"] = serialized_data["user_id"]
        session["role_id"] = serialized_data["role_id"]
        session["username"] = serialized_data["username"]
        session["email"] = serialized_data["email"]
        session["verified"] = serialized_data["verified"]

        return jsonify({"message": "User have been verified"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Create a route to logout user
def logout():
    # Clear the session
    session.clear()
    return jsonify({}), 200