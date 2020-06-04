from google.cloud import datastore
from flask import Flask, request, make_response, render_template
import json
import constants
import secrets
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth import crypt
from google.auth import jwt
from google.auth.transport import requests

app = Flask(__name__)
client = datastore.Client()

CLIENT_ID = secrets.secretID
CLIENT_SECRET = secrets.secret
REDIRECT_URL = 'https://randhagufin.appspot.com/userInfo'


# These let us get basic info to identify a user and not much else
# they are part of the Google People API
scope = ['https://www.googleapis.com/auth/userinfo.email',
         'https://www.googleapis.com/auth/userinfo.profile', 'openid']
oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URL,
                      scope=scope)


@app.route('/')
def index():
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        # access_type and prompt are Google specific extra
        # parameters.
        access_type="offline", prompt="select_account")
    return render_template('index.html', url=authorization_url)

@app.route('/boats', methods=['POST', 'GET'])
def boat_get_post():
    if request.method == 'POST' and request.is_json == True:
        content = request.get_json()
        new_boat = datastore.entity.Entity(key=client.key(constants.boat))

        # Verifies attributes aren't missing
        try:
            req = requests.Request()
            token = request.headers['authorization']
            token = token[len("Bearer "):]
            id_info = id_token.verify_oauth2_token(
                token, req, CLIENT_ID)

                #Creates new boat if attributes are valid
            if "name" in content and "type" in content and "length" in content:
                new_boat.update({"name": content["name"], "type": content["type"],
                                "length": content["length"], "owner": id_info["sub"]})
                client.put(new_boat)
                selfstr = request.url + "/" + str(new_boat.id)
                new_boat["self"] = selfstr
                new_boat["id"] = new_boat.key.id
                boatInfo = json.dumps(new_boat)
                return (boatInfo, 201)
            else:
                response = '{"Error":"One or more of the required attributes are missing"}'
                return (response, 400)
        except ValueError:
            response = '{"Error":"The JWT token is missing or invalid"}'
            return (response, 401)
        except KeyError:
            response = '{"Error": "There was an issue with authorization"}'
            return (response, 401)

    #Retrieves paginated list of boats. Limit 5 per page.
    elif request.method == 'GET' and 'application/json' in request.accept_mimetypes:
        query = client.query(kind=constants.boat)
        rawResults = list(query.fetch())
        q_limit = int(request.args.get('limit', '5'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))

        #Generates link for next page in list
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + \
                str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        #Makes sure only loads that exist are still on boats
        for e in rawResults:
            if "loads" in e.keys():
                loadQuery = client.query(kind=constants.load)
                loadResults = list(loadQuery.fetch())
                exists = False
                for l in loadResults:
                    for item in e["loads"]:
                        if item["id"] == l.key.id:
                            exists = True

                if exists == False:
                    del e["loads"]
                    client.put(e)

        for e in results:
            e["id"] = e.key.id
            selfstr = request.base_url + "/" + str(e.key.id)
            e["self"] = selfstr

        output = {"boats": results, "count": len(list(query.fetch()))}
        if next_url:
            output["next"] = next_url
        return (json.dumps(output), 200)

    elif request.method == 'GET' and 'application/json' not in request.accept_mimetypes:
        response = '{"Error": The GET method of the root boat URL only allows for JSON content to be sent}'
        return (response, 406)

    elif request.method == 'DELETE' or request.method == 'PUT':
        response = '{"Error": The DELETE and PUT methods are not allowed at the root boat url}'
        return (response, 405)

    else:
        response = '{"Error": The method is not recognized or allowed}'
        return (response, 400)

#Retrieves list of boats owned by a user
@app.route('/users/<id>/boats', methods=['GET'])
def usersGet(id):
    if request.method == 'GET' and 'application/json' in request.accept_mimetypes:
        req = requests.Request()
        token = request.headers['authorization']
        token = token[len("Bearer "):]
        try:
            id_info = id_token.verify_oauth2_token(
                token, req, CLIENT_ID)
            if id_info["sub"] == id:
                query = client.query(kind=constants.boat)
                results = list(query.fetch())
                boatInfo = []
                for e in results:
                    if id == e["owner"]:
                        selfstr = request.url_root + "/" + str(e.key.id)
                        e['self'] = selfstr
                        e['id'] = e.key.id
                        boatInfo.append(json.dumps(e))
                return(str(boatInfo), 200)
            else:
                response = '{"Error":"The JWT token is invalid"}'
                return (response, 401)
        except ValueError:
            response = '{"Error":"The JWT token is missing or invalid"}'
            return (response, 401)
    elif request.method == 'GET' and 'application/json' not in request.accept_mimetypes:
        response = '{"Error": "The header must accept application/json"}'
        return (response, 406)
    else:
        response = '{"Error": "Method not allowed or recognized"}'
        return (response, 400)


@app.route('/boats/<id>', methods=['DELETE', 'GET', 'PUT', 'PATCH'])
def singleBoatMethods(id):
    #Only deletes boats owned by authorized user
    if request.method == 'DELETE':
        try:
            req = requests.Request()
            token = request.headers['authorization']
            token = token[len("Bearer "):]

            id_info = id_token.verify_oauth2_token(
                token, req, CLIENT_ID)
            key = client.key(constants.boat, int(id))
            boat = client.get(key=key)
            if boat:
                if id_info["sub"] == boat["owner"]:
                    client.delete(key)
                    return ('', 204)
                else:
                    response = '{"Error":"The provided JWT does not own the boat"}'
                    return(response, 403)
            else:
                response = '{"Error":"No boat with this boat_id exists"}'
                return(response, 403)
        except:
            response = '{"Error":"The JWT token is missing or invalid"}'
            return (response, 401)

    #Retrieves information regarding specific boat
    elif request.method == 'GET' and "application/json" in request.accept_mimetypes:
        content = request.get_json()
        boat_key = client.key(constants.boat, int(id))
        boat = client.get(key=boat_key)

        # Verifies boat with id exists
        if boat:
            if "loads" in boat:
                query = client.query(kind=constants.load)
                results = list(query.fetch())
                exists = False

                for e in results:
                    if e.key.id == boat["loads"][0]:
                        exists = True
                if exists == False:
                    del boat["loads"]
                    client.put(boat)

            selfstr = request.url
            boat["self"] = selfstr
            boat["id"] = int(id)
            boatInfo = json.dumps(boat)
            return(boatInfo, 200)
        else:
            response = '{"Error":"No boat with this boat_id exists"}'
            return(response, 404)

    #Allows authorized user to modify all attributes of owned boat
    elif request.method == 'PUT' and request.is_json == True:
        try:
            content = request.get_json()
            req = requests.Request()
            token = request.headers['authorization']
            token = token[len("Bearer "):]
            id_info = id_token.verify_oauth2_token(
                token, req, CLIENT_ID)
            key = client.key(constants.boat, int(id))
            boat = client.get(key=key)

            if id_info["sub"] == boat["owner"]:
                if 'id' in content:
                    response = '{"Error": "Object id is immutable"}'
                    return (response, 400)

                # Verifies attributes aren't missing
                if 'name' in content and 'type' in content and 'length' in content:
                    boat_key = client.key(constants.boat, int(id))
                    boat = client.get(key=boat_key)

                    # Verifies boat with id exists, and if so, makes sure name is unique, but allows boat to update to same name
                    if boat:
                        boat.update({"name": content["name"], "type": content["type"],
                                     "length": content["length"]})
                        client.put(boat)
                        selfstr = request.url
                        boat["self"] = selfstr
                        boat["id"] = int(id)
                        boatInfo = make_response(json.dumps(boat))
                        boatInfo.headers.set("Location", selfstr)
                        return (boatInfo, 303)

                    else:
                        response = '{"Error":"No boat with this boat_id exists"}'
                        return (response, 404)
                else:
                    response = '{"Error":"The request object is missing at least one of the required attributes"}'
                    return(response, 400)
            else:
                response = '{"Error":"The provided JWT does not own the boat"}'
                return(response, 403)
        except:
            response = '{"Error":"The JWT token is missing or invalid"}'
            return (response, 401)

    #Allows authorized user to modify any number of attributes of owned boat
    elif request.method == 'PATCH' and request.is_json == True:
        try:
            content = request.get_json()
            req = requests.Request()
            token = request.headers['authorization']
            token = token[len("Bearer "):]
            id_info = id_token.verify_oauth2_token(
                token, req, CLIENT_ID)
            boat_key = client.key(constants.boat, int(id))
            boat = client.get(key=boat_key)

            if id_info["sub"] == boat["owner"]:
                if 'id' in content:
                    response = '{"Error": "Object id is immutable"}'
                    return (response, 400)

                # Verifies boat with id exists
                if boat:
                    if 'name' in content:
                        boat["name"] = content["name"]
                        client.put(boat)

                    if 'type' in content:
                        boat["type"] = content["type"]
                        client.put(boat)

                    if 'length' in content:
                        boat["length"] = content["length"]
                        client.put(boat)

                    selfstr = request.url
                    boat["self"] = selfstr
                    boat["id"] = int(id)
                    boatInfo = json.dumps(boat)
                    return (boatInfo, 200)
                else:
                    response = '{"Error":"No boat with this boat_id exists"}'
                    return (response, 404)
            else:
                response = '{"Error":"The provided JWT does not own the boat"}'
                return(response, 403)
        except:
            response = '{"Error":"The JWT token is missing or invalid"}'
            return (response, 401)

    else:
        response = '{"Error": The method is not recognized or allowed}'
        return (response, 400)


@app.route('/loads', methods=['POST', 'GET'])
def load_get_post():
    if request.method == 'POST' and request.is_json == True:
        content = request.get_json()
        new_load = datastore.entity.Entity(key=client.key(constants.load))

        # Verifies attributes aren't missing
        if 'weight' in content and 'content' in content and 'transport' in content:
            new_load.update(
                {"weight": content["weight"], "content": content["content"], "transport": content["transport"]})
            client.put(new_load)
            selfstr = request.url + "/" + str(new_load.id)
            new_load["self"] = selfstr
            new_load["id"] = new_load.key.id
            loadInfo = json.dumps(new_load)
            return (loadInfo, 201)
        else:
            response = '{"Error":"The request object is missing the required number"}'
            return (response, 400)

    #Retrieves paginated list of all loads
    elif request.method == 'GET' and 'application/json' in request.accept_mimetypes:
        query = client.query(kind=constants.load)
        q_limit = int(request.args.get('limit', '5'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))

        #Generates links between pages
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + \
                str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        for e in results:
            e["id"] = e.key.id
            selfstr = request.base_url + "/" + str(e.key.id)
            e["self"] = selfstr

        output = {"loads": results, "count": len(list(query.fetch()))}
        if next_url:
            output["next"] = next_url
        return (json.dumps(output), 200)

    elif request.method == 'GET' and 'application/json' not in request.accept_mimetypes:
        response = '{"Error": The GET method of the root load URL only allows for JSON content to be sent}'
        return (response, 406)

    elif request.method == 'DELETE' or request.method == 'PUT':
        response = '{"Error": The DELETE and PUT methods are not allowed at the root load url}'
        return (response, 405)

    else:
        response = '{"Error": The method is not recognized or allowed}'
        return (response, 400)


@app.route('/loads/<id>', methods=['DELETE', 'GET', 'PUT', 'PATCH'])
def singleLoadMethods(id):
    if request.method == 'DELETE':
        key = client.key(constants.load, int(id))
        load = client.get(key=key)
        if load:
            client.delete(key)
            return ('', 204)
        else:
            response = '{"Error":"No load with this load_id exists"}'
            return(response, 404)

    elif request.method == 'GET' and "application/json" in request.accept_mimetypes:
        content = request.get_json()
        load_key = client.key(constants.load, int(id))
        load = client.get(key=load_key)

        # Verifies load with id exists
        if load:
            selfstr = request.url
            load["self"] = selfstr
            load["id"] = int(id)
            loadInfo = json.dumps(load)
            return(loadInfo, 200)
        else:
            response = '{"Error":"No load with this load_id exists"}'
            return(response, 404)

    elif request.method == 'PUT' and request.is_json == True:
        content = request.get_json()

        if 'id' in content:
            response = '{"Error": "Object id is immutable"}'
            return (response, 400)

        # Verifies attributes aren't missing
        if 'weight' in content and 'content' in content and 'transport' in content:
            load_key = client.key(constants.load, int(id))
            load = client.get(key=load_key)

            if load:
                load.update({"weight": content["weight"], "content": content["content"],
                             "transport": content["transport"]})
                client.put(load)
                selfstr = request.url
                load["self"] = selfstr
                load["id"] = int(id)
                loadInfo = make_response(json.dumps(load))
                loadInfo.headers.set("Location", selfstr)
                return (loadInfo, 303)

            else:
                response = '{"Error":"No load with this load_id exists"}'
                return (response, 404)
        else:
            response = '{"Error":"The request object is missing at least one of the required attributes"}'
            return(response, 400)

    elif request.method == 'PATCH' and request.is_json == True:
        content = request.get_json()

        if 'id' in content:
            response = '{"Error": "Object id is immutable"}'
            return (response, 400)

        load_key = client.key(constants.load, int(id))
        load = client.get(key=load_key)

        # Verifies load with id exists
        if load:
            if 'weight' in content:
                load["weight"] = content["weight"]
                client.put(load)

            if 'content' in content:
                load["content"] = content["content"]
                client.put(load)

            if 'transport' in content:
                load["transport"] = content["transport"]
                client.put(load)

            selfstr = request.url
            load["self"] = selfstr
            load["id"] = int(id)
            loadInfo = json.dumps(load)
            return (loadInfo, 200)

    else:
        response = '{"Error": The method is not recognized or allowed}'
        return (response, 400)


@app.route('/marinas', methods=['POST', 'GET'])
def marina_get_post():
    if request.method == 'POST' and request.is_json == True:
        content = request.get_json()
        new_marina = datastore.entity.Entity(key=client.key(constants.marina))

        # Verifies attributes aren't missing
        if 'name' in content and 'location' in content and 'leisure' in content:
            new_marina.update(
                {"name": content["name"], "location": content["location"], "leisure": content["leisure"]})
            client.put(new_marina)
            selfstr = request.url + "/" + str(new_marina.id)
            new_marina["self"] = selfstr
            new_marina["id"] = new_marina.key.id
            marinaInfo = json.dumps(new_marina)
            return (marinaInfo, 201)
        else:
            response = '{"Error":"The request object is missing the required number"}'
            return (response, 400)

    #Retrieves paginated list of marinas
    elif request.method == 'GET' and 'application/json' in request.accept_mimetypes:
        query = client.query(kind=constants.marina)
        q_limit = int(request.args.get('limit', '5'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))

        #Generates links to next page
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + \
                str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        for e in results:
            e["id"] = e.key.id
            selfstr = request.base_url + "/" + str(e.key.id)
            e["self"] = selfstr

        output = {"marinas": results, "count": len(list(query.fetch()))}
        if next_url:
            output["next"] = next_url
        return (json.dumps(output), 200)

    elif request.method == 'GET' and 'application/json' not in request.accept_mimetypes:
        response = '{"Error": The GET method of the root marina URL only allows for JSON content to be sent}'
        return (response, 406)

    elif request.method == 'DELETE' or request.method == 'PUT':
        response = '{"Error": The DELETE and PUT methods are not allowed at the root marina url}'
        return (response, 405)

    else:
        response = '{"Error": The method is not recognized or allowed}'
        return (response, 400)


@app.route('/marinas/<id>', methods=['DELETE', 'GET', 'PUT', 'PATCH'])
def singleMarinaMethods(id):
    if request.method == 'DELETE':
        key = client.key(constants.marina, int(id))
        marina = client.get(key=key)
        if marina:
            client.delete(key)
            return ('', 204)
        else:
            response = '{"Error":"No marina with this marina_id exists"}'
            return(response, 404)

    elif request.method == 'GET' and "application/json" in request.accept_mimetypes:
        content = request.get_json()
        marina_key = client.key(constants.marina, int(id))
        marina = client.get(key=marina_key)

        # Verifies marina with id exists
        if marina:
            selfstr = request.url
            marina["self"] = selfstr
            marina["id"] = int(id)
            marinaInfo = json.dumps(marina)
            return(marinaInfo, 200)
        else:
            response = '{"Error":"No marina with this marina_id exists"}'
            return(response, 404)

    elif request.method == 'PUT' and request.is_json == True:
        content = request.get_json()

        if 'id' in content:
            response = '{"Error": "Object id is immutable"}'
            return (response, 400)

        # Verifies attributes aren't missing
        if 'name' in content and 'location' in content and 'leisure' in content:
            marina_key = client.key(constants.marina, int(id))
            marina = client.get(key=marina_key)

            if marina:
                marina.update({"name": content["name"], "location": content["location"],
                               "leisure": content["leisure"]})
                client.put(marina)
                selfstr = request.url
                marina["self"] = selfstr
                marina["id"] = int(id)
                marinaInfo = make_response(json.dumps(marina))
                marinaInfo.headers.set("Location", selfstr)
                return (marinaInfo, 303)

            else:
                response = '{"Error":"No marina with this marina_id exists"}'
                return (response, 404)
        else:
            response = '{"Error":"The request object is missing at least one of the required attributes"}'
            return(response, 400)

    elif request.method == 'PATCH' and request.is_json == True:
        content = request.get_json()

        if 'id' in content:
            response = '{"Error": "Object id is immutable"}'
            return (response, 400)

        marina_key = client.key(constants.marina, int(id))
        marina = client.get(key=marina_key)

        # Verifies marina with id exists
        if marina:
            if 'name' in content:
                marina["name"] = content["name"]
                client.put(marina)

            if 'location' in content:
                marina["location"] = content["location"]
                client.put(marina)

            if 'leisure' in content:
                marina["leisure"] = content["leisure"]
                client.put(marina)

            selfstr = request.url
            marina["self"] = selfstr
            marina["id"] = int(id)
            marinaInfo = json.dumps(marina)
            return (marinaInfo, 200)

    else:
        response = '{"Error": The method is not recognized or allowed}'
        return (response, 400)

#Allows for the addition or removal of a load from a boat
@app.route('/boats/<bid>/loads/<lid>', methods=["PUT", "DELETE"])
def load_add_remove_load(lid, bid):
    if request.method == "PUT":
        load_key = client.key(constants.load, int(lid))
        load = client.get(key=load_key)
        boat_key = client.key(constants.boat, int(bid))
        boat = client.get(key=boat_key)

        if boat and load:
            lPayLoad = {"id": load.id, "content": load["content"], "self": request.url_root + "loads/" + str(load.id)}
            bPayLoad = {"id": boat.id, "name": boat['name'], "self": request.url_root + "boats/" + str(boat.id)}

            if 'carrier' in load.keys():
                return('{"Error": "This load is already assigned to a ship"}', 403)
            else:
                boat['loads'] = [lPayLoad]
                load['carrier'] = [bPayLoad]
                client.put(boat)
                client.put(load)
                return('', 204)
        else:
            response = '{"Error":"This boat/load does not exist"}'
            return(response, 404)

    elif request.method == "DELETE":
        load_key = client.key(constants.load, int(lid))
        load = client.get(key=load_key)
        boat_key = client.key(constants.boat, int(bid))
        boat = client.get(key=boat_key)

        # Verifies that load and boat ids are valid
        if load and boat:
            if 'loads' in boat.keys():
                del boat['loads']
                client.put(boat)
            if 'carrier' in load.keys():
                del load['carrier']
                client.put(load)
            return('', 204)
        else:
            response = '{"Error":"No boat with this boat_id is at the load with this load_id"}'
            return(response, 404)

    else:
        return 'Method not recognized'

#Allows for the addition or removal of a boat from a marina
@app.route('/marinas/<mid>/boats/<bid>', methods=["PUT", "DELETE"])
def marina_add_remove_marina(mid, bid):
    if request.method == "PUT":
        marina_key = client.key(constants.marina, int(mid))
        marina = client.get(key=marina_key)
        boat_key = client.key(constants.boat, int(bid))
        boat = client.get(key=boat_key)

        if boat and marina:
            lPaymarina = {"id": marina.id, "self": request.url_root + "marina/" + str(marina.id)}
            bPaymarina = {"id": boat.id, "name": boat['name'], "self": request.url_root + "boats/" + str(boat.id)}

            if 'marina' in boat.keys():
                return('{"Error": "This boat is already in a marina"}', 403)
            else:
                boat['marina'] = [lPaymarina]
                marina['docked'] = [bPaymarina]
                client.put(boat)
                client.put(marina)
                return('', 204)
        else:
            response = '{"Error":"This boat/marina does not exist"}'
            return(response, 404)

    elif request.method == "DELETE":
        marina_key = client.key(constants.marina, int(mid))
        marina = client.get(key=marina_key)
        boat_key = client.key(constants.boat, int(bid))
        boat = client.get(key=boat_key)

        # Verifies that marina and boat ids are vamid
        if marina and boat:
            if 'marina' in boat.keys():
                del boat['marina']
                client.put(boat)
            if 'docked' in marina.keys():
                del marina['docked']
                client.put(marina)
            return('', 204)
        else:
            response = '{"Error":"No boat with this boat_id is at the marina with this marina_id"}'
            return(response, 404)

    else:
        return 'Method not recognized'


@app.route('/userInfo')
def userInfo():
    try:
        token = oauth.fetch_token(
            'https://accounts.google.com/o/oauth2/token',
            authorization_response=request.url,
            client_secret=CLIENT_SECRET)
        req = requests.Request()

        id_info = id_token.verify_oauth2_token(
            token['id_token'], req, CLIENT_ID)

        query = client.query(kind=constants.users)
        results = list(query.fetch())
        exists = False

        for e in results:
            if id_info['sub'] == e['sub']:
                exists = True

        if exists == False:
            new_user = datastore.entity.Entity(key=client.key(constants.users))
            new_user.update({"sub": id_info["sub"]})
            client.put(new_user)

        return render_template('userInfo.html', token=token['id_token'])
    except:
        return render_template('userInfo.html', token='The JWT is either missing or invalid')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
