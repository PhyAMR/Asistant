import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
from pycaw.pycaw import AudioUtilities
import time


class AudioRecorder:
    def __init__(
        self,
        sample_rate=44100,
        channels=2,
        chunk_duration=5,
        output_file="recording.wav",
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.output_file = output_file
        self.all_audio_data = []
        self.sessions = AudioUtilities.GetAllSessions()

    def get_device_index_by_name(self, device_name):
        devices = sd.query_devices()
        # print(devices)
        for index, device in enumerate(devices):
            if device_name.lower() in device["name"].lower():
                return index

        return None  # Return None if the device is not found

    def record(self):

        try:

            while self.is_audio_playing():
                # Record a chunk of audio
                device_name = "Stereo Mix (Realtek(R) Audio)"
                device_index = self.get_device_index_by_name(device_name)

                if device_index is not None:
                    print(f"Device index for '{device_name}': {device_index}")
                else:
                    print(f"Device '{device_name}' not found.")

                audio_chunk = sd.rec(
                    int(self.chunk_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    device=device_index,  # Adjust accordingly based on your audio setup
                )
                sd.wait()  # Wait until the chunk recording is finished
                self.all_audio_data.append(audio_chunk)  # Append to the list
                print(f"Recorded {self.chunk_duration} seconds...")
            print("Recording complete.")
            self.save_audio()
            print("File saved.")
            while not os.path.isfile(self.output_file):
                print(f"Esperando a que aparezca {self.output_file}...")
                time.sleep(0.5)  # Espera 1 segundo antes de volver a verificar

            print(
                f"Archivo {self.output_file} encontrado. Continuando con la ejecución..."
            )
            return self.output_file

        except Exception as e:
            print("An error occurred:", str(e))

        # Combine all chunks into a single array

    def is_audio_playing(self):
        """This function checks if there is any audio playing in the system. And returns true if the browser you select
        is the one playing audio."""
        # Set a flag to track audio playing
        audio_playing = False

        for session in self.sessions:
            if session.State == 1:  # State == 1 means the audio session is active
                if session.Process.name().lower() == "vivaldi.exe":
                    # print("Audio playing in Vivaldi.")  # add to config
                    audio_playing = True
                    break  # Exit loop since we've found the audio

        return audio_playing  # Return the flag indicating whether audio is playing

    def save_audio(self):
        # Combine all audio chunks into a single array
        full_audio_data = np.concatenate(self.all_audio_data)
        # Save the combined audio to a file
        write(self.output_file, self.sample_rate, full_audio_data)
        print(f"Audio saved to '{self.output_file}'")

    def clean(self):
        try:
            os.remove(self.output_file)
            self.all_audio_data = []
            print("Cleaned up.")
        except FileNotFoundError as e:
            print(f"Could not find file {self.output_file}. Error: {str(e)}")
            pass


# Usage
# if __name__ == "__main__":
#    recorder = AudioRecorder()
#    recorder.record()
