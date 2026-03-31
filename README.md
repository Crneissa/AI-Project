Here’s a cleaner, more professional version of your README with better structure, clarity, and formatting:

---

# AI Project

## Setup Instructions

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

* **Windows:**

```bash
venv\Scripts\activate
```

* **macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file inside the `backend/` directory and add the following:

```env
API_KEY=your_gemini_api_key
SECRET_KEY=your_flask_secret_key
```

* `API_KEY`: Your Gemini API key
* `SECRET_KEY`: Your Flask secret key

---

## Running the Application

Navigate to the backend folder and start the server:

```bash
cd backend
python app.py
```

---

## Notes

* Make sure your virtual environment is activated before installing dependencies or running the app.
* Keep your `.env` file private and do not commit it to version control.

---
