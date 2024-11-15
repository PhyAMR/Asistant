import speech_recognition as sr
import whisper


class Transcriber:  # Replace with your actual class name
    def __init__(self, audio_path=None):
        self.path = audio_path

    def transcript(self):
        r = sr.Recognizer()

        # Use audio from file if provided; otherwise, use microphone.
        if not self.path:
            with sr.Microphone() as source:
                print(f"Please speak something to {source}...")
                audio = r.record(source)  # Use record() to read the entire file
        else:
            audio = self.path
            print(f"Transcribing {self.path}...")

        try:

            model = whisper.load_model("tiny")
            source = self.path
            result = model.transcribe(audio=audio, verbose=True, language="en")
            return result["text"]
        except sr.WaitTimeoutError:
            print("Timed out. No speech detected.")
        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
        except Exception as e:
            print("An error occurred:", str(e))
