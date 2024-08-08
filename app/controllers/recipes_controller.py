from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Recipe
from app import db
from app.data.links import links

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/')
@login_required
def recipes_list():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return render_template('recipes.html', title='Recipes List', recipes=recipes, links=links)

@recipes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_recipe():
    if request.method == 'POST':
        # handle form submission
        new_recipe = Recipe(
            name=request.form['name'],
            servings=request.form['servings'],
            prep_time=request.form['prep_time'],
            cook_time=request.form['cook_time'],
            ingredients=request.form['ingredients'],
            method=request.form['method'],
            user_id=current_user.id
        )
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('recipes.recipes_list'))
    return render_template('recipe_create.html', title='Create a Recipe')

@recipes_bp.route('/<int:recipe_id>')
@login_required
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', title=f'Recipe: {recipe.name}', recipe=recipe)

@recipes_bp.route('/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if request.method == 'POST':
        # handle form submission
        recipe.name = request.form['name']
        recipe.servings = request.form['servings']
        recipe.prep_time = request.form['prep_time']
        recipe.cook_time = request.form['cook_time']
        recipe.ingredients = request.form['ingredients']
        recipe.method = request.form['method']
        db.session.commit()
        return redirect(url_for('recipes.recipe_detail', recipe_id=recipe.id))
    return render_template('recipe_edit.html', title=f'Edit Recipe: {recipe.name}', recipe=recipe)

@recipes_bp.route('/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('recipes.recipes_list'))