from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Recipe
from app import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/recipes', methods=['GET'])
@login_required
def get_all_recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return jsonify([recipe.to_dict() for recipe in recipes])

@api_bp.route('/recipes/<int:recipe_id>', methods=['GET'])
@login_required
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe.to_dict())

@api_bp.route('/recipes', methods=['POST'])
@login_required
def create_recipe():
    data = request.get_json()
    new_recipe = Recipe(
        name=data['name'],
        servings=data.get('servings'),
        prep_time=data.get('prep_time'),
        cook_time=data.get('cook_time'),
        ingredients=data['ingredients'],
        method=data['method'],
        user_id=current_user.id
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify(new_recipe.to_dict()), 201

@api_bp.route('/recipes/<int:recipe_id>', methods=['PUT'])
@login_required
def update_recipe(recipe_id):
    data = request.get_json()
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.name = data['name']
    recipe.servings = data.get('servings')
    recipe.prep_time = data.get('prep_time')
    recipe.cook_time = data.get('cook_time')
    recipe.ingredients = data['ingredients']
    recipe.method = data['method']
    db.session.commit()
    return jsonify(recipe.to_dict())

@api_bp.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    return '', 204