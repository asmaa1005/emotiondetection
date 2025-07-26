from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model  # type: ignore
from tensorflow.keras.preprocessing.text import tokenizer_from_json  # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences  # type: ignore
import numpy as np
import json

app = Flask(__name__)

# Load emotion model
emotion_model = load_model("assets/model/final_trained_model_combined.h5")

# Load tokenizer
with open('assets/tokenizer/tokenizer.json', 'r') as f:
    tokenizer_json = f.read()
    tokenizer = tokenizer_from_json(tokenizer_json)

# Constants
MAX_LEN = 100
emotion_labels = ['fearful', 'surprised' 'frustrated', 'neutral', 'anger', 'sad', 'happy', 'excited']

# Map emotion -> sentiment + emoji
emotion_map = {
    'fearful':    {'sentiment': '2', 'emoji': '😨😱'},
    'sad':        {'sentiment': '2', 'emoji': '😢😔'},
    'anger':      {'sentiment': '2', 'emoji': '😠🤬'},
    'excited':    {'sentiment': '1', 'emoji': '😃😁'},
    'neutral':    {'sentiment': '0', 'emoji': '😐'},
    'frustrated': {'sentiment': '2', 'emoji': '😤'},
    'happy':      {'sentiment': '1', 'emoji': '😊🤗'},
    'surprised':  {'sentiment': '2', 'emoji': '😯😦'},
}

# Preprocess input
def preprocess(text):
    sequence = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(sequence, maxlen=MAX_LEN, padding='post', truncating='post')
    return padded

# Predict route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    input_tensor = preprocess(text)
    emotion_pred = emotion_model.predict(input_tensor)[0]
    emotion_idx = np.argmax(emotion_pred)
    emotion = emotion_labels[emotion_idx] if emotion_idx < len(emotion_labels) else "unknown"

    mapped = emotion_map.get(emotion, {'sentiment': 'unknown', 'emoji': 'unknown'})
    sentiment = mapped['sentiment']
    emoji = mapped['emoji']

    return jsonify({
        "emotion": emotion,
        "sentiment": sentiment,
        "emoji": emoji
    })

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
