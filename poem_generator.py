import os
from dotenv import load_dotenv
import openai
import random
import time
from sint_scraper import SinterklaasGedichtenScraper

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai

# Initialize Sint scraper
sint_scraper = SinterklaasGedichtenScraper()

class PoemGenerator:
    def __init__(self):
        self.use_rhyme_check = False
        try:
            import rijm_checker
            self.rijmwoorden = rijm_checker
            self.use_rhyme_check = True
            print("Rijmwoordenboek succesvol geladen! ")
        except ImportError:
            print("Waarschuwing: Rijmwoordenboek niet gevonden. Alleen basis gedichten worden gegenereerd.")
        
        # Initialize Sint scraper
        self.sint_scraper = sint_scraper
        self.sint_scraper.scrape_poems()

    def get_person_info(self):
        """Verzamel informatie over de persoon waarvoor het gedicht is"""
        print("\n--- Informatie over het Sinterklaasgedicht ---")
        name = input("Voor wie is het gedicht? (naam): ")
        
        while True:
            gender = input("Is dat een jongen, meisje, man of vrouw? ").lower()
            if gender in ['jongen', 'meisje', 'man', 'vrouw']:
                break
            print("Kies alstublieft uit: jongen, meisje, man of vrouw")
        
        gift = input("Wat is het kado? ")
        hobbies = input("Wat zijn de hobbies van deze persoon? ")
        
        # Extra Sinterklaas-specifieke vragen
        while True:
            is_surprise = input("Is het een surprise? (ja/nee): ").lower()
            if is_surprise in ['ja', 'nee']:
                break
            print("Antwoord alstublieft met 'ja' of 'nee'")
        
        theme = input("Kies een thema (sinterklaas, verjaardag, afscheid, bedankt): ").lower()
        difficulty = input("Kies een moeilijkheidsgraad (easy, medium, hard): ").lower()
        
        return {
            "name": name,
            "gender": gender,
            "gift": gift,
            "hobbies": hobbies,
            "is_surprise": is_surprise == 'ja',
            "theme": theme,
            "difficulty": difficulty
        }

    def call_openai_with_retry(self, messages, temperature=0.7, max_tokens=500, max_retries=3):
        """Probeer OpenAI API aan te roepen met retry logic"""
        for attempt in range(max_retries):
            try:
                response = client.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except openai.error.RateLimitError:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 20  # Exponential backoff
                    print(f"\nEven wachten vanwege API limiet ({wait_time} seconden)...")
                    time.sleep(wait_time)
                else:
                    raise Exception("Kon geen verbinding maken met de AI. Probeer het later opnieuw.")
            except Exception as e:
                print(f"Error: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise

    def suggest_rhyming_words(self, word):
        """Get rhyming words for a given word using both dictionary and AI"""
        rhyming_words = set()
        
        # First try the dictionary if available
        if self.use_rhyme_check:
            dict_words = self.rijmwoorden.get_rhyming_words(word.lower())
            rhyming_words.update(dict_words)
        
        # Then use AI to generate more contextual rhyming words
        prompt = f"""Geef 5 Nederlandse woorden die rijmen op '{word}'.
        De woorden moeten:
        1. Echt bestaande Nederlandse woorden zijn
        2. Passen in een gedicht
        3. Verschillend zijn van elkaar
        4. Perfect rijmen (geen half-rijm)
        
        Geef alleen de woorden terug, gescheiden door komma's."""
        
        try:
            response = self.call_openai_with_retry([{
                "role": "system",
                "content": "Je bent een expert in Nederlandse rijmwoorden."
            }, {
                "role": "user",
                "content": prompt
            }], temperature=0.7, max_tokens=100)
            
            ai_words = [w.strip() for w in response.split(',')]
            rhyming_words.update(ai_words)
            
            # Return a list of unique words, sorted alphabetically
            return sorted(list(rhyming_words))
        except Exception as e:
            print(f"Error suggesting rhyming words: {str(e)}")
            # If AI fails, return dictionary words if available, otherwise empty list
            return sorted(list(rhyming_words)) if rhyming_words else []

    def regenerate_line(self, line_index, current_lines):
        """Generate a new line that fits with the context of surrounding lines"""
        context = {
            'previous_lines': current_lines[:line_index],
            'next_lines': current_lines[line_index + 1:] if line_index + 1 < len(current_lines) else []
        }
        
        prompt = f"""Genereer een nieuwe regel voor een Nederlands gedicht.
        Deze regel moet passen bij de volgende context:
        
        Vorige regels:
        {chr(10).join(context['previous_lines']) if context['previous_lines'] else '[Begin van gedicht]'}
        
        Volgende regels:
        {chr(10).join(context['next_lines']) if context['next_lines'] else '[Einde van gedicht]'}
        
        De nieuwe regel moet:
        1. Rijmen op de vorige of volgende regel (afhankelijk van de positie)
        2. Passen bij het thema en de toon van het gedicht
        3. Natuurlijk Nederlands zijn
        4. Ongeveer dezelfde lengte hebben als de andere regels
        
        Geef alleen de nieuwe regel terug, zonder aanvullende tekst of uitleg."""
        
        try:
            response = self.call_openai_with_retry([{
                "role": "system",
                "content": "Je bent een expert in het schrijven van Nederlandse gedichten."
            }, {
                "role": "user",
                "content": prompt
            }], temperature=0.8, max_tokens=100)
            
            return response.strip()
        except Exception as e:
            print(f"Error generating new line: {str(e)}")
            raise

    def analyze_poem_rhyme(self, poem):
        """Analyseer het rijmschema van het gedicht"""
        if not self.use_rhyme_check:
            return
        
        lines = [line.strip() for line in poem.split('\n') if line.strip()]
        print("\nRijmanalyse van het gedicht:")
        
        for i in range(0, len(lines)-1, 2):
            if i+1 < len(lines):
                word1 = lines[i].split()[-1].lower().strip('.,!?')
                word2 = lines[i+1].split()[-1].lower().strip('.,!?')
                
                # Haal rijmwoorden op voor het eerste woord
                rhyming_words = self.rijmwoorden.get_rhyming_words(word1)
                
                if word2.lower() in [w.lower() for w in rhyming_words]:
                    print(f"✓ '{word1}' rijmt met '{word2}'")
                else:
                    print(f"× '{word1}' rijmt niet met '{word2}'")
                    print("Suggesties voor alternatieve rijmwoorden:")
                    self.suggest_rhyming_words(word1)

    def generate_fallback_poem(self, context):
        """Genereer een eenvoudig Sinterklaasgedicht zonder OpenAI"""
        name = context['name']
        gift = context['gift']
        hobbies = context['hobbies'].split(',')[0] if ',' in context['hobbies'] else context['hobbies']
        
        templates = [
            [
                f"Op een koude decemberdag,",
                f"Zag ik {name} met een grote lach,",
                f"Bezig met {hobbies} zoals altijd,",
                f"Dat maakt deze Sint zeer verblijd!",
                f"Daarom krijg je dit jaar van mij,",
                f"Een {gift}, dat maakt je vast heel blij!"
            ],
            [
                f"Het is weer die tijd van het jaar,",
                f"Met pepernoten hier en daar,",
                f"En kijk eens wie ik daar zie staan,",
                f"{name} komt er vrolijk aan!",
                f"Een {gift} heb ik voor jou bewaard,",
                f"Dat maakt deze dag heel wat waard!"
            ],
            [
                f"De sterren schijnen aan de hemel zo mooi,",
                f"De daken zijn met sneeuw bedekt, wat een tooi!",
                f"En daar zie ik {name} die van {hobbies} houdt,",
                f"Een passie die nooit zal worden oud!",
                f"Speciaal voor jou heb ik dit jaar,",
                f"Een {gift} met een strik, helemaal klaar!"
            ]
        ]
        
        return random.choice(templates)

    def generate_single_line(self, previous_line, context, target_words=None):
        """Genereer een enkele regel die rijmt op de vorige regel, met een specifiek aantal woorden"""
        try:
            system_message = {
                "role": "system",
                "content": """Je bent een Nederlandse dichter, gespecialiseerd in rijmende regels.
                Genereer één enkele dichtregel in natuurlijk Nederlands die rijmt op de gegeven regel.
                
                Richtlijnen:
                - Gebruik ALLEEN natuurlijk, idiomatisch Nederlands
                - Vermijd letterlijke vertalingen uit het Engels
                - Gebruik correcte Nederlandse zinsconstructies
                - Zorg dat de regel natuurlijk aanvoelt
                - Maak de regel persoonlijk en relevant voor de context"""
            }

            user_message = {
                "role": "user",
                "content": f"""Schrijf één regel die rijmt op: "{previous_line}"

                Context over de persoon:
                - Naam: {context['name']}
                - {'Kind' if context['gender'] in ['jongen', 'meisje'] else 'Volwassene'}: {context['gender']}
                - Cadeau: {context['gift']}
                - Hobby's: {context['hobbies']}

                De nieuwe regel moet:
                - Rijmen op de vorige regel
                - Natuurlijk Nederlands zijn
                - Passen bij de context
                - {f'Ongeveer {target_words} woorden bevatten' if target_words else 'Een passende lengte hebben'}

                Geef alleen de nieuwe regel terug, zonder extra tekst."""
            }

            response = self.call_openai_with_retry(
                messages=[system_message, user_message],
                temperature=0.7,
                max_tokens=50
            )
            
            return response.strip()
            
        except Exception as e:
            return self.generate_fallback_line(context)

    def generate_fallback_line(self, context):
        """Genereer een fallback regel als OpenAI niet beschikbaar is"""
        fallback_lines = [
            f"En {context['name']} vindt dat heel fijn!",
            f"Met een {context['gift']} erbij!",
            "Dat maakt deze dag zo blij!",
            "Sinterklaas is er ook bij!",
            "Dat vindt iedereen heel fijn!",
            "Een feest voor groot en klein!",
            "Dat moet wel heel leuk zijn!",
            f"Want {context['name']} verdient iets bijzonders vandaag!",
            "Een cadeautje met een lach!",
            "Op deze speciale dag!"
        ]
        return random.choice(fallback_lines)

    def get_alternative_words(self, word, context):
        """Genereer alternatieve woorden die passen in de context"""
        try:
            system_message = {
                "role": "system",
                "content": """Je bent een expert in de Nederlandse taal.
                Genereer alternatieve Nederlandse woorden die natuurlijk passen in de context.
                
                Richtlijnen:
                - Kies ALLEEN natuurlijke Nederlandse woorden
                - Let op dat de woorden in de zinsconstructie passen
                - Vermijd letterlijke vertalingen uit het Engels
                - Kies woorden die passen bij Sinterklaasgedichten
                - Houd rekening met formeel/informeel taalgebruik"""
            }
            
            user_message = {
                "role": "user",
                "content": f"""Geef 5 alternatieve Nederlandse woorden voor "{word}" die passen in deze context: "{context}"
                
                De woorden moeten:
                1. Natuurlijk Nederlands zijn
                2. Grammaticaal correct zijn op deze plek
                3. Qua betekenis passen in de context
                4. Ongeveer dezelfde lengte hebben
                5. Passen bij de stijl van een Sinterklaasgedicht
                
                Geef alleen de woorden terug, gescheiden door komma's."""
            }
            
            response = self.call_openai_with_retry(
                messages=[system_message, user_message],
                temperature=0.7,
                max_tokens=50
            )
            
            alternatives = [w.strip() for w in response.split(',')]
            return alternatives[:5]  # Maximaal 5 alternatieven
            
        except Exception as e:
            return []

    def generate_poem(self, context):
        """Genereer een Sinterklaasgedicht met context"""
        is_child = context['gender'] in ['jongen', 'meisje']
        theme = context.get('theme', 'sinterklaas')
        difficulty = context.get('difficulty', 'medium')
        
        try:
            # Bepaal de stijl op basis van moeilijkheidsgraad
            style_guide = {
                'easy': (
                    "- Gebruik eenvoudige woorden en korte zinnen\n"
                    "- Vermijd moeilijke constructies\n"
                    "- Maak het speels en vrolijk\n"
                    "- Gebruik veel concrete voorbeelden\n"
                    "- Houd het tempo vlot"
                ),
                'medium': (
                    "- Gebruik gevarieerd taalgebruik\n"
                    "- Mix eenvoudige en complexere zinnen\n"
                    "- Voeg wat woordgrapjes toe\n"
                    "- Gebruik beeldspraak waar passend\n"
                    "- Zorg voor een goede afwisseling"
                ),
                'hard': (
                    "- Gebruik rijke taal en complexere zinstructuren\n"
                    "- Voeg subtiele humor en woordspelingen toe\n"
                    "- Gebruik creatieve beeldspraak\n"
                    "- Maak verrassende verbanden\n"
                    "- Voeg diepere lagen toe aan het gedicht"
                )
            }[difficulty]

            # Bepaal thema-specifieke elementen
            theme_elements = {
                'sinterklaas': (
                    "- Verwijs naar Sinterklaas en zijn Pieten\n"
                    "- Gebruik traditionele Sinterklaas-elementen\n"
                    "- Verwijs naar pakjesavond en surprises"
                ),
                'verjaardag': (
                    "- Focus op de feestelijke gelegenheid\n"
                    "- Verwijs naar leeftijd en groei\n"
                    "- Gebruik vrolijke, feestelijke taal"
                ),
                'afscheid': (
                    "- Toon waardering voor de persoon\n"
                    "- Verwijs naar gedeelde herinneringen\n"
                    "- Eindig met goede wensen voor de toekomst"
                ),
                'bedankt': (
                    "- Uit oprechte dankbaarheid\n"
                    "- Verwijs naar specifieke acties of momenten\n"
                    "- Maak het persoonlijk en warm"
                )
            }[theme]

            system_message = {
                "role": "system",
                "content": f"""Je bent een Nederlandse dichter, gespecialiseerd in het schrijven van {theme}-gedichten.
                Gebruik ALLEEN natuurlijk, idiomatisch Nederlands - geen vertalingen uit het Engels.
                
                Stijlniveau voor dit gedicht:
                {style_guide}
                
                Thema-specifieke elementen:
                {theme_elements}
                
                Belangrijke taalrichtlijnen:
                - Gebruik Nederlandse zinsconstructies (NIET: 'Hij is aan het spelen games' maar 'Hij speelt graag spelletjes')
                - Gebruik typisch Nederlandse uitdrukkingen en gezegden
                - Vermijd letterlijke vertalingen uit het Engels
                - Let op correcte werkwoordvolgorde in bijzinnen
                - Gebruik natuurlijke Nederlandse woordvolgorde
                
                Stijlrichtlijnen:
                - Maak het persoonlijk en origineel
                - Gebruik humor die past bij het thema en niveau
                - Vermijd clichés
                - Zorg voor een originele, pakkende opening die past bij de context
                - Gebruik rijm (bij voorkeur gepaard rijm: aabb)"""
            }

            user_message = {
                "role": "user",
                "content": f"""Schrijf een origineel {theme}-gedicht in natuurlijk Nederlands voor deze persoon:
                
                Persoon:
                - Naam: {context['name']}
                - {'Kind' if is_child else 'Volwassene'}: {context['gender']}
                - Cadeau: {context['gift']}
                - Hobby's: {context['hobbies']}
                - Surprise: {'ja' if context['is_surprise'] else 'nee'}
                
                Het gedicht moet:
                - Persoonlijk zijn en de context gebruiken
                - 6-8 regels lang zijn
                - Rijmen (aabb)
                - Natuurlijk Nederlands gebruiken
                - Een verrassende opening hebben
                - Humor bevatten die past bij een {'kind' if is_child else 'volwassene'}
                - Passen bij het gekozen thema: {theme}
                - Qua moeilijkheid passen bij niveau: {difficulty}
                
                Begin direct met het gedicht, zonder inleiding."""
            }

            response = self.call_openai_with_retry(
                messages=[system_message, user_message],
                temperature=0.8,
                max_tokens=200
            )
            
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            return lines[:8]  # Maximaal 8 regels
            
        except Exception as e:
            return self.generate_fallback_poem(context)

def main():
    generator = PoemGenerator()
    
    try:
        # Verzamel informatie
        context = generator.get_person_info()
        
        # Genereer gedicht
        poem = generator.generate_poem(context)
        
        if poem:
            print("\nHier is je gedicht:\n")
            print('\n'.join(poem))
            
            # Vraag of de gebruiker nog een gedicht wil
            while True:
                again = input("\nWil je nog een gedicht maken? (ja/nee): ").lower()
                if again in ['ja', 'nee']:
                    break
                print("Antwoord alstublieft met 'ja' of 'nee'")
        
            if again == 'ja':
                main()
    
    except KeyboardInterrupt:
        print("\n\nProgramma onderbroken. Tot ziens!")
    except Exception as e:
        print(f"\nEr is een fout opgetreden: {str(e)}")
        print("Probeer het later opnieuw.")

if __name__ == "__main__":
    print("Welkom bij de Sinterklaas Gedichtengenerator!")
    print("---------------------------------------------")
    main()
