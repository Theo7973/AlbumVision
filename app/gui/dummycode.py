from flask import Flask, request, jsonify
import openai
import base64
from PIL import Image
import io

openai.api_key = "your-api-key"

app = Flask(__name__)

@app.route('/describe', methods=['POST'])
def describe_image():
    file = request.files['image']
    image_bytes = file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image for accessibility."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=300
    )

    return jsonify({
        "description": response.choices[0].message['content']
    })

if __name__ == '__main__':
    app.run(port=5000) 

_________________________________________________________________________________________________________________

def on_image_clicked(self, image_path):
try:
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()

    response = requests.post(
        "http://localhost:5000/describe",
        files={"image": img_file}
    )

    if response.ok:
        description = response.json().get("description", "No description returned.")
    else:
        description = f"API Error: {response.status_code}"

    self.img_info.setText(f"AI Description:\n\n{description}")

except Exception as e:
    self.img_info.setText(f"Error generating AI description:\n{str(e)}")