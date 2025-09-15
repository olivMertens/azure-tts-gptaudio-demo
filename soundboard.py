import gradio as gr
import random
import json
import asyncio
import os
import io
import tempfile
import time
import numpy as np
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

load_dotenv()

# Global state
is_playing = False
current_voice = "alloy"
current_vibe = None

# Available voices for the gpt-audio model
VOICES = ["alloy", "ash", "ballad", "cedar", "coral", "echo", "marin", "sage", "shimmer", "verse"]

# Create temporary directory to store audio files
temp_dir = tempfile.mkdtemp()

#openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
azure = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
)

def update_voice(selected_voice):
    global current_voice
    current_voice = selected_voice.lower()
    return selected_voice, gr.Button(variant="primary")

def reset_buttons():
    return [gr.Button(variant="secondary") for _ in range(11)]

def update_random_button():
    buttons = reset_buttons()
    random_index = random.randint(0, 10)  # Randomly select one button index
    buttons[random_index] = gr.Button(variant="primary")
    selected_voice = "Alloy Ash Ballad Coral Echo Fable Nova Onyx Sage Shimmer Verse".split()[random_index]
    return f"Voice: {selected_voice}", *buttons

def load_vibes():
    with open("vibe.json", "r", encoding="utf-8") as file:
        vibes = json.load(file)
    return [vibe["Vibe"] for vibe in vibes]

def update_vibe_buttons(all_vibes=None):
    global current_vibe
    if all_vibes is None:
        all_vibes = load_vibes()
    visible_vibes = random.sample(all_vibes, 5)
    current_vibe = None  # Reset current vibe when shuffling
    return [gr.Button(vibe, variant="secondary", visible=(vibe in visible_vibes)) for vibe in all_vibes], visible_vibes

def get_vibe_description(vibe_name):
    global current_vibe
    current_vibe = vibe_name
    with open("vibe.json", "r", encoding="utf-8") as file:
        vibes = json.load(file)
        for vibe in vibes:
            if vibe["Vibe"] == vibe_name:
                # Replace escaped newlines with actual newlines while preserving other characters
                description = vibe["Description"].replace('\\n', '\n')
                return description
    return ""

def update_selected_vibe(selected_vibe, visible_vibes):
    global current_vibe
    current_vibe = selected_vibe
    all_vibes = load_vibes()
    description = get_vibe_description(selected_vibe)
    return [gr.Button(vibe, 
            variant="primary" if vibe == selected_vibe else "secondary",
            visible=(vibe in visible_vibes)) 
            for vibe in all_vibes], visible_vibes

def shuffle_vibes():
    global current_vibe
    current_vibe = None  # Reset current vibe when shuffling
    all_vibes = load_vibes()
    visible_vibes = random.sample(all_vibes, 5)
    buttons = [gr.Button(vibe, variant="secondary", visible=(vibe in visible_vibes)) for vibe in all_vibes]
    return *buttons, visible_vibes

def get_vibe_info(vibe_name):
    with open("vibe.json", "r", encoding="utf-8") as file:
        vibes = json.load(file)
        for vibe in vibes:
            if vibe["Vibe"] == vibe_name:
                # Replace escaped newlines with actual newlines while preserving other characters
                description = vibe["Description"].replace('\\n', '\n')
                script = vibe["Script"].replace('\\n', '\n')
                return description, script
    return "", ""

def check_api_key():
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Azure OpenAI API key not found. Please set the AZURE_OPENAI_API_KEY environment variable.")
    return api_key

async def generate_streaming_audio(voice_name, text, instructions):
    """Generate audio chunks from OpenAI gpt-audio model via chat completions"""
    try:
        # Combine text and instructions for the audio generation
        full_prompt = f"{instructions}\n\nText to speak: {text}" if instructions else text
        
        response = await azure.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-audio"),
            messages=[
                {
                    "role": "user", 
                    "content": full_prompt
                }
            ],
            modalities=["text", "audio"],
            audio={
                "voice": voice_name,
                "format": "mp3"
            },
            stream=True
        )
        
        async for chunk in response:
            if hasattr(chunk, 'choices') and chunk.choices:
                choice = chunk.choices[0]
                if hasattr(choice, 'delta') and hasattr(choice.delta, 'audio') and choice.delta.audio:
                    if hasattr(choice.delta.audio, 'data') and choice.delta.audio.data:
                        # Decode base64 audio data
                        import base64
                        audio_bytes = base64.b64decode(choice.delta.audio.data)
                        yield audio_bytes
    except Exception as e:
        # Fallback to traditional TTS if gpt-audio doesn't work as expected
        print(f"Trying fallback TTS approach: {e}")
        async with azure.audio.speech.with_streaming_response.create(
            model="tts-1",  # fallback model
            voice=voice_name,
            input=text,
            response_format="mp3"
        ) as response:
            async for chunk in response.iter_bytes():
                yield chunk

async def generate_audio_file(input, output_path, voice_name="coral", instructions=None):
    """Generate audio file from OpenAI gpt-audio model and save to the given path"""
    try:
        # Combine text and instructions for the audio generation
        full_prompt = f"{instructions}\n\nText to speak: {input}" if instructions else input
        
        response = await azure.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-audio"),
            messages=[
                {
                    "role": "user", 
                    "content": full_prompt
                }
            ],
            modalities=["text", "audio"],
            audio={
                "voice": voice_name,
                "format": "mp3"
            }
        )
        
        # Extract audio data from response
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'audio') and choice.message.audio:
                if hasattr(choice.message.audio, 'data') and choice.message.audio.data:
                    import base64
                    audio_bytes = base64.b64decode(choice.message.audio.data)
                    with open(output_path, 'wb') as f:
                        f.write(audio_bytes)
                    return
        
        raise Exception("No audio data found in response")
        
    except Exception as e:
        # Fallback to traditional TTS if gpt-audio doesn't work as expected
        print(f"Trying fallback TTS approach: {e}")
        async with azure.audio.speech.with_streaming_response.create(
            model="tts-1",  # fallback model
            voice=voice_name,
            input=input,
            response_format="mp3",
        ) as response:
            await response.stream_to_file(output_path)

def stream_audio(voice_name, text, instructions):
    """Stream audio chunks from OpenAI TTS to the Gradio Audio component"""
    def generate():
        """Generator function that yields audio chunks as they're received"""
        # We need to accumulate bytes for proper MP3 playback
        audio_bytes = b""
        
        # Run the async function and collect audio chunks
        for chunk in asyncio.run(generate_streaming_audio(voice_name, text, instructions)):
            # Add the new chunk to our accumulated audio
            audio_bytes += chunk
            # Yield the accumulated audio so far
            yield audio_bytes
    
    # Return the generator function itself
    return generate



def stop_audio():
    global is_playing
    if (is_playing):
        is_playing = False
        yield "Audio stopped."
    yield "No audio is playing."

css = """
/* === DARK THEME LARGE VIEWPORT DESIGN === */

/* Main container - Full width dark theme */
.gradio-container {
    max-width: 100vw !important;
    width: 100vw !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 2rem 3rem !important;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%) !important;
    color: #f1f5f9 !important;
}

/* Body and root background */
body, html, .gradio-app {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Header section - Large and prominent */
.gradio-container h1 {
    color: #f8fafc !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    font-size: 3.5rem !important;
    text-align: center !important;
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    background: linear-gradient(135deg, #60a5fa, #34d399, #fbbf24) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-top: 0 !important;
}

.gradio-container p {
    color: #cbd5e1 !important;
    margin-bottom: 3rem !important;
    font-size: 1.4rem !important;
    text-align: center !important;
    font-weight: 400 !important;
    line-height: 1.6 !important;
}

/* Voice label styling - Dark theme */
.gradio-label {
    background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
    color: #ffffff !important;
    padding: 1rem 2rem !important;
    border-radius: 1rem !important;
    text-align: center !important;
    font-weight: 600 !important;
    border: 2px solid #3b82f6 !important;
    box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3) !important;
    font-size: 1.3rem !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
}

/* Voice buttons grid - Large and accessible */
.voice-buttons {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)) !important;
    gap: 1.5rem !important;
    width: 100% !important;
    padding: 2rem !important;
    margin: 2rem 0 !important;
    background: rgba(30, 41, 59, 0.6) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 1.5rem !important;
    border: 2px solid rgba(59, 130, 246, 0.3) !important;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2) !important;
}

.voice-button {
    min-height: 80px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    border-radius: 1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    padding: 1.2rem !important;
    border: 2px solid #475569 !important;
    background: linear-gradient(135deg, #1e293b, #334155) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    cursor: pointer !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
}

.voice-button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 12px 24px rgba(59, 130, 246, 0.4) !important;
    border-color: #3b82f6 !important;
    background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
}

.voice-button[data-variant="primary"] {
    background: linear-gradient(135deg, #dc2626, #ef4444) !important;
    border-color: #dc2626 !important;
    color: #ffffff !important;
    box-shadow: 0 8px 20px rgba(220, 38, 38, 0.4) !important;
}

.voice-button[data-variant="primary"]:hover {
    background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
    transform: translateY(-4px) scale(1.03) !important;
    box-shadow: 0 16px 32px rgba(220, 38, 38, 0.5) !important;
}

/* Voice button text - High contrast */
.voice-button span,
.voice-button > div > span,
button.voice-button span,
button.voice-button > div > span {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    padding: 0 !important;
    color: #f1f5f9 !important;
    text-transform: capitalize !important;
    display: block !important;
    visibility: visible !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    letter-spacing: 0.5px !important;
}

.voice-button[data-variant="primary"] span,
.voice-button[data-variant="primary"] > div > span,
button.voice-button[data-variant="primary"] span,
button.voice-button[data-variant="primary"] > div > span {
    color: #ffffff !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
}

.voice-button > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Vibe buttons layout - Dark theme */
.vibe-buttons {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
    gap: 1.5rem !important;
    width: 100% !important;
    padding: 2rem !important;
    margin: 2rem 0 !important;
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 1.5rem !important;
    border: 2px solid rgba(34, 197, 94, 0.3) !important;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2) !important;
}

.vibe-buttons button {
    min-height: 70px !important;
    border-radius: 1rem !important;
    border: 2px solid #475569 !important;
    background: linear-gradient(135deg, #1e293b, #334155) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
}

.vibe-buttons button span,
.vibe-buttons button > div > span {
    color: #f1f5f9 !important;
    visibility: visible !important;
    font-weight: 600 !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}

.vibe-buttons button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 20px rgba(34, 197, 94, 0.4) !important;
    border-color: #22c55e !important;
    background: linear-gradient(135deg, #15803d, #22c55e) !important;
}

.vibe-buttons button[data-variant="primary"] {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    border-color: #7c3aed !important;
    color: #ffffff !important;
    box-shadow: 0 8px 20px rgba(124, 58, 237, 0.4) !important;
}

.vibe-buttons button[data-variant="primary"] span,
.vibe-buttons button[data-variant="primary"] > div > span {
    color: #ffffff !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
}

/* Random button styling - Dark theme */
.random-button {
    background: linear-gradient(135deg, #ea580c, #f97316) !important;
    color: #ffffff !important;
    border: 2px solid #ea580c !important;
    border-radius: 1rem !important;
    padding: 1rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 6px 16px rgba(234, 88, 12, 0.4) !important;
    cursor: pointer !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}

.random-button:hover {
    background: linear-gradient(135deg, #c2410c, #ea580c) !important;
    border-color: #c2410c !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 12px 28px rgba(234, 88, 12, 0.5) !important;
}

/* Text areas and inputs - Dark theme */
.gradio-textbox, .gradio-textarea {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 2px solid #475569 !important;
    border-radius: 1rem !important;
    color: #f1f5f9 !important;
    font-size: 1.1rem !important;
    padding: 1rem !important;
    backdrop-filter: blur(5px) !important;
}

.gradio-textbox textarea, .gradio-textarea textarea {
    color: #f1f5f9 !important;
    font-size: 1.1rem !important;
    background: transparent !important;
}

.gradio-textbox:focus, .gradio-textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2) !important;
    background: rgba(30, 41, 59, 0.9) !important;
}

/* Labels and text - High contrast */
.gradio-label, .gradio-label span {
    color: #f8fafc !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
}

/* General button text visibility - Dark theme */
button span, 
button > div > span,
.gradio-button span,
.gradio-button > div > span {
    color: #f1f5f9 !important;
    visibility: visible !important;
    display: inline-block !important;
    font-weight: 700 !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}

/* Primary button text */
button[data-variant="primary"] span,
button[data-variant="primary"] > div > span,
.gradio-button[data-variant="primary"] span,
.gradio-button[data-variant="primary"] > div > span {
    color: #ffffff !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
}

/* Secondary button text */
button[data-variant="secondary"] span,
button[data-variant="secondary"] > div > span,
.gradio-button[data-variant="secondary"] span,
.gradio-button[data-variant="secondary"] > div > span {
    color: #f1f5f9 !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}

/* Generate button - Dark theme */
.generate-button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: #ffffff !important;
    border: 2px solid #059669 !important;
    border-radius: 1rem !important;
    padding: 1rem 2.5rem !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    box-shadow: 0 6px 16px rgba(5, 150, 105, 0.4) !important;
}

.generate-button:hover {
    background: linear-gradient(135deg, #047857, #059669) !important;
    border-color: #047857 !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 12px 28px rgba(5, 150, 105, 0.5) !important;
}

/* Stop button styling - Dark theme */
button[data-variant="stop"], .gradio-button[data-variant="stop"] {
    background: linear-gradient(135deg, #dc2626, #ef4444) !important;
    color: #ffffff !important;
    border: 2px solid #dc2626 !important;
    border-radius: 1rem !important;
    padding: 1rem 2.5rem !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4) !important;
}

button[data-variant="stop"]:hover, .gradio-button[data-variant="stop"]:hover {
    background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
    border-color: #b91c1c !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 12px 28px rgba(220, 38, 38, 0.5) !important;
}

/* Audio component styling */
.gradio-audio {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 2px solid #475569 !important;
    border-radius: 1rem !important;
    padding: 1rem !important;
    backdrop-filter: blur(5px) !important;
}

/* Responsive design for large viewports */
@media (min-width: 1920px) {
    .gradio-container {
        padding: 3rem 5rem !important;
    }
    
    .voice-buttons {
        grid-template-columns: repeat(6, 1fr) !important;
        gap: 2rem !important;
    }
    
    .voice-button {
        min-height: 100px !important;
        font-size: 1.2rem !important;
    }
    
    .vibe-buttons {
        grid-template-columns: repeat(5, 1fr) !important;
        gap: 2rem !important;
    }
}

@media (min-width: 1600px) {
    .voice-buttons {
        grid-template-columns: repeat(5, 1fr) !important;
    }
    
    .vibe-buttons {
        grid-template-columns: repeat(4, 1fr) !important;
    }
}

@media (min-width: 1280px) {
    .voice-buttons {
        grid-template-columns: repeat(4, 1fr) !important;
    }
    
    .vibe-buttons {
        grid-template-columns: repeat(3, 1fr) !important;
    }
}

@media (max-width: 1024px) {
    .gradio-container {
        padding: 1.5rem 2rem !important;
    }
    
    .voice-buttons {
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 1rem !important;
    }
    
    .vibe-buttons {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 1rem !important;
    }
}

@media (max-width: 768px) {
    .gradio-container h1 {
        font-size: 2.5rem !important;
    }
    
    .voice-buttons {
        grid-template-columns: repeat(2, 1fr) !important;
    }
    
    .vibe-buttons {
        grid-template-columns: repeat(1, 1fr) !important;
    }
}

/* Hide footer */
footer {
    visibility: hidden !important;
}
"""

brand_theme = gr.themes.Soft(
    primary_hue="blue", 
    secondary_hue="slate", 
    neutral_hue="slate"
).set(
        # Dark theme colors
        button_primary_background_fill="linear-gradient(135deg, #dc2626, #ef4444)", 
        button_primary_background_fill_hover="linear-gradient(135deg, #b91c1c, #dc2626)", 
        button_primary_text_color="#ffffff", 
        button_secondary_background_fill="linear-gradient(135deg, #1e293b, #334155)", 
        button_secondary_background_fill_hover="linear-gradient(135deg, #1e40af, #3b82f6)", 
        button_secondary_text_color="#f1f5f9", 
        body_background_fill="#0f172a", 
        block_background_fill="rgba(30, 41, 59, 0.6)", 
        body_text_color="#f1f5f9", 
        body_text_color_subdued="#cbd5e1", 
        block_border_color="rgba(59, 130, 246, 0.3)", 
        input_background_fill="rgba(30, 41, 59, 0.8)", 
        input_border_color="#475569", 
        input_border_color_focus="#3b82f6"
)

def update_vibe_and_global(vibe, current_vibes):
    """Update the selected vibe and global state"""
    global current_vibe
    current_vibe = vibe
    desc, script = get_vibe_info(vibe)
    updated_buttons, updated_state = update_selected_vibe(vibe, current_vibes)
    return (desc, *updated_buttons, updated_state, script)

def generate_random_content():
    """Generate random audio content using GPT-5 Nano with 3 different use cases"""
    try:
        import random
        
        # Define the 3 use cases for GPT-5 Nano
        use_cases = [
            {
                "type": "kids_story",
                "prompt": "Create a short, engaging children's story (2-3 paragraphs) with a clear moral lesson. Include friendly characters and simple language that would be perfect for text-to-speech. Make it warm and educational.",
                "description": "🧸 Children's Story\n\nTone: Warm, enthusiastic, and child-friendly with varied pacing to keep young listeners engaged\n\nThis content was generated by GPT-5 Nano to showcase dynamic AI-powered storytelling."
            },
            {
                "type": "financial_report", 
                "prompt": "Generate a realistic quarterly financial report summary for a tech company. Include specific numbers, percentages, and business metrics. Make it sound professional and authoritative, suitable for investor presentation via text-to-speech.",
                "description": "📊 Financial Report\n\nTone: Professional, confident, and authoritative with clear articulation of financial data and business insights\n\nThis content was generated by GPT-5 Nano to showcase dynamic business communication."
            },
            {
                "type": "tech_podcast",
                "prompt": "Create an engaging tech podcast segment about emerging technology trends. Make it conversational, informative, and enthusiastic. Include specific examples and make it sound like a real podcast host speaking naturally.",
                "description": "🎧 Tech Podcast\n\nTone: Conversational yet knowledgeable, with enthusiasm for technology and a casual podcast style that's informative but engaging\n\nThis content was generated by GPT-5 Nano to showcase dynamic content creation."
            }
        ]
        
        # Randomly select one of the 3 use cases
        selected_use_case = random.choice(use_cases)
        
        # Generate content using GPT-5 Nano via Azure OpenAI
        response = azure.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_NANO_DEPLOYMENT_NAME", "gpt-5-nano"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content creator specializing in audio content. Generate engaging, well-structured content optimized for text-to-speech conversion. Focus on clear, natural language that sounds great when spoken aloud."
                },
                {
                    "role": "user", 
                    "content": selected_use_case["prompt"]
                }
            ],
            max_tokens=500,
            temperature=0.8
        )
        
        generated_content = response.choices[0].message.content.strip()
        
        return selected_use_case["description"], generated_content
        
    except Exception as e:
        # Fallback to static content if GPT-5 Nano is not available
        print(f"GPT-5 Nano not available, using fallback content: {e}")
        return generate_fallback_content()

def generate_fallback_content():
    """Fallback function with static content when GPT-5 Nano is not available"""
    content_scenarios = [
        {
            "type": "kids_story",
            "description": "🧸 Children's Story\n\nTone: Warm, enthusiastic, and child-friendly with varied pacing to keep young listeners engaged\n\nThis content was randomly generated to showcase different audio scenarios and speaking styles.",
            "content": "Once upon a time, in a magical forest, there lived a little bunny named Benny and a wise old owl named Olivia. Benny loved to hop around and explore, but he was always in such a hurry that he never stopped to listen to others.\n\nOne sunny morning, Benny found a shiny red apple hanging from a tree. 'Mine!' he squeaked excitedly, jumping as high as he could. But the apple was too high, and Benny began to cry.\n\nOlivia flew down from her branch. 'What's wrong, little friend?' she asked kindly.\n\n'I want that apple, but I can't reach it!' Benny sniffled.\n\nOlivia smiled. 'Sometimes, when we ask for help and share with others, wonderful things happen. Would you like me to help you?'\n\nTogether, they got the apple down. Benny was so grateful that he shared half with Olivia. From that day on, Benny learned that friendship and sharing make everything sweeter.\n\nAnd they both lived happily ever after, sharing adventures and apples in their beautiful forest home."
        },
        {
            "type": "financial_report",
            "description": "📊 Financial Report\n\nTone: Professional, confident, and authoritative with clear articulation of financial data and business insights\n\nThis content was randomly generated to showcase different audio scenarios and speaking styles.",
            "content": "Good morning, investors and stakeholders. I'm pleased to present TechFlow Innovations' Q4 financial results, which demonstrate strong performance across all key metrics.\n\nRevenue reached $47.2 million, representing a 23% year-over-year increase, driven primarily by our cloud infrastructure services and AI consulting divisions. Our gross margin improved to 68%, up from 64% in the previous quarter, reflecting improved operational efficiency and strategic pricing adjustments.\n\nOperating expenses were well-controlled at $28.1 million, with R&D investments comprising 15% of revenue as we continue to innovate in machine learning and automation solutions. Net income reached $8.7 million, or $1.24 per share, exceeding analyst expectations by 12%.\n\nLooking ahead, we're optimistic about Q1 2025, with our new enterprise AI platform launching next month and three major client partnerships already secured. We're raising our full-year revenue guidance to $195-205 million, reflecting our strong market position and expanding customer base.\n\nThank you for your continued confidence in TechFlow Innovations."
        },
        {
            "type": "tech_podcast",
            "description": "🎧 Tech Podcast\n\nTone: Conversational yet knowledgeable, with enthusiasm for technology and a casual podcast style that's informative but engaging\n\nThis content was randomly generated to showcase different audio scenarios and speaking styles.",
            "content": "Hey everyone, welcome back to CodeCast! I'm your host, and today we're diving into something that's absolutely revolutionizing how we build software – AI-powered development tools.\n\nSo, picture this: you're stuck on a complex algorithm, and instead of spending hours on Stack Overflow, you just describe what you want in plain English, and boom – your IDE generates not just the code, but explains the logic, suggests optimizations, and even writes your unit tests. It sounds like science fiction, but it's happening right now!\n\nWhat's really fascinating is how these tools are learning from billions of lines of code. They're not just copy-pasting – they're understanding patterns, architectural decisions, and even coding style preferences. But here's the kicker – they're making us better developers, not replacing us.\n\nI've been using GitHub Copilot and ChatGPT for coding, and the productivity boost is incredible. But the real magic happens when you understand how to prompt them effectively. It's like having a senior developer pair programming with you 24/7.\n\nThe future of software development is collaborative intelligence – humans and AI working together to build amazing things. What do you think? Are you already using AI in your development workflow? Let me know in the comments!"
        }
    ]
    
    # Randomly select a content scenario
    import random
    selected_scenario = random.choice(content_scenarios)
    
    return selected_scenario["description"], selected_scenario["content"]

with gr.Blocks(
    css=css,
    theme=brand_theme,
    title="Azure OpenAI GPT-Audio TTS Soundboard"
) as demo:
    with gr.Row():
        gr.HTML(
            '''
            <div style="text-align: center;">
                <h1 style="color: #2d3748; margin-bottom: 10px;">Azure OpenAI TTS Soundboard</h1>
                <p style="color: #718096; font-size: 16px;">Create engaging audio content with AI-powered text-to-speech</p>
            </div>
            '''
        )
    
    # Voice Selection Section
    with gr.Row():
        with gr.Column():
            voice_label = gr.Label("Current Voice: Alloy", show_label=False, container=False)
    
    # Voice Buttons
    with gr.Row(elem_classes="voice-buttons"):
        alloy = gr.Button("Alloy", variant="primary", elem_classes="voice-button")
        ash = gr.Button("Ash", variant="secondary", icon="assets/ic_fluent_sound_wave_circle_sparkle_24_regular.svg", elem_classes="voice-button")
        ballad = gr.Button("Ballad", variant="secondary", icon="assets/ic_fluent_sound_wave_circle_sparkle_24_regular.svg", elem_classes="voice-button")
        coral = gr.Button("Coral", variant="secondary", icon="assets/ic_fluent_sound_wave_circle_sparkle_24_regular.svg", elem_classes="voice-button")
        echo = gr.Button("Echo", variant="secondary", elem_classes="voice-button")
        fable = gr.Button("Fable", variant="secondary", elem_classes="voice-button")
        nova = gr.Button("Nova", variant="secondary", elem_classes="voice-button")
        onyx = gr.Button("Onyx", variant="secondary", elem_classes="voice-button")
        sage = gr.Button("Sage", variant="secondary", icon="assets/ic_fluent_sound_wave_circle_sparkle_24_regular.svg", elem_classes="voice-button")
        shimmer = gr.Button("Shimmer", variant="secondary", elem_classes="voice-button")
        verse = gr.Button("Verse", variant="secondary", icon="assets/ic_fluent_sound_wave_circle_sparkle_24_regular.svg", elem_classes="voice-button")
        random_btn = gr.Button("🎲 Random Voice", variant="primary", elem_classes="random-button")

    def update_button_and_reset(selected_voice):
        global current_voice
        current_voice = selected_voice.lower()
        buttons = reset_buttons()
        buttons["Alloy Ash Ballad Coral Echo Fable Nova Onyx Sage Shimmer Verse".split().index(selected_voice)] = gr.Button(variant="primary")
        return f"Current Voice: {selected_voice}", *buttons

    def update_random_button_enhanced():
        buttons = reset_buttons()
        random_index = random.randint(0, 10)  # Randomly select one button index
        buttons[random_index] = gr.Button(variant="primary")
        selected_voice = "Alloy Ash Ballad Coral Echo Fable Nova Onyx Sage Shimmer Verse".split()[random_index]
        global current_voice
        current_voice = selected_voice.lower()
        return f"Current Voice: {selected_voice}", *buttons

    # Voice button event handlers
    alloy.click(lambda: update_button_and_reset("Alloy"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    ash.click(lambda: update_button_and_reset("Ash"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    ballad.click(lambda: update_button_and_reset("Ballad"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    coral.click(lambda: update_button_and_reset("Coral"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    echo.click(lambda: update_button_and_reset("Echo"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    fable.click(lambda: update_button_and_reset("Fable"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    nova.click(lambda: update_button_and_reset("Nova"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    onyx.click(lambda: update_button_and_reset("Onyx"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    sage.click(lambda: update_button_and_reset("Sage"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    shimmer.click(lambda: update_button_and_reset("Shimmer"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    verse.click(lambda: update_button_and_reset("Verse"), outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])

    random_btn.click(update_random_button_enhanced, outputs=[voice_label, alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse])
    
    # Content Generation Section
    with gr.Row():
        with gr.Column():
            gr.Label("Vibe", container=False)
            with gr.Row(elem_classes="vibe-buttons"):
                all_vibes = load_vibes()
                vibe_buttons, visible_vibes = update_vibe_buttons(all_vibes)
                visible_vibes_state = gr.State(value=visible_vibes)
                shuffle_btn = gr.Button("Shuffle", variant="huggingface", visible=True)
                generate_content_btn = gr.Button("🤖 Generate Random Content (GPT-5 Nano)", variant="secondary", elem_classes="random-button", visible=True)
            vibe_desc = gr.Textbox(show_label=False, container=False, lines=8, max_lines=20)

        with gr.Column():
            gr.Label("Script", container=False)
            vibe_script = gr.Textbox(show_label=False, container=False, lines=8, max_lines=20)
            audio_output = gr.Audio(autoplay=True, streaming=True)
            play_btn = gr.Button(value="🎵 Generate Audio", variant="primary", elem_classes="generate-button", visible=True)
            stop_btn = gr.Button(value="⏹️ Stop", variant="stop", visible=False)

        for vibe_button in vibe_buttons:
            vibe_button.click(
                lambda vibe, current_vibes: update_vibe_and_global(vibe, current_vibes),
                inputs=[vibe_button, visible_vibes_state],
                outputs=[vibe_desc, *vibe_buttons, visible_vibes_state, vibe_script]
            )
            
        shuffle_btn.click(shuffle_vibes,
            outputs=[*vibe_buttons, visible_vibes_state]
        )
        
        # Generate random content button handler
        def handle_generate_content():
            try:
                return generate_random_content()
            except Exception as e:
                return f"Error: {str(e)}", "Please check your connection and try again."
        
        generate_content_btn.click(
            handle_generate_content,
            outputs=[vibe_desc, vibe_script]
        )

    def toggle_play_stop(voice_name, vibe_desc, vibe_script):
        """Handle the play button click and toggle button visibility"""
        global is_playing, current_voice, current_vibe
        is_playing = True
        try:            
            api_key = check_api_key()
            
            # Use global current_voice if available, otherwise parse from voice_name
            if current_voice:
                voice_to_use = current_voice
            elif voice_name and isinstance(voice_name, str):
                voice_to_use = voice_name.replace("Voice: ", "").strip().lower()
            else:
                voice_to_use = "alloy"  # default voice
            
            if not voice_to_use:
                raise ValueError("Invalid voice name. Please select a valid voice.")
            
            # Check if we have content to generate audio from
            if not vibe_script or vibe_script.strip() == "":
                raise ValueError("Please add some content to generate audio. You can select a vibe or use the Generate Random Content button.")
            
            # Use vibe description if available, otherwise use a default
            description_to_use = vibe_desc if vibe_desc and vibe_desc.strip() else "Custom content"
            vibe_name = current_vibe if current_vibe else "custom"
            
            # Create a temporary file path
            temp_file = os.path.join(temp_dir, f"{voice_to_use}_{vibe_name}_{int(time.time())}.mp3")
            
            # Generate and save audio to temp file
            asyncio.run(generate_audio_file(vibe_script, temp_file, voice_to_use, description_to_use))
            
            gr.Info(f"Audio playing with {voice_to_use.title()} voice...")
            play_btn = gr.Button(value="🎵 Generate Audio", variant="primary", elem_classes="generate-button", visible=False)
            stop_btn = gr.Button(value="⏹️ Stop", variant="stop", visible=True)
            return play_btn, stop_btn, temp_file  # Return the path to the temp file
            
        except Exception as e:
            is_playing = False
            play_btn = gr.Button(value="Play", variant="primary", icon=os.path.join("assets", "ic_fluent_play_24_filled.svg"), visible=True)
            stop_btn = gr.Button(value="Stop", variant="stop", icon=os.path.join("assets", "ic_fluent_stop_24_filled.svg"), visible=False)            
            raise gr.Error(f"Error playing audio: {str(e)}")

    def handle_stop():
        """Handle the stop button click"""
        global is_playing
        is_playing = False
        gr.Info("Audio stopped")
        play_btn = gr.Button(value="🎵 Generate Audio", variant="primary", elem_classes="generate-button", visible=True)
        stop_btn = gr.Button(value="⏹️ Stop", variant="stop", visible=False)
        return play_btn, stop_btn, None

    play_btn.click(
        toggle_play_stop,
        inputs=[voice_label, vibe_desc, vibe_script],
        outputs=[play_btn, stop_btn, audio_output]
    )
    
    stop_btn.click(
        handle_stop,
        outputs=[play_btn, stop_btn, audio_output]
    )
        
if __name__ == "__main__":
    asyncio.run(demo.launch(favicon_path="assets/ai_studio_icon_color.png"))