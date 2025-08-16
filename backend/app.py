from flask import Flask, jsonify
from flask_cors import CORS
from database import test_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return jsonify({"message": "Rent Check API is running!"})

@app.route('/health')
def health():
    db_status = test_db_connection()
    return jsonify({
        "status": "healthy",
        "database": "connected" if db_status else "disconnected"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)