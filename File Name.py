from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    # Health check endpoint to verify the service is running
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)

