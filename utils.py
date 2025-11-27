import requests
import json
import time

def load(path):
    with open(path,'r' ,encoding='utf-8') as f:
        file = f.read()
    print(f"Loaded {path}.")
    return file

def dump(path, text):
    with open(path,'w+', encoding='utf-8') as f:
        f.write(text)
    print(f"Written results to {path}")


def get_category_members(category_name):
    if category_name.startswith("Category:"):
        url = "https://en.wiktionary.org/w/api.php"
    elif category_name.startswith("Kategorie:"):
        url = "https://cs.wiktionary.org/w/api.php"
    else:
        url = "https://cs.wiktionary.org/w/api.php"

    headers = {
        'User-Agent': 'MyBot/1.0 (vojtech-balek@github)'
    }

    # Query parameters
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category_name,
        "cmlimit": "max",
        "cmtype": "page"
    }

    members = []

    while True:
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()

            if "query" in data and "categorymembers" in data["query"]:
                for member in data["query"]["categorymembers"]:
                    members.append(member['title'])

            if "continue" in data and data["continue"].get("cmcontinue"):
                params["cmcontinue"] = data["continue"]["cmcontinue"]
                print(f"Fetching next batch... (found {len(members)} so far)")
                time.sleep(0.5) # Be polite to the server
            else:
                break
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            break
        except json.JSONDecodeError:
            print("Failed to decode JSON from response. Response text:")
            print(response.text)
            break
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
            break


    return members
