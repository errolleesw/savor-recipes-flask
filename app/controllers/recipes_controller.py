# app/controllers/recipes_controller.py
import json
import re
import urllib.parse
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import Recipe, IngredientsSection, Ingredients, IngredientsMaster, InstructionSection, InstructionStep
from app import db
from app.data.links import links
from app.utils.fetch_recipe_data import fetch_recipe_data
from app.utils.process_recipe import process_recipe_content, processed_recipe_to_markdown


recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/')
@login_required
def recipes_list():
    recipes = Recipe.query.filter_by(created_by=current_user.id).all()
    return render_template('recipes.html', title='Recipes List', recipes=recipes, links=links)

@recipes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_recipe():
    if request.method == 'POST':
        # Create the main recipe object
        new_recipe = Recipe(
            # id=request.form['name'],
            name=request.form['name'],
            # recipe_image=request.form['image'],
            description=request.form['description'],
            keywords=request.form['keywords'],
            # author=request.form['author'],
            c_notes=request.form['notes'],
            prep_time=request.form['prep_time'], # TODO: Need to convert to ISO 8601 duration
            cook_time=request.form['cook_time'],
            # total_time= prep_time + cook_time, TODO: Need to calculate and convert to ISO 8601 duration
            recipe_yield=request.form['recipe_yield'],
            # recipe_cuisine=request.form['recipe_cuisine'], # TODO: Need to convert to recipe_cuisine and convert to JSON array
            # suitable_for_diet=request.form['suitable_for_diet'], # TODO: Need to convert to JSON array. This should be a multi-select.
            source=request.form['source'],
            recipe_ingredients_raw=request.form['ingredients'],
            recipe_instructions_raw=request.form['instructions'], 
            # nutrition=request.form['nutrition'], TODO: Need to create input and convert to JSON object.
            created_by=current_user.id
        )
        db.session.add(new_recipe)
        db.session.flush()  # Get the ID of the newly created recipe

        # Process each ingredient section
        section_index = 0
        while f'section_name_{section_index}' in request.form:
            section_name = request.form[f'section_name_{section_index}']
            new_section = IngredientsSection(
                recipe_id=new_recipe.id,
                name=section_name,
                c_order=section_index + 1,
                created_by=current_user.id
            )
            db.session.add(new_section)
            db.session.flush()

            # Process each ingredient in the section
            ingredient_index = 0
            while f'ingredient_name_{section_index}_{ingredient_index}' in request.form:
                ingredient_name = request.form[f'ingredient_name_{section_index}_{ingredient_index}']
                quantity = request.form[f'ingredient_quantity_{section_index}_{ingredient_index}']
                unit = request.form[f'ingredient_unit_{section_index}_{ingredient_index}']

                new_ingredient = Ingredients(
                    section_id=new_section.id,
                    name=ingredient_name,
                    quantity=quantity,
                    unit=unit,
                    created_by=current_user.id
                )
                db.session.add(new_ingredient)
                # ingredient_index += 1

            # section_index += 1

        db.session.commit()
        return redirect(url_for('recipes.recipes_list'))

    return render_template('recipe_create.html', title='Create a Recipe', recipe_data={})

@recipes_bp.route('/fetch', methods=['POST'])
@login_required
def fetch_recipe():
    url = request.form.get('url')
    data = fetch_recipe_data(url)
    if data:
        return render_template('recipe_create.html', title='Create Recipe', recipe_data=data)
    else:
        return render_template('recipe_create.html', title='Create Recipe', error="No structured data found.")

@recipes_bp.route('/process-recipe', methods=['POST'])
# @login_required()
def process_recipe():
    processed_recipe_data = {}
    
    # Extract the recipe content from the request
    processed_recipe_data['name'] = request.form.get('name')
    processed_recipe_data['description'] = request.form.get('description')
    processed_recipe_data['recipe_cuisine'] = request.form.get('recipe_cuisine')
    processed_recipe_data['keywords'] = request.form.get('keywords')
    processed_recipe_data['recipe_yield'] = request.form.get('recipe_yield')
    processed_recipe_data['prep_time'] = request.form.get('prep_time')
    processed_recipe_data['cook_time'] = request.form.get('cook_time')
    processed_recipe_data['notes'] = request.form.get('notes')
    processed_recipe_data['source'] = request.form.get('source')

    ingredients = request.form.get('ingredients')
    instructions = request.form.get('instructions')

    # print(recipe_name)
    # print(recipe_description)
                                    
    # # Assuming you have a function `process_recipe_content` that processes the recipe data
    schema_file_path = './app/data/schema/ingredients_instructions_schema_v1.json'
    processed_recipe = process_recipe_content(processed_recipe_data['name'], ingredients, instructions, schema_file_path)
    processed_recipe_data['recipeIngredients'], processed_recipe_data['recipeInstructions'] = processed_recipe_to_markdown(processed_recipe)

    # # Return the processed recipe as JSON
    return render_template('recipe_create.html', title='Create Recipe', recipe_data=processed_recipe_data)

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

from flask import render_template, request, jsonify

@recipes_bp.route('/add_section', methods=['POST'])
@login_required
def add_section():
    section_index = request.form.get('section_index', 0, type=int)
    return render_template('partials/_ingredient_section.html', section_index=section_index)

@recipes_bp.route('/add_ingredient', methods=['POST'])
@login_required
def add_ingredient():
    section_index = request.form.get('section_index', 0, type=int)
    ingredient_index = request.form.get('ingredient_index', 0, type=int)
    return render_template('partials/_ingredient.html', section_index=section_index, ingredient_index=ingredient_index)