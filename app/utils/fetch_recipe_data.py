import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime


def fetch_recipe_data(url):
    response = requests.get(url)
    web_content = response.content

    soup = BeautifulSoup(web_content, 'html.parser')
    script_tag = soup.find('script', type='application/ld+json')
    recipe_data = {}

    if script_tag:
        structured_data = json.loads(script_tag.string)
        
        # Write the structured data to a JS file with a timestamp
        write_json_to_file(structured_data, 'recipe_structured_data')

        if '@graph' in structured_data:
            recipe = next((item for item in structured_data['@graph'] if item['@type'] == 'Recipe'), {})
            if recipe:
                recipe_data['name'] = recipe.get('name')
                recipe_data['description'] = recipe.get('description')
                recipe_data['recipeCuisine'] = ', '.join(recipe.get('recipeCuisine', []))
                recipe_data['keywords'] = ', '.join(recipe.get('keywords', '').split(', '))
                recipe_data['recipeYield'] = recipe.get('recipeYield', [''])[0]
                recipe_data['prepTime'] = recipe.get('prepTime')
                recipe_data['cookTime'] = recipe.get('cookTime')
                recipe_data['recipeIngredient'] = '\n'.join(recipe.get('recipeIngredient', []))
                recipe_data['recipeInstructions'] = '\n'.join(step['text'] for step in recipe.get('recipeInstructions', []))
                recipe_data['source'] = recipe.get('mainEntityOfPage')

                # Extract nutrition information
                nutrition_info = recipe.get('nutrition', {})
                if nutrition_info:
                    recipe_data['nutrition'] = {
                        'servingSize': nutrition_info.get('servingSize'),
                        'calories': nutrition_info.get('calories'),
                        'carbohydrateContent': nutrition_info.get('carbohydrateContent'),
                        'proteinContent': nutrition_info.get('proteinContent'),
                        'fatContent': nutrition_info.get('fatContent'),
                        'saturatedFatContent': nutrition_info.get('saturatedFatContent'),
                        'cholesterolContent': nutrition_info.get('cholesterolContent'),
                        'sodiumContent': nutrition_info.get('sodiumContent'),
                        'fiberContent': nutrition_info.get('fiberContent'),
                        'sugarContent': nutrition_info.get('sugarContent')
                    }

    # Extract Recipe Notes from the HTML and store them in recipe_data['notes']
    recipe_data['notes'] = extract_recipe_notes(soup)
    write_json_to_file(recipe_data, 'recipe_data')

    return recipe_data

def extract_recipe_notes(soup):
    # Locate the div that contains the recipe notes
    notes_section = soup.find('div', class_='wprm-recipe-notes-container')

    if notes_section:
        # Extract the text content of the notes
        notes = notes_section.get_text(separator='\n', strip=True)
        return notes
    else:
        return ''
    

def write_json_to_file(data, file_name):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(os.getcwd(), 'app', '00_sandbox', f"{file_name}_{current_time}.js")
    js_content = f"const structuredData = {json.dumps(data, indent=2)};"
    with open(file_path, 'w') as js_file:
        js_file.write(js_content)
        print(f"Structured data has been written to {file_path}")