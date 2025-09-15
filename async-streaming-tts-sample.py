import asyncio
import os
import base64
import io

from openai import AsyncAzureOpenAI
from openai.helpers import LocalAudioPlayer

from dotenv import load_dotenv

load_dotenv()

client = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
)

async def main() -> None:
    try:
        # Try gpt-audio model approach first
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-audio"),
            messages=[
                {
                    "role": "user", 
                    "content": """Voice Affect: Soft, gentle, soothing; embody tranquility.

Tone: Calm, reassuring, peaceful; convey genuine warmth and serenity.

Pacing: Slow, deliberate, and unhurried; pause gently after instructions to allow the listener time to relax and follow along.

Emotion: Deeply soothing and comforting; express genuine kindness and care.

Pronunciation: Smooth, soft articulation, slightly elongating vowels to create a sense of ease.

Pauses: Use thoughtful pauses, especially between breathing instructions and visualization guidance, enhancing relaxation and mindfulness.

Text to speak: Hello, and welcome to your moment of mindfulness. I'm so glad you're here. Let's begin by closing your eyes and taking a deep, calming breath. Breathe in slowly through your nose, and exhale softly, releasing any tension.

Imagine your thoughts as soft clouds drifting across the sky—observe them without attachment, letting your mind become clear and peaceful."""
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
                    # Save to a temporary file
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_file.write(audio_bytes)
                        temp_file_path = temp_file.name
                    
                    print(f"Audio saved using gpt-audio model to: {temp_file_path}")
                    print("You can play this audio file manually.")
                    return
        
        print("No audio data found in gpt-audio response, trying fallback...")
        
    except Exception as e:
        print(f"gpt-audio approach failed: {e}")
        print("Please check your gpt-audio deployment configuration.")

if __name__ == "__main__":
    asyncio.run(main())