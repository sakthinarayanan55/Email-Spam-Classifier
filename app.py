
import os

from flask import Flask, jsonify, render_template, request, send_from_directory

from src.predictor import SpamPredictor

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024   # 1 MB request limit

# Train automatically on first start if no model exists (handy for hosting)
if not os.path.exists(os.path.join("models", "best_model.joblib")):
    import train
    train.main()

predictor = SpamPredictor()


@app.route("/")
def index():
    return render_template("index.html", metrics=predictor.metrics)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or request.form
    text = data.get("text", "")
    try:
        return jsonify(predictor.predict(text))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/metrics")
def metrics():
    return jsonify(predictor.metrics)


@app.route("/reports/<path:filename>")
def reports(filename):
    return send_from_directory("reports", filename)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
