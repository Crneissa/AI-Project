from flask import Flask, request, jsonify, send_from_directory, render_template, session
import os
import google.generativeai as generativeai
import summary_logic
import quiz_logic
import eye_tracker
import utils
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

generativeai.configure(api_key=utils.get_api_key())

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    template_folder=FRONTEND_DIR
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "focusup-dev-secret-key")

eye_trackers = {}

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_quiz_state():
    if "quiz_state" not in session:
        session["quiz_state"] = {
            "score": 0,
            "total_answered": 0,
            "correct_streak": 0,
            "wrong_streak": 0,
            "last_difficulty": "medium"
        }


def get_attention_from_eye_tracker(user_id):
    if user_id in eye_trackers:
        strikes = eye_trackers[user_id].get_strikes()

        if strikes >= 3:
            return 0.2
        elif strikes == 2:
            return 0.4
        elif strikes == 1:
            return 0.7
        else:
            return 0.9

    return 0.8


@app.route("/")
def serve_index():
    return render_template("home.html")


@app.route("/summary")
def serve_summary():
    print("Summary route accessed.")
    print(f"Session: {session}")

    if "user_id" not in session:
        session["user_id"] = os.urandom(16).hex()

    user_id = session["user_id"]

    if user_id not in eye_trackers:
        try:
            eye_trackers[user_id] = eye_tracker.EyeTracker(user_id)
            eye_trackers[user_id].start_tracking()
        except Exception as e:
            print(f"Error starting eye tracker: {e}")
    else:
        print(f"Reusing existing eye tracker for user {user_id}")

    return render_template("summary.html", user_id=user_id)


@app.route("/quiz")
def serve_quiz():
    print("Quiz route accessed.")
    print(f"Session: {session}")

    if "user_id" not in session:
        session["user_id"] = os.urandom(16).hex()

    user_id = session["user_id"]

    if user_id not in eye_trackers:
        try:
            eye_trackers[user_id] = eye_tracker.EyeTracker(user_id)
            eye_trackers[user_id].start_tracking()
        except Exception as e:
            print(f"Error starting eye tracker: {e}")
    else:
        print(f"Reusing existing eye tracker for user {user_id}")

    init_quiz_state()
    return render_template("quiz.html", user_id=user_id)


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if "pdf" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files["pdf"]

    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file.filename)
        pdf_file.save(filepath)

        summary_logic.process_pdf_data(filepath)
        session["pdf_filename"] = pdf_file.filename

        session["quiz_state"] = {
            "score": 0,
            "total_answered": 0,
            "correct_streak": 0,
            "wrong_streak": 0,
            "last_difficulty": "medium"
        }

        return jsonify({"message": "PDF uploaded successfully!"}), 200

    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return jsonify({"error": f"Error uploading PDF: {str(e)}"}), 500


@app.route("/get_pdf_data", methods=["GET"])
def get_pdf_data():
    filename = session.get("pdf_filename")
    if not filename:
        return jsonify({"error": "No PDF data found"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        pdf_data = summary_logic.get_pdf_data(filepath)
        return jsonify({"pdf_data": pdf_data})
    except Exception as e:
        print(f"Error getting PDF data: {e}")
        return jsonify({"error": "Error getting PDF data"}), 500


@app.route("/process_pdf", methods=["POST"])
def process_pdf():
    return summary_logic.process_pdf()


@app.route("/ask_question", methods=["POST"])
def ask_question():
    return summary_logic.ask_question()


@app.route("/generate_quiz")
def generate_quiz_route():
    print("generate_quiz_route called")

    num_questions = int(request.args.get("num_questions", 5))
    filename = session.get("pdf_filename")

    if not filename:
        return jsonify({"error": "No PDF selected"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    pdf_data = summary_logic.get_pdf_data(filepath)

    if not pdf_data:
        return jsonify({"error": "No PDF data available"}), 400

    init_quiz_state()
    quiz_state = session["quiz_state"]

    user_id = session.get("user_id")
    attention = get_attention_from_eye_tracker(user_id)

    score_percent = 0
    if quiz_state["total_answered"] > 0:
        score_percent = (quiz_state["score"] / quiz_state["total_answered"]) * 100

    try:
        difficulty = quiz_logic.get_next_difficulty(
            score=score_percent,
            correct_streak=quiz_state["correct_streak"],
            wrong_streak=quiz_state["wrong_streak"],
            attention=attention
        )
    except Exception as e:
        print(f"Decision tree error: {e}")
        difficulty = "medium"

    quiz_state["last_difficulty"] = difficulty
    session["quiz_state"] = quiz_state

    print("=== Decision Tree Debug ===")
    print("score_percent:", score_percent)
    print("correct_streak:", quiz_state["correct_streak"])
    print("wrong_streak:", quiz_state["wrong_streak"])
    print("attention:", attention)
    print("chosen difficulty:", difficulty)
    print("===========================")

    quiz_data, error_message = quiz_logic.generate_quiz(
        pdf_data,
        num_questions,
        difficulty
    )

    if quiz_data:
        return jsonify(quiz_data)
    return jsonify({"error": error_message}), 500


@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.get_json(silent=True) or {}
    is_correct = data.get("is_correct", False)

    init_quiz_state()
    quiz_state = session["quiz_state"]

    quiz_state["total_answered"] += 1

    if is_correct:
        quiz_state["score"] += 1
        quiz_state["correct_streak"] += 1
        quiz_state["wrong_streak"] = 0
    else:
        quiz_state["wrong_streak"] += 1
        quiz_state["correct_streak"] = 0

    session["quiz_state"] = quiz_state
    
    
    print("=== Updated Quiz State ===")
    print("score:", quiz_state["score"])
    print("total_answered:", quiz_state["total_answered"])
    print("correct_streak:", quiz_state["correct_streak"])
    print("wrong_streak:", quiz_state["wrong_streak"])
    print("==========================")

    return jsonify({
        "status": "success",
        "quiz_state": quiz_state
    })
    
    
    
    
    
    
    


@app.route("/get_quiz_state", methods=["GET"])
def get_quiz_state():
    init_quiz_state()
    return jsonify(session["quiz_state"])


@app.route("/strike/<user_id>", methods=["POST"])
def strike(user_id):
    if user_id == "undefined" or user_id is None:
        return jsonify({"status": "error", "message": "Invalid user ID"})

    if user_id in eye_trackers:
        strikes = eye_trackers[user_id].get_strikes()

        print(f"APP.PY: User {user_id} has {strikes} strikes.")
        print(f"APP.PY: strike route: user_id={user_id}, strikes={strikes}")

        audio_file = generate_strike_audio(strikes)

        if audio_file:
            print(f"APP.PY: Serving audio file: {audio_file}")
            return jsonify({"status": "success", "strikes": strikes, "audio_file": audio_file})
        return jsonify({"status": "error", "message": "Failed to generate audio"})

    return jsonify({"status": "error"})


@app.route("/get_user_id")
def get_user_id():
    if "user_id" in session:
        return jsonify({"user_id": session["user_id"]})
    return jsonify({"user_id": None})


@app.route("/reset_strikes")
def reset_strikes():
    if "user_id" in session:
        user_id = session["user_id"]
        if user_id in eye_trackers:
            eye_trackers[user_id].reset_strikes()
            return jsonify({"status": "success"})
    return jsonify({"status": "error"})


@app.route("/home")
def serve_home():
    if "user_id" in session:
        user_id = session["user_id"]
        if user_id in eye_trackers:
            eye_trackers[user_id].stop_tracking()
            del eye_trackers[user_id]
    return render_template("home.html")


@app.route("/stop_eye_tracker", methods=["POST"])
def stop_eye_tracker():
    user_id = session.get("user_id")
    if user_id and user_id in eye_trackers:
        try:
            eye_trackers[user_id].stop_tracking()
            del eye_trackers[user_id]
            return jsonify({"status": "success", "message": "Eye tracker stopped."})
        except Exception as e:
            print(f"Error stopping eye tracker: {e}")
            return jsonify({"status": "error", "message": f"Error stopping eye tracker: {e}"}), 500
    return jsonify({"status": "error", "message": "Eye tracker not running for this user."}), 400


@app.route("/audio_cache/<filename>")
def serve_audio(filename):
    return send_from_directory(os.path.join(app.static_folder, "audio_cache"), filename)


def generate_strike_audio(strikes):
    message = f"You now have {strikes} strikes."
    if strikes == 1:
        message = "Warning! One strike."
    elif strikes == 2:
        message = "Second warning! Two strikes."
    elif strikes >= 3:
        message = "Third warning! Three or more strikes."

    audio_file = f"strike_{strikes}.mp3"
    audio_dir = os.path.join(app.static_folder, "audio_cache")
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, audio_file)

    if not os.path.exists(audio_path):
        try:
            tts = gTTS(text=message, lang="en")
            tts.save(audio_path)
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

    return audio_file


if __name__ == "__main__":
    app.run(debug=True)