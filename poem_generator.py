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
        
        return {
            "name": name,
            "gender": gender,
            "gift": gift,
            "hobbies": hobbies,
            "is_surprise": is_surprise == 'ja'
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
        """Suggereer rijmwoorden voor een gegeven woord"""
        if not self.use_rhyme_check:
            return []
        
        try:
            rhyming_words = self.rijmwoorden.get_rhyming_words(word.lower())
            if rhyming_words:
                print(f"\nGevonden rijmwoorden voor '{word}':")
                # Toon maximaal 5 rijmwoorden
                shown_words = rhyming_words[:5]
                for rhyme_word in shown_words:
                    print(f"- {rhyme_word}")
                if len(rhyming_words) > 5:
                    print(f"... en nog {len(rhyming_words) - 5} andere rijmwoorden")
            return rhyming_words
        except Exception as e:
            print(f"Fout bij het zoeken naar rijmwoorden: {str(e)}")
            return []

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
        if not previous_line:
            return self.generate_fallback_line(context)
            
        try:
            last_word = previous_line.split()[-1].strip('.,!?').lower()
            rhyming_words = self.rijmwoorden.get_rhyming_words(last_word) if self.use_rhyme_check else []
            
            system_message = {
                "role": "system",
                "content": """Je bent een ervaren Sinterklaasgedichtenschrijver.
                Genereer één regel die rijmt op de vorige regel.
                Gebruik een natuurlijke, vloeiende schrijfstijl."""
            }
            
            length_hint = ""
            if target_words:
                length_hint = f"\nDe regel moet ongeveer {target_words} woorden bevatten."
            
            rhyme_hint = ""
            if rhyming_words:
                rhyme_hint = f"\nMogelijke rijmwoorden: {', '.join(rhyming_words[:5])}"
            
            user_message = {
                "role": "user",
                "content": f"""Schrijf één regel die rijmt op: "{previous_line}"
                
                Context:
                - Naam: {context['name']}
                - Cadeau: {context['gift']}
                - Hobby's: {context['hobbies']}{length_hint}{rhyme_hint}
                
                Geef alleen de nieuwe regel terug, zonder extra tekst."""
            }
            
            response = self.call_openai_with_retry(
                messages=[system_message, user_message],
                temperature=0.7,
                max_tokens=50
            )
            
            return response
            
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
                "content": """Je bent een expert in het Nederlands.
                Genereer alternatieve woorden die passen in de context.
                De woorden moeten natuurlijk klinken en betekenisvol zijn."""
            }
            
            user_message = {
                "role": "user",
                "content": f"""Geef 5 alternatieve woorden voor "{word}" die passen in deze context: "{context}"
                
                De woorden moeten:
                1. Grammaticaal correct zijn op deze plek
                2. Betekenisvol zijn in de context
                3. Ongeveer dezelfde lengte hebben
                
                Geef alleen de woorden terug, gescheiden door komma's."""
            }
            
            response = self.call_openai_with_retry(
                messages=[system_message, user_message],
                temperature=0.7,
                max_tokens=50
            )
            
            alternatives = [w.strip() for w in response.choices[0].message.content.split(',')]
            return alternatives[:5]  # Maximaal 5 alternatieven
            
        except Exception as e:
            return []

    def generate_poem(self, context):
        """Genereer een Sinterklaasgedicht met context"""
        is_child = context['gender'] in ['jongen', 'meisje']
        
        try:
            system_message = {
                "role": "system",
                "content": """Je bent een ervaren en originele Sinterklaasgedichtenschrijver.
                Schrijf een origineel Sinterklaasgedicht dat persoonlijk en verrassend is.
                Vermijd clichés zoals 'Sinterklaas zat te denken, wat hij X zou schenken'.
                Begin met een originele, pakkende opening die past bij de context.
                Gebruik humor en verrassende wendingen.
                Het gedicht moet rijmen (bij voorkeur gepaard rijm: aabb)."""
            }

            # Voeg voorbeelden toe van goede openingen
            examples = """Hier zijn voorbeelden van originele openingen:
            - Een verhaal over de hobby's van de persoon
            - Een grappige situatie met het cadeau
            - Een verrassende observatie over de persoon
            - Een actuele gebeurtenis die relevant is
            - Een leuke anekdote over de persoon
            
            Vermijd standaard Sinterklaasgedicht-openingen."""

            user_message = {
                "role": "user",
                "content": f"""Schrijf een origineel Sinterklaasgedicht voor deze persoon:
                
                Context:
                - Naam: {context['name']}
                - Gender: {context['gender']}
                - Cadeau: {context['gift']}
                - Hobby's: {context['hobbies']}
                - Is het een surprise?: {'ja' if context['is_surprise'] else 'nee'}
                
                {examples}
                
                Het gedicht moet:
                - Persoonlijk zijn en de context gebruiken
                - 6-8 regels lang zijn
                - {'Kindvriendelijk zijn' if is_child else 'Geschikt zijn voor een volwassene'}
                - Rijmen (bij voorkeur gepaard rijm: aabb)
                - Een originele opening hebben
                - Humor bevatten
                
                Geef alleen het gedicht terug, zonder extra tekst."""
            }

            response = self.call_openai_with_retry(
                messages=[system_message, user_message],
                temperature=0.8,
                max_tokens=200
            )

            poem = response.choices[0].message.content.strip().split('\n')
            return [line.strip() for line in poem if line.strip()]

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
