import asyncio
import os
import base64

from pathlib import Path
from openai import AzureOpenAI

from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
)

speech_file_path = Path(__file__).parent / "speech.mp3"

try:
    # Try gpt-audio model approach first
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-audio"),
        messages=[
            {
                "role": "user", 
                "content": "Speak in a cheerful and positive tone.\n\nText to speak: Today is a wonderful day to build something people love!"
            }
        ],
        modalities=["text", "audio"],
        audio={
            "voice": "coral",
            "format": "mp3"
        }
    )
    
    # Extract and save audio data
    if hasattr(response, 'choices') and response.choices:
        choice = response.choices[0]
        if hasattr(choice, 'message') and hasattr(choice.message, 'audio') and choice.message.audio:
            if hasattr(choice.message.audio, 'data') and choice.message.audio.data:
                audio_bytes = base64.b64decode(choice.message.audio.data)
                with open(speech_file_path, 'wb') as f:
                    f.write(audio_bytes)
                print(f"Audio saved to {speech_file_path}")
            else:
                print("No audio data found in response")
        else:
            print("No audio in message")
    else:
        print("No choices in response")

except Exception as e:
    print(f"gpt-audio approach failed: {e}")
    print("Trying fallback TTS approach...")
    
    # Fallback to traditional TTS
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="coral",
        input="Today is a wonderful day to build something people love!",
    ) as response:
        response.stream_to_file(speech_file_path)
    print(f"Audio saved to {speech_file_path} using fallback method")