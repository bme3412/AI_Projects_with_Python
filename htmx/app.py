from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    # Process file...
    return jsonify({"message": "File processed successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
