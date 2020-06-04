## Intro

```
URL of Website and Login: https://randhagufin.appspot.com/
```
**Non-User Entities:**

```
Boats have names, lengths, and types.
```
```
Loads have weights, contents, and transports.
```
```
Marinas have names, locations, and leisure.
```
```
A boat can have multiple loads, but a load can only be on one boat. A marina can have
multiple boats, but a boat can only be at one marina.
```
User Entity:

The “sub” field is used to store unique identifiers for each user and it’s gathered from the
JWT provided by the Google API using OAUTH. Logging in allows a user to create boat

entities, edit them, delete them, and view each boat entity that they created. Since the sub field is

unique, it’s matched against the “owner” property of the boat entity to verify that only the correct

creator is able to modify or delete the boat.

In order to make an authenticated request, the Authorization header must include a valid

bearer token. In the case of viewing specific user created boats, the sub property must be

included as an id in the url.


## Create a Boat

Allows you to create a new boat.

```
POST /boats
```
Request

Request Parameters
**Name Type Description Required?**
Authorization Token JWT Bearer token Yes

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
name String The name of the boat. Yes
type String The type of the boat. E.g., Sailboat, Catamaran, etc. Yes
length Integer Length of the boat in feet. Yes
```
Request Body Example

```
{
"name": "Sea Witch",
"type": "Catamaran",
"length": 28
}
```
Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 201 Created
Failure 400 Bad Request
Failure 401 Unauthorized If the provided JWT token is missing or invalid, the
request is rejected.

_Success_
Status: 201 Created

```
{
"id": "abc123",
"name": "Sea Witch",
"type": "Catamaran",
"length": 28,
“owner”: 123,
"self": "https://<your-app>/boats/abc123"
}
```

_Failure_
Status: 400 Bad Request

```
{
"Error": "The request object is missing at least one of the required attributes"
}
```
_Failure_
Status: 40 1 Unauthorized

```
{
"Error": "The JWT token is missing or invalid"
}
```

## Get a Boat

Allows you to get an existing boat

```
GET /boats/:boat_id
```
Request

Request Parameters
**Name Type Description Required?**
boat_id String ID of the boat Yes
Accept Application/json Accept header must have ‘application/json’ Yes

Request Body
None

Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 200 OK
Failure 400 Bad Request Accept header must include application/json
Failure 404 Not Found No boat with this boat_id exists
```
Response Examples

_Success_
Status: 200 OK

```
{
"id": "abc123",
"name": "Sea Witch",
"type": "Catamaran",
"length": 28,
“owner”: 123,
"self": "https://<your-app>/boats/abc123"
}
```
_Failure_
Status: 404 Not Found

{
"Error": "No boat with this boat_id exists"
}
_Failure_
Status: 40 0 Bad Request

```
{
"Error": "The method is not recognized or allowed"
}
```

## List all Boats

List all the boats.

```
GET /boats
```
Request

Request Parameters
**Name Type Description Required?**
Accept Application/json Accept header must have ‘application/json’ Yes

Request Body
None

Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 200 OK
Failure 400 Bad Request Accept header must have ‘application/json’
```
Response Examples

_Success_
Status: 200 OK
[
{
"id": "abc123",
"name": "Sea Witch",
"type": "Catamaran",
"length": 28,
“owner”: 123,
"self": "https://<your-app>/boats/abc123"
},
{
"id": "def456",
"name": "Adventure",
"type": "Sailboat",
"length": 50 ,
“owner”: 456 ,
"self": "https://<your-app>/boats/def456"
}
]

_Failure_
Status: 40 0 Bad Request

```
{
"Error": "The method is not recognized or allowed"
}
```

## Put a Boat

Allows you to edit a boat.

```
PUT /boats/:boat_id
```
Request

Request Parameters
**Name Type Description Required?**
boat_id String ID of the boat Yes
Authorization Token JWT Bearer token Yes

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
name String The name of the boat. Yes
type String The type of the boat. E.g., Sailboat, Catamaran, etc. Yes
length Integer Length of the boat in feet. Yes
```
Request Body Example

```
{
"name": "Sea Witch",
"type": "Catamaran",
"length": 99
}
```
Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 20 0 OK
Failure 400 Bad Request One or more attributes are missing
Failure 404 Not Found No boat with this boat_id exists
Failure 401 Unauthorized Provided JWT is invalid or missing

_Success_
Status: 200 OK

```
{
"id": "abc123",
"name": "Sea Witch",
"type": "Catamaran",
"length": 99 ,
“owner”: 123,
"self": "https://<your-app>/boats/abc123"
```

### }

_Failure_
Status: 400 Bad Request

```
{
"Error": "The request object is missing at least one of the required attributes"
}
```
```
Status: 404 Not Found
```
{
"Error": "No boat with this boat_id exists"
}
_Failure_
Status: 40 1 Unauthorized

```
{
"Error": "The JWT token is missing or invalid"
}
```

## Patch a Boat

Allows you to edit a boat.

```
PATCH /boats/:boat_id
```
Request

Request Parameters
**Name Type Description Required?**
boat_id String ID of the boat Yes
Authorization Token JWT Bearer token Yes

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
name String The name of the boat. No
type String The type of the boat. E.g., Sailboat, Catamaran, etc. No
length Integer Length of the boat in feet. No
```
Request Body Example

```
{
"length": 99
}
```
Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 20 0 OK
Failure 404 Not Found No boat with this boat_id exists
Failure 401 Unauthorized Provided JWT is invalid or missing

_Success_
Status: 200 OK

```
{
"id": "abc123",
"name": "Sea Witch",
"type": "Catamaran",
"length": 99 ,
“owner”: 123,
"self": "https://<your-app>/boats/abc123"
}
```

_Failure_
Status: 404 Not Found

```
{
"Error": "No boat with this boat_id exists"
}
```
_Failure_
Status: 40 1 Unauthorized

```
{
"Error": "The JWT token is missing or invalid"
}
```

## Delete a Boat

Allows you to delete a boat. Note that if the boat is currently in a marina, deleting the boat makes the
marina empty.

```
DELETE /boats/:boat_id
```
Request

Request Parameters
**Name Type Description Required?**
Authorization Token JWT Bearer token Yes

Request Body
None

Response
No body

Response Body Format
Success: No body

Failure: JSON

Response Statuses

```
Outcome Status Code Notes
Success 20 4 No Content
Failure 404 Not Found No boat with this boat_id exists
Failure 401 Unauthorized Provided JWT is invalid or missing
```
Response Examples

_Success_
Status: 20 4 No Content

_Failure_
Status: 404 Not Found

```
{
"Error": "No boat with this boat_id exists"
}
```
_Failure_
Status: 40 1 Unauthorized

```
{
"Error": "The JWT token is missing or invalid"
}
```


## Create a Marina

Allows you to create a new marina.

```
POST /marinas
```
Request

Request Parameters
None

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
Name String The name of the marina. Yes
Location String The location of the marina. Yes
Leisure String Relaxing activities at the marina. Yes
```
Request Body Example
{
"name": "Turtle Cove",
"location": "Best Coast",
"leisure": "Snorkling"
}

Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 201 Created
Failure 400 Bad Request

Success
Status: 201 Created

```
{
"name": "Turtle Cove",
"location": "Best Coast",
"leisure": "Snorkling",
"self": "https://<your-app>/marinas/123abc"
}
```
_Failure_
Status: 400 Bad Request

```
{
```

"Error": "The request object is missing the required number"
}


## Get a Marina

Allows you to get an existing marina.

```
GET /marinas/:marina_id
```
Request

Request Parameters
**Name Type Description Required?**
marina_id String ID of the marina Yes
Accept Application/json Header must accept application/json Yes

Request Body
None

Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 200 OK
Failure 400 Bad Request Application/json missing from accept header
Failure 404 Not Found No marina with this marina_id exists
```
Response Examples

_Success_
Status: 200 OK

```
{
"name": "Turtle Cove",
"location": "Best Coast",
"leisure": "Snorkling",
"self": "https://<your-app>/marinas/123abc"
}
```
_Failure_
Status: 40 0 Bad Request

```
{
"Error": "The method is not recognized or allowed"
}
```
_Failure_
Status: 404 Not Found

```
{
"Error": "No marina with this marina_id exists"
}
```

## List all Marinas

List all the marinas.

```
GET /marinas
```
Request

Request Parameters
Accept header must include ‘application/json’

Request Body
None

Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 200 OK
Failure 406 Not Acceptable The method requires application/json to be accepted

Response Examples

_Success_
Status: 200 OK

```
[
{
"name": "Turtle Cove",
"location": "Best Coast",
"leisure": "Snorkling",
"self": "https://<your-app>/marinas/123abc"
},
{
"name": "Shallow Creek",
"location": "Worst Coast",
"leisure": "Digging",
"self": "https://<your-app>/marinas/turrible"
}
]
```
_Failure_
Status: 406 Not Acceptable

```
{
"Error":"The GET method of the root marina URL only allows for JSON content to be
sent"
}
```

## Put a Marina

Allows you to edit a boat.

```
PUT /marinas/:marina_id
```
Request

Request Parameters
**Name Type Description Required?**
marina_id String ID of the marina Yes

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
Name String The name of the marina. Yes
Location String The location of the marina. Yes
Leisure String Relaxing activities at the marina. Yes
```
Request Body Example

```
{
"name": “Ice Town”,
"location": "Indiana",
"leisure": "Roasts"
}
```
Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 20 0 OK
Failure 404 Not Found No marina with this marina_id exists

_Success_
Status: 200 OK
{
"name": "Ice Town",
"location": "Indiana",
"leisure": "Roasts"
}

_Failure_
Status: 404 Not Found

```
{
"Error": "No marina with this marina_id exists"
}
```

## Patch a Marina

Allows you to edit a boat.

```
PATCH /marinas/:marina_id
```
Request

Request Parameters
**Name Type Description Required?**
marina_id String ID of the marina Yes

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
Name String The name of the marina. No
Location String The location of the marina. No
Leisure String Relaxing activities at the marina. No
```
Request Body Example

```
{
"name": “Ice Town”
}
```
Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 20 0 OK
Failure 404 Not Found No marina with this marina_id exists
```
_Success_
Status: 200 OK
{
"name": "Ice Town",
"location": "Best Coast",
"leisure": "Snorkling"
}

_Failure_
Status: 404 Not Found

```
{
"Error": "No marina with this marina_id exists"
}
```

## Delete a Marina

Allows you to delete a marina. If the marina being deleted has a boat, the boat is now considered “at
sea.”

```
DELETE /marinas/:marina_id
```
Request

Request Parameters
None

Request Body
None

Response
No body

Response Body Format
Success: No body

Failure: JSON

Response Statuses
**Outcome Status Code Notes**
Success 204 No Content
Failure 404 Not Found No marina with this marina_id exists

Response Examples

_Success_
Status: 204 No Content

_Failure_
Status: 404 Not Found

```
{
"Error": "No marina with this marina_id exists"
}
```

## Boat Arrives at a Marina

Boat has arrived at a marina.

```
PUT /marinas/:marina_id/boats/:boat_id
```
Request

Request Parameters
None

Request Body
None

Response
No body

Response Body Format
Success: No body

Failure: JSON

Response Statuses
**Outcome Status Code Notes**
Success 204 No Content Succeeds only if a boat exists with this boat_id and a
marina exists with this marina_id.
Failure 403 Forbidden The boat is already in a marina.
Failure 404 Not Found No boat with this boat_id exists, and/or no marina with
this marina_id exits.

Response Examples

_Success_
Status: 204 No Content

_Failure_

```
Status: 403 Forbidden
```
```
{
"Error": "This boat is already in a marina."
}
```
```
Status: 404 Not Found
```
```
{
"Error": "The specified boat and/or marina don’t exist"
}
```

## Boat Departs a Marina

Boat has left the marina to go to sea. The marina is now empty.

```
DELETE /marinas/:marina_id/boats/:boat_id
```
Request

Request Parameters
None

Request Body
None

Response
No body

Response Body Format
Success: No body

Failure: JSON

Response Statuses
**Outcome Status Code Notes**
Success 204 No Content Succeeds only if a boat exists with this boat_id, a marina
exists with this marina_id and this boat is at this marina.
Failure 404 Not Found No boat with this boat_id is at the marina with this
marina_id.

Response Examples

_Success_
Status: 204 No Content

_Failure_
Status: 4 04 Not Found

```
{
"Error": "No boat with this boat_id is at the marina with this marina_id"
}
```

## Create a Load

Allows you to create a new Load.

```
POST /loads
```
Request

Request Parameters
None

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
Weight Integer The weight (in pounds) of the load. Yes
Content String The cargo being transported. Yes
Transport String Special handling types. Yes
```
Request Body Example
{
"weight": 2000,
"content": "candles",
"transport": "flammable"
}

Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 201 Created
Failure 400 Bad Request All attributes must be included

Success
Status: 201 Created

```
{
"weight": 2000,
"content": "candles",
"transport": "flammable"
"self": "https://<your-app>/loads/123abc"
}
```
_Failure_
Status: 400 Bad Request

```
{
```

"Error": "The request object is missing the required number"
}


## Get a Load

Allows you to get an existing load.

```
GET /loads/:load_id
```
Request

Request Parameters
**Name Type Description Required?**
load_id String ID of the load Yes
Accept Application/json Header must accept application/json Yes

Request Body
None

Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 200 OK
Failure 400 Bad Request Application/json missing from accept header
Failure 404 Not Found No load with this load_id exists
```
Response Examples

_Success_
Status: 200 OK

```
{
"weight": 2000,
"content": "candles",
"transport": "flammable"
"self": "https://<your-app>/loads/123abc"
}
```
_Failure_
Status: 40 0 Bad Request

```
{
"Error": "The method is not recognized or allowed"
}
```
_Failure_
Status: 404 Not Found

```
{
"Error": "No load with this load_id exists"
}
```

## List all Loads

List all the loads.

```
GET /loads
```
Request

Request Parameters
**Name Type Description Required?**
Accept Application/json Accept header must include application/json Yes

Request Body
None

Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 200 OK
Failure 406 Not Acceptable The method requires application/json to be accepted
```
Response Examples

_Success_
Status: 200 OK
[
{
"weight": 2000,
"content": "candles",
"transport": "flammable"
"self": "https://<your-app>/loads/123abc"
},
{
"weight": 5821 ,
"content": "ice cream",
"transport": "frozen"
"self": "https://<your-app>/loads/456def"
}
]

_Failure_
Status: 406 Not Acceptable

```
{
"Error":"The GET method of the root load URL only allows for JSON content to be
sent"
}
```

## Put a Load

Allows you to edit a boat.

```
PUT /loads/:load_id
```
Request

Request Parameters
**Name Type Description Required?**
load_id String ID of the load Yes

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
Weight Integer The weight (in pounds) of the load. Yes
Content String The cargo being transported. Yes
Transport String Special handling types. Yes
```
Request Body Example

```
{
"weight": 5821 ,
"content": "ice cream",
"transport": "frozen"
}
```
Response

Response Body Format
JSON

Response Statuses
**Outcome Status Code Notes**
Success 20 0 OK
Failure 404 Not Found No load with this load_id exists

_Success_
Status: 200 OK
{
"weight": 5821 ,
"content": "ice cream",
"transport": "frozen"
"self": "https://<your-app>/loads/123abc"
}

_Failure_
Status: 404 Not Found
{
"Error": "No load with this load_id exists"
}


## Patch a Load

Allows you to edit a boat.

```
PATCH /loads/:load_id
```
Request

Request Parameters
**Name Type Description Required?**
load_id String ID of the load Yes

Request Body
Required

Request Body Format
JSON

Request JSON Attributes

```
Name Type Description Required?
Weight Integer The weight (in pounds) of the load. No
Content String The cargo being transported. No
Transport String Special handling types. No
```
Request Body Example

```
{
"weight": 2
}
```
Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 20 0 OK
Failure 404 Not Found No load with this load_id exists
```
_Success_
Status: 200 OK
{
"weight": 2 ,
"content": "ice cream",
"transport": "frozen"
}

_Failure_
Status: 404 Not Found

```
{
"Error": "No load with this load_id exists"
}
```

## Delete a Load

Allows you to delete a load. If the load being deleted has a boat, the boat is now considered “at sea.”

```
DELETE /loads/:load_id
```
Request

Request Parameters
None

Request Body
None

Response
No body

Response Body Format
Success: No body

Failure: JSON

Response Statuses
**Outcome Status Code Notes**
Success 204 No Content
Failure 404 Not Found No load with this load_id exists

Response Examples

_Success_
Status: 204 No Content

_Failure_
Status: 404 Not Found

```
{
"Error": "No load with this load_id exists"
}
```

## Boat Picks up a Load

Boat has arrived at a load.

```
PUT /boats/:boat_id/loads/:load_id
```
Request

Request Parameters
None

Request Body
None

Note: You will need to set Content-Length to 0 in your request when calling out to this endpoint.

Response
No body

Response Body Format
Success: No body

Failure: JSON

Response Statuses
**Outcome Status Code Notes**
Success 204 No Content Succeeds only if a boat exists with this boat_id and a load
exists with this load_id.
Failure 403 Forbidden The load is already on a boat.
Failure 404 Not Found No boat with this boat_id exists, and/or no load with this
load_id exits.

Response Examples

_Success_
Status: 204 No Content

_Failure_

```
Status: 403 Forbidden
```
```
{
"Error": "This load is already on a boat."
}
```
```
Status: 404 Not Found
```
```
{
"Error": "The specified boat and/or load don’t exist"
}
```

## Boat Drops off a Load

Boat has left the load to go to sea. The load is now empty.

```
DELETE /boats/:boat_id/loads/:load_id
```
Request

Request Parameters
None

Request Body
None

Response
No body

Response Body Format
Success: No body

Failure: JSON

Response Statuses
**Outcome Status Code Notes**
Success 204 No Content Succeeds only if a boat exists with this boat_id, a load
exists with this load_id and this load is on this boat.
Failure 404 Not Found No boat with this boat_id is at the load with this load_id.

Response Examples

_Success_
Status: 204 No Content

_Failure_
Status: 4 04 Not Found

```
{
"Error": "No boat with this boat_id is at the load with this load_id"
}
```

## List all User-Specific Boats

List all the loads.

```
GET /users/:user_id/boats
```
Request

Request Parameters
**Name Type Description Required?**
Authorization Token JWT Bearer token Yes
Accept Application/json Accept header must include application/json Yes

Request Body
None

Response

Response Body Format
JSON

Response Statuses

```
Outcome Status Code Notes
Success 200 OK
Failure 401 Unauthorized The JWT token is missing or invalid
Failure 406 Not Acceptable The method requires application/json to be accepted
```
Response Examples

_Success_
Status: 200 OK
[
{
"weight": 2000,
"content": "candles",
"transport": "flammable",
“owner”: 123
"self": "https://<your-app>/loads/123abc"
},
{
"weight": 5821 ,
"content": "ice cream",
"transport": "frozen",
“owner”: 123,
"self": "https://<your-app>/loads/456def"
}
]

_Failure_
Status: 406 Not Acceptable

```
{
"Error”: “The header must accept application/json”
}
```

_Failure_
Status: 40 1 Unauthorized

```
{
"Error": "The JWT token is missing or invalid"
}
```
