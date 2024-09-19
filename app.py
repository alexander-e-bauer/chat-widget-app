from flask import Flask, request, jsonify
from flask_cors import CORS
import config

openai_client = config.openai_client
app = Flask(__name__)
CORS(app)

def chat_completion(user_input, system_input="you are a helpful assistant", image_path=None, tools=None,
                    streaming=False):
    if image_path is None:
        messages = [
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_input}
        ]
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=streaming
        )
    else:
        messages = [
            {"role": "system", "content": system_input},
            {"role": "user", "content": [
                {"type": "image", "data": image_path},
                {"type": "text", "text": user_input}
            ]}
        ]
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=streaming
        )
    if not streaming:
        output = completion.choices[0].message.content
        print(output)
        return output
    else:
        output = ""
        for chunk in completion:
            output += str(chunk.choices[0].delta.content)
            print(chunk.choices[0].delta.content)
        print(output)
        return output


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    # Here you would typically process the message and generate a response
    # For this example, we'll just echo the message back
    completion = chat_completion(user_input=message)
    response = f"{completion}"
    return jsonify({"response": response})



