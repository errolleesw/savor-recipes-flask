from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', title='Savor')

@main.route('/mealplan')
def mealplan():
    return 'TBD - meal planning features'

@main.route('/settings')
def settings():
    return 'TBD - SETTINGS'