from flask import Flask, request, jsonify, send_file, render_template
from poem_generator import PoemGenerator
from pdf_generator import PoemPDFGenerator
import os
import datetime
import re
import json
from werkzeug.middleware.proxy_fix import ProxyFix
import io

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
generator = PoemGenerator()
pdf_generator = PoemPDFGenerator()

# For Vercel deployment - use /tmp for file storage
STORAGE_DIR = '/tmp' if os.environ.get('VERCEL') else os.path.dirname(__file__)

# Update paths to use STORAGE_DIR
VERSION_FILE = os.path.join(STORAGE_DIR, 'poem_versions.json')
POEMS_DIR = os.path.join(STORAGE_DIR, 'poems')
PDFS_DIR = os.path.join(STORAGE_DIR, 'pdfs')
PREVIEWS_DIR = os.path.join(STORAGE_DIR, 'previews')
FONTS_DIR = os.path.join(STORAGE_DIR, 'fonts')

# Create necessary directories
for directory in [POEMS_DIR, PDFS_DIR, PREVIEWS_DIR, FONTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Dictionary to store version numbers

def load_versions():
    """Load version numbers from file"""
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_versions(versions):
    """Save version numbers to file"""
    try:
        with open(VERSION_FILE, 'w') as f:
            json.dump(versions, f)
    except:
        pass  # Fail silently on Vercel due to read-only filesystem

def get_next_version(name):
    """Get next version number for a given name"""
    versions = load_versions()
    current_version = versions.get(name, 0)
    next_version = current_version + 1
    versions[name] = next_version
    save_versions(versions)
    return next_version

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    # Replace spaces with underscores and remove invalid characters
    return re.sub(r'[<>:"/\\|?*]', '', filename.replace(' ', '_'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_poem():
    try:
        data = request.get_json()
        poem = generator.generate_poem(data)
        
        if not poem:
            return jsonify({
                'success': False,
                'error': 'Kon geen gedicht genereren'
            })
        
        # poem is already a list of lines, no need to split
        return jsonify({
            'success': True,
            'poem': poem
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/regenerate_line', methods=['POST'])
def regenerate_line():
    """Endpoint voor het regenereren van een enkele regel"""
    try:
        data = request.get_json()
        line_index = data.get('lineIndex')
        previous_line = data.get('previousLine', '')
        context = data.get('context', {})
        target_words = data.get('targetWords')
        
        if not context:
            return jsonify({
                'success': False,
                'error': 'Geen context meegegeven'
            })
        
        new_line = generator.generate_single_line(
            previous_line=previous_line,
            context=context,
            target_words=target_words
        )
        
        return jsonify({
            'success': True,
            'new_line': new_line
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/regenerate_line_v2', methods=['POST'])
def regenerate_line_v2():
    data = request.get_json()
    line_index = data.get('line_index')
    current_lines = data.get('current_lines')
    
    try:
        new_line = generator.regenerate_line(line_index, current_lines)
        return jsonify({'new_line': new_line})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_alternative_words', methods=['POST'])
def get_alternative_words():
    """Endpoint voor het ophalen van alternatieve woorden"""
    try:
        data = request.get_json()
        word = data.get('word', '')
        context = data.get('context', '')
        
        if not word or not context:
            return jsonify({
                'success': False,
                'error': 'Geen woord of context meegegeven'
            })
        
        alternatives = generator.get_alternative_words(word, context)
        
        return jsonify({
            'success': True,
            'alternatives': alternatives
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/get_rhyming_words', methods=['POST'])
def get_rhymes():
    word = request.json.get('word', '')
    rhyming_words = get_rhyming_words(word)
    return jsonify({'rhyming_words': rhyming_words})

@app.route('/get_rhyming_words_v2', methods=['POST'])
def get_rhyming_words_v2():
    data = request.get_json()
    word = data.get('word')
    
    try:
        rhyming_words = generator.suggest_rhyming_words(word)
        return jsonify({'rhyming_words': rhyming_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_poem', methods=['POST'])
def save_poem():
    """Endpoint voor het opslaan van een gedicht"""
    try:
        data = request.get_json()
        lines = data.get('lines', [])
        name = data.get('name', '').strip()
        formatting = data.get('formatting', {})
        
        if not lines:
            return jsonify({
                'success': False,
                'error': 'Geen gedichtregels meegegeven'
            })
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Geen naam opgegeven'
            })
        
        # Get next version number for this name
        version = get_next_version(name)
        
        # Create safe filename
        safe_name = sanitize_filename(name)
        filename = f'{safe_name}_Gedicht_{version}'
        
        # Save text version
        txt_filepath = os.path.join(POEMS_DIR, f'{filename}.txt')
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        # Generate PDF version
        pdf_filepath = os.path.join(PDFS_DIR, f'{filename}.pdf')
        pdf_generator.generate_pdf(lines, formatting, pdf_filepath)
        
        return jsonify({
            'success': True,
            'txt_filename': f'{filename}.txt',
            'pdf_path': f'{filename}.pdf'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    """Endpoint voor het downloaden van een PDF gedicht"""
    try:
        pdf_dir = PDFS_DIR
        return send_file(
            os.path.join(pdf_dir, filename),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/get_fonts', methods=['GET'])
def get_fonts():
    """Get list of available handwritten fonts"""
    try:
        fonts = pdf_generator.get_available_fonts()
        return jsonify({
            'success': True,
            'fonts': fonts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/preview_pdf', methods=['POST'])
def preview_pdf():
    """Generate a preview PDF with current formatting"""
    try:
        data = request.get_json()
        lines = data.get('lines', [])
        formatting = data.get('formatting', {})
        
        if not lines:
            return jsonify({
                'success': False,
                'error': 'Geen gedichtregels meegegeven'
            })
        
        # Generate preview PDF
        preview_dir = PREVIEWS_DIR
        os.makedirs(preview_dir, exist_ok=True)
        
        # Use timestamp to ensure unique filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        preview_path = os.path.join(preview_dir, f'preview_{timestamp}.pdf')
        
        pdf_generator.generate_pdf(lines, formatting, preview_path)
        
        return jsonify({
            'success': True,
            'preview_path': os.path.basename(preview_path)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/preview_pdf_v2', methods=['POST'])
def preview_pdf_v2():
    data = request.get_json()
    lines = data.get('lines')
    
    try:
        pdf_bytes = pdf_generator.generate_pdf(lines)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=False,
            download_name='preview.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<filename>')
def get_preview(filename):
    """Serve preview PDF file"""
    try:
        preview_dir = PREVIEWS_DIR
        return send_file(
            os.path.join(preview_dir, filename),
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.debug = False
    app.run(port=5001)
