import os
from dotenv import load_dotenv
import json
import os
from bs4 import BeautifulSoup
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# from jsonschema import validate
from datetime import datetime
# import markdown
from langchain_openai import ChatOpenAI
from app.utils.fetch_recipe_data import fetch_recipe_data


load_dotenv()

tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

def processed_recipe_to_markdown(processed_recipe):
    # Initialize variables to store the markdown content
    ingredients_md = ""
    instructions_md = ""

    # Parse the ingredients sections
    for section in processed_recipe.get('c_supply', []):
        ingredients_md += f"### {section['name']}\n"
        for item in section['itemListElement']:
            quantity = item['quantity']
            unit = item['unit']
            ingredient = item['ingredient']
            ingredients_md += f"- **{quantity} {unit}** {ingredient}\n"
        ingredients_md += "\n"  # Add an extra newline for better readability

    # Parse the instructions sections
    for section in processed_recipe.get('recipeInstructions', []):
        instructions_md += f"### {section['name']}\n"
        for step in section['itemListElement']:
            step_name = step['name']
            step_text = step['text']
            instructions_md += f"1. **{step_name}:** {step_text}\n"
        instructions_md += "\n"  # Add an extra newline for better readability

    # Update the recipe_data with the markdown content

    return ingredients_md, instructions_md

def process_recipe_content(recipe_name, recipe_ingredients, recipe_instructions, schema_file_path):
    system_message = """I have provided you with the recipe name, ingredients and instructions for a recipe. I want you to organise and update the ingredients and instructions list 
    based on these principles:
        1. Ingredients should be standardised against the raw item that is available at the local grocery store. There should be no "processing" / "preparation" steps in the ingreidents. 
        E.g. it shouldn't say roughly chopped parsely, it should just say Parsely, the chopping should be included in the steps.
        2. Ingredients should be organised into categories, based on where they would typically be found in a kitchen.
        3. Recipe instructions should include the preparation of the ingredients and be organised as efficiently as possible, 
        E.g. if an item needs to go in the oven or simmer for a while, prep that first and prep other items while that is cooking.
        4. You can add additional steps if required to help make the instructions easier to understand, but DO NOT change the core steps in the recipe.
        5. Recipe instructions should be grouped into sections where it makes sense. 
    
    Output must be provided in this JSON Structure:
    {schema}
    """
    user_message = """
        Recipe Name: {recipe_name}
        Ingredients: {recipe_ingredients}
        Instructions: {recipe_instructions}
    """

 # create prompt template
    prompt_template = ChatPromptTemplate.from_messages([("system", system_message), ("user", user_message)])

    # define model and chain
    model = ChatOpenAI(model="gpt-4o")
    schema = read_json(schema_file_path)  # extract json dict form schema
    structured_model = model.with_structured_output(schema)  # ensuring structured output from model
    chain = prompt_template | structured_model

    # prep recipe and invoke chain.
    recipe_json = chain.invoke({"recipe_name": recipe_name, "recipe_ingredients": recipe_ingredients, "recipe_instructions": recipe_instructions, "schema": schema})

    return recipe_json
    # create json file
    # json_output_file_path = os.path.join(json_output_dir, os.path.basename(recipe_name).replace('.html', '.json'))
    # save_json_to_file(recipe_json, json_output_file_path)
    # print(f"Recipe JSON saved to {json_output_file_path}")

# Function to read the JSON schema
def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None