import requests
from bs4 import BeautifulSoup
import random
import re

class SinterklaasGedichtenScraper:
    def __init__(self):
        self.base_url = "https://sinterklaasgedichten.com/kant-en-klare-sinterklaasgedichten"
        self.poems = []
        self.common_sint_phrases = [
            "Zie ginds komt de stoomboot",
            "Sinterklaas kapoentje",
            "Hoor wie klopt daar kinderen",
            "Zwarte Piet",
            "pepernoten",
            "chocoladeletter",
            "pakjesavond",
            "verlanglijstje",
            "schoentje zetten",
            "zak met cadeautjes",
            "5 december",
            "Sint en Piet",
            "marsepein",
            "strooigoed",
            "mijter",
            "staf",
            "stoomboot uit Spanje",
            "door de schoorsteen",
            "het grote boek"
        ]

    def scrape_poems(self):
        """Scrape Sinterklaasgedichten from the website"""
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Zoek alle gedichten op de pagina
            # Dit moet aangepast worden op basis van de HTML structuur van de website
            poem_elements = soup.find_all(['p', 'div'], class_=['poem', 'gedicht'])
            
            for element in poem_elements:
                poem_text = element.get_text().strip()
                if poem_text and len(poem_text.split('\n')) > 2:  # Minimaal 2 regels
                    self.poems.append(self.clean_poem(poem_text))
            
            print(f"Aantal gedichten verzameld: {len(self.poems)}")
        except Exception as e:
            print(f"Fout bij het scrapen van gedichten: {str(e)}")
            # Gebruik backup zinnen als scrapen mislukt
            self.poems = self.get_backup_phrases()

    def clean_poem(self, poem):
        """Maak het gedicht schoon van onnodige tekens en opmaak"""
        # Verwijder HTML tags
        poem = re.sub(r'<[^>]+>', '', poem)
        # Verwijder dubbele witregels
        poem = re.sub(r'\n\s*\n', '\n', poem)
        # Verwijder spaties aan begin en eind van regels
        poem = '\n'.join(line.strip() for line in poem.split('\n'))
        return poem

    def get_backup_phrases(self):
        """Geef backup Sinterklaas zinnen terug als scrapen mislukt"""
        return [
            "Sinterklaas is weer in het land,\nMet zijn Pieten aan elke kant.",
            "Pepernoten, marsepein,\nWat zal er in mijn schoentje zijn?",
            "Door de schoorsteen komt de Sint,\nMet cadeautjes voor elk kind.",
            "Het paard van Sinterklaas op het dak,\nStrooit pepernoten uit zijn zak."
        ]

    def get_random_sint_phrase(self):
        """Geef een willekeurige Sinterklaas-gerelateerde zin"""
        return random.choice(self.common_sint_phrases)

    def get_random_poem(self):
        """Geef een willekeurig gedicht terug"""
        if not self.poems:
            self.scrape_poems()
        return random.choice(self.poems) if self.poems else self.get_random_sint_phrase()

    def get_sint_context(self):
        """Verzamel context voor het genereren van Sinterklaasgedichten"""
        context = {
            'phrases': random.sample(self.common_sint_phrases, 3),
            'example_poem': self.get_random_poem(),
            'themes': [
                'pakjesavond',
                'schoentje zetten',
                'sinterklaasavond',
                'verlanglijstje',
                'surprise'
            ]
        }
        return context
