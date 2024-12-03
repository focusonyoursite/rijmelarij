import os
from fpdf import FPDF
import requests
from datetime import datetime

class PoemPDFGenerator:
    FONTS = {
        'homemade-apple': {
            'name': 'Homemade Apple',
            'url': "https://fonts.gstatic.com/s/homemadeapple/v18/Qw3EZQFXECDrI2q789EKQZJob3x9.ttf",
            'filename': 'HomemadeApple-Regular.ttf'
        },
        'caveat': {
            'name': 'Caveat',
            'url': "https://fonts.gstatic.com/s/caveat/v17/WnznHAc5bAfYB2QRah7pcpNvOx-pjfJ9SIc.ttf",
            'filename': 'Caveat-Regular.ttf'
        },
        'indie-flower': {
            'name': 'Indie Flower',
            'url': "https://fonts.gstatic.com/s/indieflower/v17/m8JVjfNVeKWVnh3QMuKkFcZVaUuH.ttf",
            'filename': 'IndieFlower-Regular.ttf'
        },
        'dancing-script': {
            'name': 'Dancing Script',
            'url': "https://fonts.gstatic.com/s/dancingscript/v24/If2cXTr6YS-zF4S-kcSWSVi_sxjsohD9F50Ruu7BMSo3Sup5.ttf",
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
            try:
                if not os.path.exists(font_path):
                    print(f"Downloading font: {font_info['name']}")
                    response = requests.get(font_info['url'], headers={'User-Agent': 'Mozilla/5.0'})
                    response.raise_for_status()  # Raise an error for bad status codes
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                
                # Verify the font file
                with open(font_path, 'rb') as f:
                    header = f.read(4)
                    if header.startswith(b'\x00\x01\x00\x00') or header.startswith(b'true') or header.startswith(b'OTTO'):
                        available_fonts[font_id] = {
                            'name': font_info['name'],
                            'path': font_path
                        }
                    else:
                        print(f"Invalid font file for {font_info['name']}")
                        if os.path.exists(font_path):
                            os.remove(font_path)
                        continue
                        
            except Exception as e:
                print(f"Error with font {font_info['name']}: {str(e)}")
                if os.path.exists(font_path):
                    os.remove(font_path)
                continue
                
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
        
        # Try to use the selected font, fall back to Arial if not available
        font_family = "Arial"
        if font_id in self.available_fonts:
            try:
                font_path = self.available_fonts[font_id]['path']
                # Verify font file exists and is readable
                if os.path.exists(font_path) and os.access(font_path, os.R_OK):
                    pdf.add_font("CustomFont", "", font_path, uni=True)
                    font_family = "CustomFont"
                else:
                    print(f"Font file not accessible: {font_id}")
            except Exception as e:
                print(f"Error loading font {font_id}: {str(e)}")
        
        # Set background color
        pdf.set_fill_color(252, 252, 250)
        pdf.rect(0, 0, 148, 210, 'F')
        
        # Add decorative border
        pdf.set_draw_color(139, 69, 19)
        pdf.rect(margin, margin, 148 - 2*margin, 210 - 2*margin)
        
        # Add title
        pdf.set_font(font_family, size=int(title_size))
        pdf.set_text_color(139, 69, 19)
        pdf.cell(0, 20, "Sinterklaasgedicht", align='C', ln=True)
        
        # Add space before poem
        pdf.ln(15)
        
        # Add poem text
        pdf.set_font(font_family, size=int(poem_size))
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

    def generate_pdf_bytes(self, lines, formatting=None):
        """Generate PDF in memory and return the bytes"""
        # Create PDF with Unicode support
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Apply formatting if provided
        if formatting:
            font_family = formatting.get('font', 'Arial')
            title_size = int(formatting.get('title_size', 16))
            poem_size = int(formatting.get('poem_size', 12))
            line_spacing = float(formatting.get('line_spacing', 1.5))
        else:
            font_family = 'Arial'
            title_size = 16
            poem_size = 12
            line_spacing = 1.5
        
        # Add a page (A5 format)
        pdf.add_page(format='A5')
        
        # Set margins (2mm)
        margin = 2
        pdf.set_margins(margin, margin)
        
        # Add font if it's one of our custom fonts
        if font_family in self.FONTS:
            font_path = os.path.join(self.fonts_dir, self.FONTS[font_family]['filename'])
            try:
                pdf.add_font(font_family, '', font_path, uni=True)
            except Exception as e:
                print(f"Error loading font {font_family}: {str(e)}")
                font_family = 'Arial'
        
        # Set background color
        pdf.set_fill_color(252, 252, 250)
        pdf.rect(0, 0, 148, 210, 'F')
        
        # Add decorative border
        pdf.set_draw_color(139, 69, 19)
        pdf.rect(margin, margin, 148 - 2*margin, 210 - 2*margin)
        
        # Add title
        pdf.set_font(font_family, size=int(title_size))
        pdf.set_text_color(139, 69, 19)
        pdf.cell(0, 20, "Sinterklaasgedicht", align='C', ln=True)
        
        # Add space before poem
        pdf.ln(15)
        
        # Add poem text
        pdf.set_font(font_family, size=int(poem_size))
        pdf.set_text_color(0, 0, 0)
        
        # Calculate line spacing
        available_height = 130
        num_lines = len(lines)
        base_line_height = poem_size * 0.5  # Convert font size to mm
        line_height = base_line_height * line_spacing
        
        # Calculate effective width for poem text (accounting for margins)
        effective_width = 148 - 2*margin
        
        for line in lines:
            # Get width of text to calculate x position for centering
            line_width = pdf.get_string_width(line)
            x_offset = (effective_width - line_width) / 2 + margin
            
            # Move to centered position
            pdf.set_x(x_offset)
            pdf.multi_cell(line_width, line_height, line, align='C')
            pdf.ln(line_height * 0.2)  # Add extra space between lines
        
        # Add space before footer
        pdf.ln(10)
        
        # Add footer
        pdf.set_font(font_family, size=8)
        pdf.set_text_color(139, 69, 19)
        pdf.cell(0, 10, "❦ Sint & Piet ❦", align='C', ln=True)
        
        # Return PDF bytes directly
        return bytes(pdf.output(dest='S'))
