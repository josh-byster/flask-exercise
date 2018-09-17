from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)

@app.route("/users", methods = ["GET","POST"])
def user():
    if request.method == 'GET':
        team = request.args.get('team')
        if team is not None:
            return getUsersByTeam(team)
        else:
            # If no team specified as a query param, return all the users
            return getAllUsers()
    if request.method == 'POST':
        # Create a new user to update the DB
        return addUser(request.args.to_dict())

def getAllUsers():
    users = db.get("users")
    data = {"users": users}
    return create_response(data)

def getUsersByTeam(team):
    users_on_team = db.getByTeam("users",team)
    data = {"users": users_on_team}
    return create_response(data)

def addUser(user_data):
    if "name" in user_data and "age" in user_data and "team" in user_data:
        # Create the user since all the necessary fields exist
        user_data["age"] = int(user_data["age"])
        new_user = db.create("users",user_data)
        return create_response({"user":new_user},status=201)
    # Return an error otherwise    
    message = "Cannot create new user with missing parameters. Got name={0},age={1},team={2}".format(user_data.get("name"),user_data.get("age"),user_data.get("team"))
    return create_response(message=message,status=422)
    
def updateUser(user_id,update_values):
    if db.getById("users",int(user_id)) is not None:
        user_update = db.updateById("users",int(user_id),update_values)
        return create_response(user_update)
    else:
        message = "Cannot update user. id {0} is invalid.".format(user_id)
        return create_response(message=message,status=404)

def deleteUser(user_id):
    if db.getById("users",int(user_id)) is not None:
        db.deleteById("users",int(user_id))
        message = "Successfully deleted user with id={0}".format(user_id)
        return create_response(message=message)
    else:
        message = "Could not delete user with id={0}. The user was not found in the database.".format(user_id)
        return create_response(message=message,status=404)
    
@app.route("/users/<user_id>", methods = ["GET","PUT","DELETE"])
def userById(user_id):
    if request.method == "GET":
        data_for_user = db.getById("users",int(user_id))
        if data_for_user is not None:
            data = {"user": data_for_user}  
            return create_response(data)   
        else:
            data = {"message": "A user with id {0} was not found in the database.".format(user_id)}
            return create_response(data, status = 404)
    if request.method == "PUT":
        return updateUser(user_id,request.args.to_dict())
    if request.method == "DELETE":
        return deleteUser(user_id)


"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)
