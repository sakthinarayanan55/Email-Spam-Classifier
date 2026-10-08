# 📧 Email Spam Classifier

A machine-learning system that classifies messages as **spam** or **ham** (legitimate) using NLP
(TF-IDF, stemming, stop-word removal) and three supervised algorithms: **Naive Bayes, Logistic
Regression and SVM**. Includes a web UI, a REST API, a CLI, evaluation plots, and keyword
visualization.

**Dataset:** UCI SMS Spam Collection (`data/spam.csv`) - 5,572 messages (5,169 after removing duplicates).

## Results (20% held-out test set)

| Model               | Accuracy | Precision | Recall | F1     | False-positive rate |
|---------------------|----------|-----------|--------|--------|---------------------|
| Naive Bayes         | 98.84%   | 97.60%    | 93.13% | 95.31% | 0.33%               |
| Logistic Regression | 98.84%   | 95.42%    | 95.42% | 95.42% | 0.66%               |
| **SVM (best)**      | 99.13%   | 98.41%    | 94.66% | 96.50% | 0.22%               |

(Re-running `train.py` regenerates these numbers in `models/metrics.json` and charts in `reports/`.)

## Project structure

```
spam_classifier/
├── data/spam.csv              # dataset
├── src/
│   ├── preprocess.py          # NLP cleaning (lowercase, tokens, stop-words, stemming)
│   └── predictor.py           # loads model, predicts, explains keywords
├── train.py                   # trains + evaluates 3 models, saves models & plots
├── app.py                     # Flask web app + REST API
├── predict_cli.py             # command-line classifier
├── templates/index.html       # web UI
├── test_app.py                # quick tests
├── models/                    # saved models (*.joblib) + metrics.json
├── reports/                   # confusion matrices, comparison, keyword charts
├── requirements.txt  Procfile  runtime.txt  Dockerfile  render.yaml
```

---

## 1. How to run locally

Requires **Python 3.9+**.

```bash
# 1. go into the project folder
cd spam_classifier

# 2. (recommended) create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. train the models (creates models/ and reports/)
python train.py

# 5. start the web app
python app.py
```

Open **http://localhost:5000** in your browser.

### Other ways to use it

```bash
# Command line
python predict_cli.py "Congratulations! You won a free prize, call now"
python predict_cli.py                      # interactive mode

# REST API
curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"text": "WINNER!! Claim your free prize now"}'

# Tests
python test_app.py
```

API response:

```json
{
  "label": "spam",
  "spam_probability": 0.9975,
  "confidence": 0.9975,
  "spam_keywords": [{"word": "prize", "score": 1.8}],
  "ham_keywords": []
}
```

| Endpoint        | Method | Purpose                          |
|-----------------|--------|----------------------------------|
| `/`             | GET    | Web UI                           |
| `/predict`      | POST   | Classify `{"text": "..."}`       |
| `/api/metrics`  | GET    | Model metrics                    |
| `/health`       | GET    | Health check for hosting         |

---

## 2. How to host (deploy) it online

Push the project folder to a **GitHub repository first** (needed for options A and B):

```bash
git init
git add .
git commit -m "Email spam classifier"
git branch -M main
git remote add origin https://github.com/<your-username>/spam-classifier.git
git push -u origin main
```

### Option A - Render.com (free, easiest)

1. Sign up at https://render.com and click **New + → Web Service**.
2. Connect your GitHub repo.
3. Fill in (or let `render.yaml` auto-fill):
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python train.py`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
4. Choose the **Free** plan → **Create Web Service**.
5. After the build (~3-5 min) you get a public URL like `https://spam-classifier.onrender.com`.

> Free instances sleep after inactivity, so the first request can take ~30 s.

### Option B - Railway / Heroku (uses the `Procfile`)

**Railway:** New Project → Deploy from GitHub repo → it detects Python and the `Procfile`.
Set a build command `python train.py` if asked (the app also auto-trains on first start if no model exists).

**Heroku:**
```bash
heroku login
heroku create my-spam-classifier
git push heroku main
heroku open
```

### Option C - Hugging Face Spaces (Docker, free)

1. Create a new **Space** at https://huggingface.co/spaces → SDK: **Docker**.
2. Upload the project files (the `Dockerfile` is included).
3. In the Space's `README.md` header add `app_port: 8000`.
4. The Space builds and gives you a public URL.

### Option D - Docker on any server / your own PC

```bash
docker build -t spam-classifier .
docker run -p 8000:8000 spam-classifier
# open http://localhost:8000
```

### Option E - Your own VPS (AWS EC2 / DigitalOcean / etc.)

```bash
sudo apt update && sudo apt install -y python3-venv nginx
git clone https://github.com/<you>/spam-classifier.git && cd spam-classifier
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python train.py
gunicorn app:app --bind 127.0.0.1:8000 --workers 2 --daemon
```
Then configure nginx to reverse-proxy port 80 → `127.0.0.1:8000`.

### Option F - PythonAnywhere (free, no Git needed)

1. Upload the folder in the **Files** tab, open a Bash console, `pip install --user -r requirements.txt`, then `python train.py`.
2. **Web** tab → *Add a new web app* → Flask → point the WSGI file to `from app import app as application`.

---

## 3. How it works

1. **Load & clean data** - drop the empty columns, remove duplicates, spam = 1 / ham = 0.
2. **NLP preprocessing** (`src/preprocess.py`) - lowercase; replace URLs, emails, phone numbers and
   currency symbols with special tokens (these are strong spam signals); remove punctuation and
   stop-words; Porter stemming.
3. **Features** - TF-IDF with unigrams + bigrams.
4. **Models** - Multinomial Naive Bayes, Logistic Regression, linear SVM (probability-calibrated).
5. **Evaluation** - stratified 80/20 split; accuracy, precision, recall, F1, false-positive rate,
   confusion matrices.
6. **Best model** - highest F1, ties broken by the lowest false-positive rate (so legitimate mail
   is rarely blocked).
7. **Keyword visualization** - Logistic Regression weights show which words indicate spam
   (`reports/top_keywords.png`, and per-message keywords in the UI).

## 4. Extending the project

- **Real emails:** train on the SpamAssassin corpus - just swap `load_data()` in `train.py` to return
  a DataFrame with `text` and `target` columns.
- **Phishing / scam / ad detection:** add those labels and switch to multi-class classification.
- **Other ideas:** add header features (sender domain, link count), try BERT embeddings, add a
  Gmail/IMAP integration for live inbox filtering.

## Notes

- The model is trained on **SMS** messages; accuracy on long, HTML-style emails will be lower until
  you retrain on an email dataset such as SpamAssassin.
- Always train with the same scikit-learn version you deploy with (pinning `requirements.txt` helps).
