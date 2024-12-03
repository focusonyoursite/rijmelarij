"""
Dutch rhyming word checker
"""
import re

def clean_word(word):
    """Remove punctuation and convert to lowercase"""
    return re.sub(r'[^\w\s]', '', word.lower())

def get_last_syllable(word):
    """Get the last syllable of a word (simplified)"""
    word = clean_word(word)
    vowels = 'aeiouy'
    # Find the last vowel sequence
    last_vowel_pos = max((i for i, c in enumerate(word) if c in vowels), default=-1)
    if last_vowel_pos == -1:
        return word
    # Include everything from the last vowel onwards
    return word[last_vowel_pos:]

class RhymeChecker:
    def __init__(self):
        # Common Dutch word endings that rhyme
        self.rhyme_patterns = {
            'aard': ['aard', 'aart', 'ard'],
            'acht': ['acht', 'agt'],
            'ag': ['ag', 'ach'],
            'eel': ['eel', 'eël'],
            'eer': ['eer', 'air', 'aire'],
            'eid': ['eid', 'ijt'],
            'ijk': ['ijk', 'eik'],
            'ing': ['ing'],
            'ooi': ['ooi', 'ooie'],
            'ouw': ['ouw', 'auw'],
            'tie': ['tie', 'sie', 'cie'],
        }

    def do_words_rhyme(self, word1, word2):
        """Check if two words rhyme"""
        word1, word2 = clean_word(word1), clean_word(word2)
        if not word1 or not word2:
            return False
            
        # Exact match of last syllable
        if get_last_syllable(word1) == get_last_syllable(word2):
            return True
            
        # Check common rhyming patterns
        for patterns in self.rhyme_patterns.values():
            if any(word1.endswith(p) for p in patterns) and any(word2.endswith(p) for p in patterns):
                return True
                
        return False

    def get_rhyming_words(self, word, word_list=None):
        """Get list of words that rhyme with the given word"""
        if word_list is None:
            # Default Dutch words that are commonly used in Sinterklaas poems
            word_list = [
                'paard', 'waard', 'taart', 'kaart', 'zwart', 'smart',
                'nacht', 'wacht', 'zacht', 'bracht', 'verwacht',
                'dag', 'zag', 'mag', 'lach', 'slag',
                'veel', 'heel', 'steel', 'kasteel', 'fluweel',
                'meer', 'keer', 'weer', 'zeer', 'peer',
                'tijd', 'blijt', 'wijt', 'spijt', 'krijt',
                'rijk', 'gelijk', 'praktijk', 'muziek', 'publiek',
                'zing', 'spring', 'ring', 'ding', 'kring',
                'mooi', 'hooi', 'dooi', 'kooi', 'strooi',
                'vrouw', 'blauw', 'gauw', 'nauw', 'trouw',
                'traditie', 'positie', 'ambitie', 'conditie', 'politie',
                'Sint', 'kind', 'wind', 'lint', 'print',
                'Piet', 'ziet', 'niet', 'lied', 'verschiet',
                'boot', 'groot', 'noot', 'rood', 'sloot',
                'dak', 'pak', 'bak', 'zak', 'tak',
                'schoen', 'doen', 'zoen', 'groen', 'toen',
                'huis', 'thuis', 'pluis', 'kruis', 'muis',
                'blij', 'zij', 'mij', 'vrij', 'voorbij',
                'feest', 'geweest', 'leest', 'meest', 'beest',
                'jaar', 'daar', 'klaar', 'zwaar', 'elkaar',
                'goed', 'moet', 'voet', 'zoet', 'groet',
                'man', 'kan', 'dan', 'span', 'plan',
                'klein', 'rein', 'plein', 'fontein', 'terrein',
                'lach', 'dag', 'zag', 'mag', 'vlag',
                'spelen', 'delen', 'velen', 'strelen', 'bevelen',
                'zingen', 'springen', 'dingen', 'kringen', 'dwingen',
                'leven', 'geven', 'zweven', 'even', 'beleven'
            ]
        
        word = clean_word(word)
        rhyming_words = []
        
        for test_word in word_list:
            if test_word.lower() != word and self.do_words_rhyme(word, test_word):
                rhyming_words.append(test_word)
                
        return rhyming_words

# Create a global instance
rhyme_checker = RhymeChecker()

# Expose methods at module level for backwards compatibility
do_words_rhyme = rhyme_checker.do_words_rhyme
get_rhyming_words = rhyme_checker.get_rhyming_words
