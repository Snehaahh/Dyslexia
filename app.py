from flask import Flask, render_template, request, redirect, url_for, send_file, session, jsonify
from flask import send_from_directory
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import openai
from gtts import gTTS
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import tempfile
import shutil

# Fix for PIL Image ANTIALIAS deprecation
try:
    from PIL import Image
    # Add ANTIALIAS if it doesn't exist (for newer Pillow versions)
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
except ImportError:
    pass

UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'static/audio'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'dyslexia_friendly_key_2024'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# Configure OpenAI API (no need to set here, GrammarCorrector will handle)

# Register OpenDyslexic font
font_path = 'fonts/OpenDyslexic-Regular.ttf'
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('OpenDyslexic', font_path))

# Session history storage (in-memory for simplicity)
session_history = {}

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session_history[session['session_id']] = []
    return session['session_id']

def add_to_history(session_id, data):
    if session_id not in session_history:
        session_history[session_id] = []
    session_history[session_id].append({
        'timestamp': datetime.now().isoformat(),
        'original_text': data.get('original_text', ''),
        'corrected_text': data.get('corrected_text', ''),
        'filename': data.get('filename', ''),
        'audio_file': data.get('audio_file', '')
    })

def correct_grammar_openai(text):
    """Correct grammar using OpenAI GPT-3.5/4 with context awareness"""
    try:
        from grammar import GrammarCorrector
        api_key = "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"
        corrector = GrammarCorrector(api_key)
        result = corrector.correct_text(text)
        corrected_text = result.get('corrected_text', text)
        corrections_data = result.get('corrections', [])
        corrections = []
        for correction in corrections_data:
            corrections.append({
                'original': correction.get('original', ''),
                'corrected': correction.get('corrected', ''),
                'message': correction.get('explanation', ''),
                'start': 0,
                'end': 0,
                'category': 'Grammar/Spelling'
            })
        return corrected_text, corrections
    except Exception as e:
        print(f"OpenAI Grammar Correction Error: {e}")
        return text, []

def generate_audio(text, filename):
    """Generate audio file using gTTS"""
    try:
        # Create audio directory if it doesn't exist
        os.makedirs(AUDIO_FOLDER, exist_ok=True)
        
        audio_filename = f"audio_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(audio_path)
        
        return audio_filename
    except Exception as e:
        print(f"Audio generation error: {e}")
        return None

def generate_pdf(original_text, corrected_text, corrections, filename):
    """Generate dyslexia-friendly PDF with corrections"""
    try:
        # Create PDF directory if it doesn't exist
        pdf_dir = 'static/pdfs'
        os.makedirs(pdf_dir, exist_ok=True)
        
        pdf_filename = f"corrected_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        
        # Define dyslexia-friendly styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DyslexiaTitle',
            parent=styles['Heading1'],
            fontName='OpenDyslexic' if 'OpenDyslexic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        normal_style = ParagraphStyle(
            'DyslexiaNormal',
            parent=styles['Normal'],
            fontName='OpenDyslexic' if 'OpenDyslexic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=14,
            spaceAfter=12,
            leading=20,
            textColor=colors.black
        )
        
        correction_style = ParagraphStyle(
            'DyslexiaCorrection',
            parent=styles['Normal'],
            fontName='OpenDyslexic' if 'OpenDyslexic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=12,
            spaceAfter=8,
            leading=16,
            textColor=colors.darkred,
            leftIndent=20
        )
        
        # Add title
        story.append(Paragraph("Dyslexia-Friendly Notes Correction", title_style))
        story.append(Spacer(1, 20))
        
        # Add original text
        story.append(Paragraph("<b>Original Text:</b>", normal_style))
        story.append(Paragraph(original_text, normal_style))
        story.append(Spacer(1, 20))
        
        # Add corrections section
        if corrections:
            story.append(Paragraph("<b>Grammar Corrections:</b>", normal_style))
            for i, correction in enumerate(corrections, 1):
                correction_text = f"<b>{i}.</b> <font color='red'>{correction['original']}</font> → <font color='green'>{correction['corrected']}</font><br/>"
                correction_text += f"<i>Explanation:</i> {correction['message']}"
                story.append(Paragraph(correction_text, correction_style))
            story.append(Spacer(1, 20))
        
        # Add corrected text
        story.append(Paragraph("<b>Corrected Text:</b>", normal_style))
        story.append(Paragraph(corrected_text, normal_style))
        
        doc.build(story)
        return pdf_filename
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    session_id = create_session_id()
    
    if request.method == 'POST':
        if 'note_image' not in request.files:
            return "No file part"
        file = request.files['note_image']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('process', filename=filename))
    
    # Get session history
    history = session_history.get(session_id, [])
    return render_template('index.html', history=history)

@app.route('/process/<filename>')
def process(filename):
    session_id = create_session_id()
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return "File not found"
    
    # Extract text using pytesseract with PIL
    try:
        # Open image using PIL
        image = Image.open(file_path)
        
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance image for better OCR
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Extract text using pytesseract
        original_text = pytesseract.image_to_string(image, config='--psm 6')
        
        # Clean up the text
        original_text = original_text.strip()
        
        if not original_text:
            # Try with different PSM mode if no text found
            original_text = pytesseract.image_to_string(image, config='--psm 3')
            original_text = original_text.strip()
            
        if not original_text:
            # Try with original image if still no text
            original_image = Image.open(file_path)
            original_text = pytesseract.image_to_string(original_image, config='--psm 6')
            original_text = original_text.strip()
            
    except Exception as e:
        print(f"OCR Error: {e}")
        return f"Error during text extraction: {str(e)}"
    
    # Clean up text
    import re
    original_text = re.sub(r'\s+([.,;:?!])', r'\1', original_text)
    original_text = re.sub(r'\s{2,}', ' ', original_text)
    
    # Correct grammar using OpenAI
    corrected_text, corrections = correct_grammar_openai(original_text)
    
    # Generate audio
    audio_filename = generate_audio(corrected_text, filename)
    
    # Generate PDF
    pdf_filename = generate_pdf(original_text, corrected_text, corrections, filename)
    
    # Add to session history
    history_entry = {
        'original_text': original_text,
        'corrected_text': corrected_text,
        'filename': filename,
        'audio_file': audio_filename,
        'pdf_file': pdf_filename,
        'corrections': corrections
    }
    add_to_history(session_id, history_entry)
    
    return render_template('result.html', 
                         original_text=original_text,
                         corrected_text=corrected_text,
                         corrections=corrections,
                         filename=filename,
                         audio_file=audio_filename,
                         pdf_file=pdf_filename)

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory('static/pdfs', filename)

@app.route('/download_audio/<filename>')
def download_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename, as_attachment=True)

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_from_directory('static/pdfs', filename, as_attachment=True)

@app.route('/history')
def history():
    session_id = create_session_id()
    history = session_history.get(session_id, [])
    return render_template('history.html', history=history)

@app.route('/clear_history')
def clear_history():
    session_id = create_session_id()
    if session_id in session_history:
        del session_history[session_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    os.makedirs('static/pdfs', exist_ok=True)
    
    app.run(debug=True)
