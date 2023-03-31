import requests
import json
import unittest
import os

###########################################
# Your name: Urja Kaushik                 #
# Who you worked with:                    #
###########################################

def load_json(filename):

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    
    except FileNotFoundError:
        data = {}
    
    return data

def write_json(filename, dict):

    with open(filename, 'w') as f:
        json.dump(dict, f)
    
    return

def get_swapi_info(url, params=None):

    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print("Request failed with status code:", response.status_code)
    
    except requests.exceptions.RequestException as e:
        print("Exception:", e)
   
    return None

def cache_all_pages(people_url, filename):

    cache = load_json(filename)
    
    if "all_pages_cached" in cache and cache["all_pages_cached"]:
        print("All pages already cached.")
        return
    
    page = 1
    all_results = []

    while True:

        if f"page {page}" in cache:
            print(f"Page {page} already cached.")
            all_results.extend(cache[f"page {page}"])
        else:

            print(f"Fetching page {page} from API...")
            response = get_swapi_info(people_url, {"page": page})
            if response is None:
                print(f"Unable to fetch page {page} from API.")
                return

            results = response.get("results", [])
            cache[f"page {page}"] = results
            all_results.extend(results)

            if response.get("next") is None:
                break
        
        page += 1
    
    cache["all_pages_cached"] = True
    
    write_json(filename, cache)
    
    return all_results


def get_starships(filename):

    cache = load_json(filename)
    starships = {}
    
    for character in cache.values():
        for person in character:
            if "starships" in person:
                starship_names = person["starships"]
            else:
                starship_names = []
                for url in person.get("starships", []):
                    starship = get_swapi_info(url)
                    if starship is not None:
                        starship_names.append(starship.get("name", ""))
                person["starships"] = starship_names
                
        write_json(filename, cache)
            
    for character in cache.values():
        for person in character:
            starships[person["name"]] = person["starships"]
    
    return starships
#################### EXTRA CREDIT ######################

def calculate_bmi(filename):

    cache_data = load_json(filename)

    # Create an empty dictionary to store the results
    bmi_data = {}

    # Loop through each character in the cache
    for character in cache_data.values():
        # Get the character's name, height, and mass
        name = character['name']
        height = character['height']
        mass = character['mass']

        # Check if the character's height and mass are known
        if height != 'unknown' and mass != 'unknown':
            # Convert the height to meters and the mass to kilograms
            height_m = float(height) / 100
            mass_kg = float(mass)

            # Calculate the BMI using the formula for the metric system
            bmi = mass_kg / height_m**2

            # Add the character's BMI to the dictionary
            bmi_data[name] = bmi

    return bmi_data

class TestHomework6(unittest.TestCase):
    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.filename = dir_path + '/' + "swapi_people.json"
        self.cache = load_json(self.filename)
        self.url = "https://swapi.dev/api/people"

    def test_write_json(self):
        write_json(self.filename, self.cache)
        dict1 = load_json(self.filename)
        self.assertEqual(dict1, self.cache)

    def test_get_swapi_info(self):
        people = get_swapi_info(self.url)
        tie_ln = get_swapi_info("https://swapi.dev/api/vehicles", {"search": "tie/ln"})
        self.assertEqual(type(people), dict)
        self.assertEqual(tie_ln['results'][0]["name"], "TIE/LN starfighter")
        self.assertEqual(get_swapi_info("https://swapi.dev/api/pele"), None)
    
    def test_cache_all_pages(self):
        cache_all_pages(self.url, self.filename)
        swapi_people = load_json(self.filename)
        self.assertEqual(type(swapi_people['page 1']), list)

    def test_get_starships(self):
        starships = get_starships(self.filename)
        self.assertEqual(len(starships), 19)
        self.assertEqual(type(starships["Luke Skywalker"]), list)
        self.assertEqual(starships['Biggs Darklighter'][0], 'X-wing')

    def test_calculate_bmi(self):
        bmi = calculate_bmi(self.filename)
        self.assertEqual(len(bmi), 59)
        self.assertAlmostEqual(bmi['Greedo'], 24.73)
    
if __name__ == "__main__":
    unittest.main(verbosity=2)
