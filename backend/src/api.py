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

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
  return response

@app.route('/')
def get_start():
    return jsonify({
    'message':'hello world'
      })
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_short_drinks():
    drinks = Drink.query.all()

    if len(drinks) == 0 :
        abort(404)

    json_drinks = [];
    for drink in drinks:
        drink=drink.short()
        json_drinks.append(drink);

    return jsonify({
        'success': True,
        'drinks': json_drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(['get:drink-details'])
def get_long_drinks(jwt):

    drinks = Drink.query.all()
    if len(drinks) == 0 :
        abort(404)

    json_drinks = [];
    for drink in drinks:
        drink=drink.long()
        json_drinks.append(drink);


    return jsonify({
        'success': True,
        'drinks': json_drinks
    })
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
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
    new_title =body.get('title',None)
    new_recipe =body.get('recipe',None)
    new_recipe=json.dumps(new_recipe)

    try:
        if not new_title or not new_recipe:
            abort(422)
        drink=Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        drink=drink.long()

        return jsonify({
          'success':True,
          'drinks': drink
          })
    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@requires_auth(['edit:drinks'])
@app.route('/drinks/<int:id>', methods=['PATCH'])
def edit_drink_title(id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    title = body.get("title", None)
    drink.title = title
    drink.update()
    json_drink=drink.long()
    return jsonify({
    'success': True,
    'drinks': json_drink
     })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@requires_auth(['patch:drinks'])
@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drink(id):
      try:
         drink= Drink.query.filter(Drink.id == id).one_or_none()
         if drink is None:
              abort(404)
         drink.delete()

         return jsonify({
          'success': True,
          'delete':drink.id,
         })
      except:
          abort(422)
## Error Handling
'''
Example error handling for unprocessable entity
'''

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

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
