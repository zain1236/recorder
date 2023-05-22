from google.cloud import speech_v1p1beta1 as speech

def transcribe_urdu_audio(audio_file):
    client = speech.SpeechClient()

    # Read the audio file
    with open(audio_file, "rb") as audio_data:
        audio = speech.RecognitionAudio(content=audio_data.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ur-PK",  # Urdu (Pakistan)
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    # Retrieve and return the transcribed text
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript

# Provide the path to your Urdu audio file
urdu_audio_file = "10764_13_05_2023_04_54_21.wav"

# Call the function to transcribe the audio
transcription = transcribe_urdu_audio(urdu_audio_file)

# Print the transcription
print("Transcription: ", transcription)
