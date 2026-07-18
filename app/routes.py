from flask import Flask, render_template, request, jsonify
from app.services.vin_decoder import decode_vin

# Create a Flask app instance
app = Flask(__name__)

# Register application routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_vin():
    vin = request.form.get('vin')
    if not vin:
        return jsonify({'error': 'VIN is required'}), 400

    try:
        result = decode_vin(vin)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500