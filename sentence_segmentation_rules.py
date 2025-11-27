import regex as re
from utils import get_category_members

ABBREVIATIONS_FILE = 'abbreviations.txt'


def rules(text: str):
    abbreviations = []
    try:
        with open(ABBREVIATIONS_FILE, 'r', encoding='utf-8') as f:
            abbreviations = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        raw_abbreviations_cs = get_category_members("Kategorie:České zkratky")
        abbreviations_cs = sorted([abbrev.rstrip('.') for abbrev in raw_abbreviations_cs if '.' in abbrev])

        raw_abbreviations_en = get_category_members("Category:English abbreviations")
        abbreviations_en = sorted([abbrev.rstrip('.') for abbrev in raw_abbreviations_en if '.' in abbrev])

        raw_abbreviations_pl = get_category_members("Category:Polish abbreviations")
        abbreviations_pl = sorted([abbrev.rstrip('.') for abbrev in raw_abbreviations_pl if '.' in abbrev])

        abbreviations = sorted(list(set(abbreviations_cs + abbreviations_en + abbreviations_pl)))
        with open(ABBREVIATIONS_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(abbreviations))
    abbreviations.extend(['Ms', 'obr'])
    abbreviations_pattern = "|".join(re.escape(abbrev) for abbrev in abbreviations)

    regex_pattern = r'(?<!\b(\d{1,2}\s?|(?i:' + abbreviations_pattern +  r'))|\b\w)\.\s(?![a-z])'

    text = re.sub(regex_pattern, '.\n', text)
    return text
