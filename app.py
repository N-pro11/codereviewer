
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from groq import Groq  

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print("API KEY LOADED:", api_key is not None)

# Initialize Groq client
client = Groq(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')  # Make sure templates/index.html exists

@app.route('/review', methods=['POST'])
def review():
    code = request.json.get('code')
    
    if not code:
        return jsonify({"error": "Code is required"}), 400

    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or llama3-70b-8192, gemma-7b-it, etc.
            messages=[
                {"role": "system", "content": "You are a code reviewer. Keep feedback concise, structured, and under 800 tokens."},
                {"role": "user", "content": f"Review the following code:\n\n{code}\n\nProvide feedback on quality, style, and improvements."}
            ],
            temperature=0.5,
            max_tokens=3000
        )
        try:
            choice = chat_completion.choices[0].message
            feedback = getattr(choice, "content", "").strip()
            if not feedback:
                feedback = "No feedback returned from the model."
        except (AttributeError, IndexError):
            feedback = "unexpected API response format."
        
        print("Feedback received:", feedback)  
        return jsonify({"feedback": feedback}), 200

    except Exception as e:
        print("Groq API error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


