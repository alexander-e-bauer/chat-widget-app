from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    # Here you would typically process the message and generate a response
    # For this example, we'll just echo the message back
    response = f"You said: {message}"
    return jsonify({"response": response})

