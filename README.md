# Rijmelarij - Sinterklaas Poem Generator

Een interactieve webapplicatie voor het genereren van persoonlijke Sinterklaasgedichten met dynamische regelgeneratie en rijmwoordsuggesties.

## Features

- 🎅 AI-aangedreven Sinterklaasgedicht generator
- 🔄 Regel-voor-regel regeneratie
- 💡 Woordsuggesties met rijmende alternatieven
- 📝 PDF export met handgeschreven stijl
- 🎨 Aanpasbare PDF opmaak:
  - Meerdere handgeschreven lettertypen
  - Instelbare lettergrootte
  - Aanpasbare regelafstand
  - Versie beheer per persoon

## Installatie

1. Clone de repository:
```bash
git clone https://github.com/[username]/rijmelarij.git
cd rijmelarij
```

2. Maak een virtuele omgeving aan en activeer deze:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installeer de benodigde packages:
```bash
pip install -r requirements.txt
```

4. Maak een `.env` bestand aan met je OpenAI API key:
```
OPENAI_API_KEY=jouw_api_key_hier
```

## Gebruik

1. Start de Flask applicatie:
```bash
python app.py
```

2. Open een browser en ga naar `http://localhost:5001`

3. Vul een naam in en genereer een gedicht

4. Pas het gedicht aan met de beschikbare tools:
   - Klik op 🔄 om een regel opnieuw te genereren
   - Klik op woorden voor alternatieve suggesties
   - Pas de PDF opmaak aan in het configuratiepaneel

5. Sla het gedicht op als PDF met de 'Bewaar' knop

## Structuur

- `app.py` - Flask webapplicatie
- `poem_generator.py` - Gedichtgeneratie logica
- `pdf_generator.py` - PDF creatie en styling
- `rijm_checker.py` - Rijmwoord validatie
- `templates/` - HTML templates
  - `index.html` - Frontend interface

## Technische Details

- Python 3.11+
- Flask voor de webserver
- OpenAI GPT-4 voor gedichtgeneratie
- FPDF2 voor PDF generatie
- Handgeschreven fonts van Google Fonts

## Bijdragen

Pull requests zijn welkom! Voor grote wijzigingen, open eerst een issue om te bespreken wat je wilt veranderen.

## Licentie

[MIT](https://choosealicense.com/licenses/mit/)
