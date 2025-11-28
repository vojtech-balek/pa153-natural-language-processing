import pandas as pd


TITLES = {
    'doc', 'prof', 'ing', 'mudr', 'judr', 'rndr', 'phdr', 'mvdr',
    'dr', 'drsc', 'csc', 'paeddr', 'pharmdr', 'thdr', 'bc', 'mgr',
    'arch', 'plk', 'mjr', 'kpt', 'gen', 'p', 'sv', 'fa'
}


def get_labels(raw_text, gold_text):
    """
    Returns a dictionary {raw_index: 1} for every sentence boundary.
    Any index not in the dict is implicitly 0.
    """
    labels = {}

    content_map = []

    for i, char in enumerate(raw_text):
        if not char.isspace():
            content_map.append(i)

    gold_content_count = 0

    for i, char in enumerate(gold_text):
        if not char.isspace():
            gold_content_count += 1

        elif char == '\n':
            if gold_content_count > 0:
                target_content_idx = gold_content_count - 1

                if target_content_idx < len(content_map):
                    raw_idx_of_boundary = content_map[target_content_idx]
                    labels[raw_idx_of_boundary] = 1

    return labels

def extract_features(text, index):
    """
    Extracts features for a candidate punctuation mark at `index`.
    """
    features = {}

    prev_word = get_previous_word(text, index)
    next_word = get_next_word(text, index)

    if next_word:
        features['next_is_upper'] = next_word[0].isupper()
        features['next_is_lower'] = next_word[0].islower()
        features['next_is_number'] = next_word[0].isdigit()
        features['next_is_quote'] = next_word[0] in ['"', "'", '”']
    else:
        features['next_is_upper'] = False
        features['next_is_lower'] = False
        features['next_is_number'] = False

    if prev_word:
        features['prev_word_len'] = len(prev_word)
        features['prev_is_upper'] = prev_word.isupper()
        clean_prev = prev_word.lower()
        features['prev_is_title'] = clean_prev in TITLES

        features['prev_is_initial'] = (len(prev_word) == 1 and prev_word.isupper())

    else:
        features['prev_word_len'] = 0
        features['prev_is_upper'] = False
        features['prev_is_title'] = False
        features['prev_is_initial'] = False

    if index > 0:
        prev_char = text[index - 1]
        features['prev_char_is_period'] = (prev_char == '.')
        features['prev_char_is_punct'] = prev_char in ['!', '?']
    else:
        features['prev_char_is_period'] = False
        features['prev_char_is_punct'] = False

    if index < len(text) - 1:
        next_char = text[index + 1]
        features['next_char_is_period'] = (next_char == '.')
        features['next_char_is_punct'] = next_char in ['!', '?']
    else:
        features['next_char_is_period'] = False
        features['next_char_is_punct'] = False

    if index < len(text) - 2:
        features['next_next_char_is_period'] = (text[index + 2] == '.')
    else:
        features['next_next_char_is_period'] = False

    features['punct_type'] = text[index]
    return features


def get_previous_word(text, index):
    end_word_idx = None
    while index > 0:
        index -= 1
        char = text[index]

        if char.isalnum():
            if end_word_idx is None:
                end_word_idx = index + 1
        else:
            if end_word_idx is not None:
                return text[index + 1: end_word_idx]
    if end_word_idx is not None:
        return text[0: end_word_idx]
    return None


def get_next_word(text, index):
    length = len(text)
    start_word_idx = None
    current_idx = index + 1

    while current_idx < length:
        char = text[current_idx]

        if char.isalnum():
            if start_word_idx is None:
                start_word_idx = current_idx
        else:
            if start_word_idx is not None:
                return text[start_word_idx: current_idx]

        current_idx += 1

    if start_word_idx is not None:
        return text[start_word_idx:]

    return None


def create_dataset(raw_text, labels):
    """
    raw_text: The string of the raw file.
    labels: A list/dictionary indicating if a specific index is a boundary.
            (You derive this from comparing Raw vs Golden Standard)
    """
    data = []

    for i, char in enumerate(raw_text):
        if char in ['.', '?', '!']:
            feats = extract_features(raw_text, i)

            is_boundary = labels.get(i, 0)

            feats['label'] = is_boundary

            data.append(feats)

    return pd.DataFrame(data)

