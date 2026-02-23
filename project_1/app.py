# Create a basic Flask application with a health check route
from flask import Flask

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)# Existing code includes a Flask app instance and a health_check route.
# Adding a new route '/status' that returns JSON {'status': 'ok'}.

from flask import jsonify

@app.route('/status')
def status():
    return jsonify({'status': 'ok'})