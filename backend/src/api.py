import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.route('/')
def get_start():
    return jsonify({'message': 'hello world'})

# db_drop_and_create_all()


"""
GET /drinks
public endpoint
---
parameters:
  no parameters
responses:
  200:
    List of all drinks
    schema:
    json array
      'success': True,
      'drinks': drink.short()
"""


@app.route('/drinks')
def get_short_drinks():
    drinks = Drink.query.all()
    json_drinks = []
    if len(drinks) == 0:
        json_drinks.append({
            'drinks': 'Empty List',
        })
        return jsonify({
            'success': True,
            'drinks': json_drinks
        })

    for drink in drinks:
        drink = drink.short()
        json_drinks.append(drink)

    return jsonify({
        'success': True,
        'drinks': json_drinks
    })


"""
GET /drinks-detail
require the 'get:drinks-detail' permission
---
parameters:
  no parameters
responses:
  200:
    List of all drinks with details
    schema:
    json array
      'success': True,
      'drinks': drink.long()
"""


@app.route('/drinks-detail')
@requires_auth(['get:drink-details'])
def get_long_drinks(jwt):
    drinks = Drink.query.all()
    json_drinks = []
    if len(drinks) == 0:
        json_drinks.append({
            'drinks': 'Empty List',
        })
        return jsonify({
            'success': True,
            'drinks': json_drinks
        })

    for drink in drinks:
        drink = drink.long()
        json_drinks.append(drink)
    return jsonify({
        'success': True,
        'drinks': json_drinks
    })


"""
POST /drinks
require the 'post:drinks' permission
---
parameters:
  no parameters
responses:
  200:
    create a new row in the drinks table
    schema:
    json array
      'success': True,
      'drinks': drink.long()
"""


# {
# "title": "matcha shake",
# "recipe": {
#  {"name": "milk",
#     "color": "grey",
#     "parts": 1
#      },
#      {
#      "name": "matcha",
#       "color": "green",
#         "parts": 3
#        },
#       }
# }
@app.route('/drinks', methods=['POST'])
@requires_auth(['create:drinks'])
def add_drink(jwt):
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    new_recipe = json.dumps(new_recipe)
    try:
        if not new_title or not new_recipe:
            abort(422)
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        drink = drink.long()
        return jsonify({
          'success': True,
          'drinks': drink
          })
    except Exception:
        abort(422)


"""
PATCH /drinks/<id>
require the 'patch:drinks' permission
---
parameters:
  id : is the existing model id
responses:
  400:
    if <id> is not found
  200:
    update the corresponding row for <id>
    schema:
    json array
      'success': True,
      'drinks': drink.long()
"""


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(['edit:drinks'])
def edit_drink_title(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    title = body.get("title", None)
    drink.title = title
    drink.update()
    json_drink = []
    json_drink.append(drink.long())
    return jsonify({
        'success': True,
        'drinks': json_drink
    })


"""
DELETE /drinks/<id>
require the 'delete:drinks' permission
---
parameters:
  id : is the existing model id
responses:
  400:
    if <id> is not found
  200:
    delete the corresponding row for <id>
    schema:
    json array
      'success': True,
      'drinks': drink.long()
"""


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth(['delete:drinks'])
def delete_drink(jwt, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        })
    except Exception:
        abort(422)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401


@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden Access"
    }), 403
