# app/models.py

from datetime import datetime
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    recipe_image = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.String(250), nullable=True)
    author = db.Column(db.JSON, nullable=True)  # Author as JSON field
    c_notes = db.Column(db.Text, nullable=True)
    prep_time = db.Column(db.String(50), nullable=False)  # ISO 8601 duration
    cook_time = db.Column(db.String(50), nullable=False)  # ISO 8601 duration
    total_time = db.Column(db.String(50), nullable=True)  # ISO 8601 duration
    recipe_yield = db.Column(db.Integer, nullable=False)
    recipe_cuisine = db.Column(db.JSON, nullable=True)  # JSON array
    suitable_for_diet = db.Column(db.JSON, nullable=True)  # JSON array
    source = db.Column(db.String(200), nullable=True)
    recipe_ingredients_json = db.Column(db.JSON, nullable=True)  # JSON array
    recipe_ingredients_raw = db.Column(db.Text, nullable=True) # raw recipe ingredients input
    recipe_instructions_json = db.Column(db.JSON, nullable=True) # JSON array
    recipe_instructions_raw = db.Column(db.Text, nullable=True) # raw recipe instructions input.

    nutrition = db.Column(db.JSON, nullable=True)  # JSON object

    created_by = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(100), nullable=True)
    modified_on = db.Column(db.DateTime, onupdate=datetime.utcnow)

    ingredients_sections = db.relationship('IngredientsSection', back_populates='recipe', cascade='all, delete-orphan')
    instruction_sections = db.relationship('InstructionSection', back_populates='recipe', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'recipe_image': self.recipe_image,
            'description': self.description,
            'keywords': self.keywords,
            'author': self.author,
            'c_notes': self.c_notes,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'total_time': self.total_time,
            'recipe_yield': self.recipe_yield,
            'recipe_cuisine': self.recipe_cuisine,
            'suitable_for_diet': self.suitable_for_diet,
            'source': self.source,
            'recipe_ingredient_json': self.recipe_ingredients_json,
            'recipe_ingredient_raw': self.recipe_ingredients_raw,
            'recipe_instructions_json': self.recipe_instructions_json,
            'recipe_instructions_raw': self.recipe_instructions_raw,
            'nutrition': self.nutrition,
            'created_by': self.created_by,
            'created_on': self.created_on,
            'modified_by': self.modified_by,
            'modified_on': self.modified_on,
            'ingredients_sections': [section.to_dict() for section in self.ingredients_sections],
            'instruction_sections': [section.to_dict() for section in self.instruction_sections]
        }

class IngredientsSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', name='fk_ingredients_section_recipe'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    c_order = db.Column(db.Integer, nullable=False)

    created_by = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(100), nullable=True)
    modified_on = db.Column(db.DateTime, onupdate=datetime.utcnow)

    recipe = db.relationship('Recipe', back_populates='ingredients_sections')
    ingredients = db.relationship('Ingredients', back_populates='section', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'c_order': self.c_order,
            'created_by': self.created_by,
            'created_on': self.created_on,
            'modified_by': self.modified_by,
            'modified_on': self.modified_on,
            'ingredients': [ingredient.to_dict() for ingredient in self.ingredients]
        }

class Ingredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('ingredients_section.id', name='fk_ingredients_section'), nullable=False)
    name = db.Column(db.String(100), db.ForeignKey('ingredients_master.name', name='fk_ingredients_master'), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    created_by = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(100), nullable=True)
    modified_on = db.Column(db.DateTime, onupdate=datetime.utcnow)

    section = db.relationship('IngredientsSection', back_populates='ingredients')
    ingredient_master = db.relationship('IngredientsMaster', back_populates='ingredients')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'created_by': self.created_by,
            'created_on': self.created_on,
            'modified_by': self.modified_by,
            'modified_on': self.modified_on
        }

class IngredientsMaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    ingredients = db.relationship('Ingredients', back_populates='ingredient_master')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class InstructionSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', name='fk_instruction_section_recipe'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    c_order = db.Column(db.Integer, nullable=False)
    steps = db.relationship('InstructionStep', back_populates='section', cascade='all, delete-orphan')

    created_by = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(100), nullable=True)
    modified_on = db.Column(db.DateTime, onupdate=datetime.utcnow)

    recipe = db.relationship('Recipe', back_populates='instruction_sections')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'c_order': self.c_order,
            'created_by': self.created_by,
            'created_on': self.created_on,
            'modified_by': self.modified_by,
            'modified_on': self.modified_on,
            'steps': [step.to_dict() for step in self.steps]
    }

class InstructionStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('instruction_section.id', name='fk_instruction_step_section'), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    c_order = db.Column(db.Integer, nullable=False)

    created_by = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(100), nullable=True)
    modified_on = db.Column(db.DateTime, onupdate=datetime.utcnow)

    section = db.relationship('InstructionSection', back_populates='steps')

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'name': self.name,
            'c_order': self.c_order,
            'created_by': self.created_by,
            'created_on': self.created_on,
            'modified_by': self.modified_by,
            'modified_on': self.modified_on
        }