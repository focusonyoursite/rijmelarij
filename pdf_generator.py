import os
from fpdf import FPDF
import requests
from datetime import datetime

class PoemPDFGenerator:
    FONTS = {
        'homemade-apple': {
            'name': 'Homemade Apple',
            'url': "https://github.com/google/fonts/raw/main/apache/homemadeapple/HomemadeApple-Regular.ttf",
            'filename': 'HomemadeApple-Regular.ttf'
        },
        'caveat': {
            'name': 'Caveat',
            'url': "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat-Regular.ttf",
            'filename': 'Caveat-Regular.ttf'
        },
        'indie-flower': {
            'name': 'Indie Flower',
            'url': "https://github.com/google/fonts/raw/main/ofl/indieflower/IndieFlower-Regular.ttf",
            'filename': 'IndieFlower-Regular.ttf'
        },
        'dancing-script': {
            'name': 'Dancing Script',
            'url': "https://github.com/google/fonts/raw/main/ofl/dancingscript/DancingScript-Regular.ttf",
            'filename': 'DancingScript-Regular.ttf'
        }
    }

    def __init__(self):
        self.fonts_dir = os.path.join('/tmp' if os.environ.get('VERCEL') else os.path.dirname(__file__), 'fonts')
        os.makedirs(self.fonts_dir, exist_ok=True)
        self.available_fonts = self.setup_fonts()
    
    def setup_fonts(self):
        """Download and setup all fonts"""
        available_fonts = {}
        for font_id, font_info in self.FONTS.items():
            font_path = os.path.join(self.fonts_dir, font_info['filename'])
            if not os.path.exists(font_path):
                try:
                    response = requests.get(font_info['url'])
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    available_fonts[font_id] = {
                        'name': font_info['name'],
                        'path': font_path
                    }
                except Exception as e:
                    print(f"Kon lettertype {font_info['name']} niet downloaden: {e}")
                    continue
            else:
                available_fonts[font_id] = {
                    'name': font_info['name'],
                    'path': font_path
                }
        return available_fonts
    
    def get_available_fonts(self):
        """Return list of available fonts"""
        return {font_id: info['name'] for font_id, info in self.available_fonts.items()}

    def generate_pdf(self, poem_lines, formatting=None, output_path=None):
        """Generate a PDF with the poem using specified formatting"""
        if formatting is None:
            formatting = {}
        
        # Default formatting values
        font_id = formatting.get('font', 'homemade-apple')
        title_size = float(formatting.get('title_size', 16))
        poem_size = float(formatting.get('poem_size', 12))
        line_spacing = float(formatting.get('line_spacing', 1.5))
        margin = float(formatting.get('margin', 20))
        
        # Create PDF
        pdf = FPDF(orientation='P', unit='mm', format='A5')
        pdf.add_page()
        
        # Add the selected font
        if font_id in self.available_fonts:
            font_path = self.available_fonts[font_id]['path']
            pdf.add_font("CustomFont", "", font_path, uni=True)
            font_family = "CustomFont"
        else:
            font_family = "Helvetica"
        
        # Set background color
        pdf.set_fill_color(252, 252, 250)
        pdf.rect(0, 0, 148, 210, 'F')
        
        # Add decorative border
        pdf.set_draw_color(139, 69, 19)
        pdf.rect(margin, margin, 148 - 2*margin, 210 - 2*margin)
        
        # Add title
        pdf.set_font(font_family, size=title_size)
        pdf.set_text_color(139, 69, 19)
        pdf.cell(0, 20, "Sinterklaasgedicht", align='C', ln=True)
        
        # Add space before poem
        pdf.ln(15)
        
        # Add poem text
        pdf.set_font(font_family, size=poem_size)
        pdf.set_text_color(0, 0, 0)
        
        # Calculate line spacing
        available_height = 130
        num_lines = len(poem_lines)
        base_line_height = poem_size * 0.5  # Convert font size to mm
        line_height = base_line_height * line_spacing
        
        # Calculate effective width for poem text (accounting for margins)
        effective_width = 148 - 2*margin
        
        for line in poem_lines:
            # Get width of text to calculate x position for centering
            line_width = pdf.get_string_width(line)
            x_offset = (effective_width - line_width) / 2 + margin
            
            # Move to centered position
            pdf.set_x(x_offset)
            pdf.cell(line_width, line_height, line, align='C')
            pdf.ln(line_height * 1.2)  # Add extra space between lines
        
        # Add space before footer
        pdf.ln(10)
        
        # Add footer
        pdf.set_font(font_family, size=8)
        pdf.set_text_color(139, 69, 19)
        pdf.cell(0, 10, "❦ Sint & Piet ❦", align='C', ln=True)
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.join(os.path.dirname(__file__), 'pdfs')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f'sinterklaasgedicht_{timestamp}.pdf')
        
        # Save the PDF
        pdf.output(output_path)
        return output_path
