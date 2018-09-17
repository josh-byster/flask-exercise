
# pytest automatically injects fixtures
# that are defined in conftest.py
# in this case, client is injected
def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json["result"]["content"] == "hello world!"


def test_mirror(client):
    res = client.get("/mirror/Tim")
    assert res.status_code == 200
    assert res.json["result"]["name"] == "Tim"


def test_get_users(client):
    res = client.get("/users")
    assert res.status_code == 200

    res_users = res.json["result"]["users"]
    assert len(res_users) == 4
    assert res_users[0]["name"] == "Aria"


def tests_get_users_with_team(client):
    res = client.get("/users?team=LWB")
    assert res.status_code == 200

    res_users = res.json["result"]["users"]
    assert len(res_users) == 2
    assert res_users[1]["name"] == "Tim"


def test_get_user_id(client):
    res = client.get("/users/1")
    assert res.status_code == 200

    res_user = res.json["result"]["user"]
    assert res_user["name"] == "Aria"
    assert res_user["age"] == 19


# Adds a new user to the database
def test_add_new_user(client):
    res = client.post("/users?team=LWB&name=Josh&age=19")
    assert res.status_code == 201

    res_user = res.json["result"]["user"]
    assert res_user["name"] == "Josh"
    assert res_user["age"] == 19
    assert res_user["team"] == "LWB"


# Checks that the new user is listed when querying teams
def test_new_user_on_team(client):
    res = client.get("/users?team=LWB")
    assert res.status_code == 200

    res_users = res.json["result"]["users"]
    assert len(res_users) == 3
    assert res_users[2]["name"] == "Josh"


# Test to make sure that now the user count is 5
def test_get_users_after_add(client):
    res = client.get("/users")
    assert res.status_code == 200

    res_users = res.json["result"]["users"]
    assert len(res_users) == 5
    assert res_users[4]["name"] == "Josh"


# Test that the we get a 422 response if not all parameters are in the request
def test_add_invalid_user(client):
    res = client.post("/users?team=LWB&name=Josh")
    assert res.status_code == 422


# Update a user record and check it gives a valid response
def test_put_user(client):
    res = client.put("/users/2?team=FAR")
    assert res.status_code == 200


# Test that the PUT request above persisted to the database
def test_put_persists(client):
    res = client.get("/users")

    res_users = res.json["result"]["users"]
    assert len(res_users) == 5
    assert res_users[1]["team"] == "FAR"


# Attempt to update a user id that doesn't exist
def test_put_invalid_user(client):
    res = client.put("/users/9?team=FAR")
    assert res.status_code == 404


# Test that we can delete a user in our database
def test_delete_user(client):
    res = client.delete("/users/1")
    assert res.status_code == 200

    get_res = client.get("/users")

    res_users = get_res.json["result"]["users"]
    assert len(res_users) == 4
    assert res_users[0]["id"] == 2


# Ensure that we don't raise an exception if we try deleting an invalid user
# and that we didn't delete another user unintentionally
def test_delete_invalid_user(client):
    res = client.delete("/users/9")
    assert res.status_code == 404

    get_res = client.get("/users")

    res_users = get_res.json["result"]["users"]
    assert len(res_users) == 4
