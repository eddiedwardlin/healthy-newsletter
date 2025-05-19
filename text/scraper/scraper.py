import requests
from bs4 import BeautifulSoup
import os

base_url = "https://www.nhs.uk"
recipes_url = f"{base_url}/healthier-families/recipes/"
res = requests.get(recipes_url)

soup = BeautifulSoup(res.content, "html.parser")

divs = soup.find_all("div", class_="nhsuk-grid-row nhsuk-promo-group")
div_tag = divs[2]

recipe_links = []
for a_tag in div_tag.find_all("a"):
    recipe_links.append(a_tag["href"])


os.makedirs('recipes', exist_ok=True)

for link in recipe_links:
    res = requests.get(f"{base_url}{link}")
    recipe_soup = BeautifulSoup(res.content, "html.parser")

    title_tag = recipe_soup.find("h1")
    title = title_tag.text.strip()
    
    description_div = recipe_soup.find("div", class_="bh-recipe__description")
    description = description_div.get_text(separator='\n', strip=True)
    
    nutritional_div = recipe_soup.find("div", class_="nhsuk-details__text")
    nutritional_info = nutritional_div.get_text(separator='\n', strip=True)
    
    ingredients_div = recipe_soup.find_all("div", class_="nhsuk-grid-column-one-third")[1]
    ingredients = ingredients_div.get_text(separator='\n', strip=True)

    method_div = recipe_soup.find("div", class_="nhsuk-grid-column-two-thirds bh-recipe-instructions__method")
    method = method_div.get_text(separator='\n', strip=True)

    output_path = f"./recipes/{title.replace(' ', '_')}.txt"
    
    with open(output_path, "w") as f:
        f.write(f"{title}\n\n{description}\n\n{nutritional_info}\n\n{ingredients}\n\n{method}")