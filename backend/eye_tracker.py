import cv2
from eye_tracking.gaze_tracking import GazeTracking
import time
import requests
import threading

class EyeTracker:
    def __init__(self, user_id, api_url="http://127.0.0.1:5000/strike"):
        self.user_id = user_id
        self.api_url = f"{api_url}/{user_id}"
        self.gaze = GazeTracking()
        self.webcam = cv2.VideoCapture(0)
        if not self.webcam.isOpened():
            print("Error: Could not open webcam.")
        self.looking_away_start_time = None
        self.strikes = 0
        self.last_strike_count = 0  # Track the last strike count sent
        self._running = False
        self._thread = None
        print(f"EyeTracker initialized for user {user_id}")

    def start_tracking(self):
        print(f"Starting eye tracking for user {self.user_id}")
        self._running = True
        self._thread = threading.Thread(target=self._run)
        try:
            self._thread.start()
            print(f"Eye tracking thread started for user {self.user_id}")
        except Exception as e:
            print(f"Error starting eye tracking thread: {e}")

    def stop_tracking(self):
        print(f"Stopping eye tracking for user {self.user_id}")
        self._running = False
        if self._thread:
            self._thread.join()
        self.webcam.release()
        print(f"Eye tracking stopped for user {self.user_id}")

    def _run(self):
        print(f"Eye tracking run method started for user {self.user_id}")
        while self._running:
            _, frame = self.webcam.read()
            if frame is None:
                print("Error: Could not read frame from webcam.")
                break
            self.gaze.refresh(frame)

            if self.gaze.is_center():
                self.looking_away_start_time = None
            else:
                if self.looking_away_start_time is None:
                    self.looking_away_start_time = time.time()
                    print("User started looking away.")
                elif time.time() - self.looking_away_start_time >= 15:
                    print("15 seconds of looking away detected.")
                    self.strikes += 1
                    print(f"Strikes incremented to: {self.strikes}")
                    self.send_strike()
                    self.looking_away_start_time = time.time()
                    print("Strike sent and timer reset.")

            if cv2.waitKey(1) == 27:
                break
        print(f"Eye tracking run method ended for user {self.user_id}")

    def add_strike(self):
        self.strikes += 1

    def get_strikes(self):
        return self.strikes

    def reset_strikes(self):
        self.strikes = 0
        self.last_strike_count = 0  # Reset the last strike count
        print(f"Strikes reset for user {self.user_id}")

    def send_strike(self):
        if self.strikes > self.last_strike_count:
            self.last_strike_count = self.strikes
            print(f"eye_tracker.py: send_strike called for user {self.user_id}, strikes: {self.strikes}")
            try:
                response = requests.post(self.api_url, json={"strikes": self.strikes})
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "redirect":
                    print(f"Redirecting user {self.user_id} to {data.get('redirect_url')}")
                else:
                    print(f"Strike sent to {self.api_url}, strikes: {self.strikes}")
                    print(f"eye_tracker send_strike: user_id={self.user_id}, strikes={self.strikes}")

                time.sleep(1.5) # Add a 2 second delay

            except requests.exceptions.RequestException as e:
                print(f"Error sending strike to {self.api_url}: {e}")