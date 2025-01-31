from flask import request, jsonify
from server.models import Role
from server import db
from server.apis.utils import serialize
from server.utils import connect_to_database

def add_role():
    try:
        # get json data from client
        form_data = request.get_json()
        name = form_data.get('name')

        # validate and refine data
        # save to database
        role = Role(name=name)
        db = connect_to_database()
        db.session.add(role)
        db.session.commit()

        serialized_data = serialize(role)
        return jsonify(serialized_data), 201

    except Exception as error:
        print(error)
        return "add role error"
    

def get_roles(id=None):
    try:
        db = connect_to_database()
        if id is not None:
            # Retrieve a specific role by ID
            role = Role.query.get(id)
            if role is not None:
                serialized_data = serialize(role)
                return jsonify(serialized_data), 200
            else:
                return jsonify({"error": "Role not found"}), 404
        else:
            # Retrieve all roles
            roles = Role.query.all()

            if len(roles) < 1:
                return [], 200
            
            serialized_data = serialize(roles)
            return jsonify(serialized_data), 200

    except Exception as error:
        print(error)
        return jsonify({"error": "Failed to retrieve roles"}), 500
    

def update_role(id):
    try:
        # Retrieve the existing role by id
        role = Role.query.get(id)

        # Check if the role exists
        if role is None:
            return jsonify({"error": "Role not found"}), 404

        # Extract the new name from the request JSON data
        data = request.get_json()
        new_name = data.get('name')

        # Update the name field if a new name is provided
        if new_name is not None:
            role.name = new_name

            # Commit the changes to the database
            db = connect_to_database()
            db.session.commit()

            # Serialize and return the updated role
            serialized_data = serialize(role)
            return jsonify(serialized_data), 200
        else:
            return jsonify({"error": "Invalid or missing 'name' field in the request"}), 400

    except Exception as error:
        print(error)
        return jsonify({"error": "Failed to update role"}), 500