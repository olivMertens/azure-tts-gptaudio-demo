# Azure OpenAI TTS Demo

A comprehensive demonstration of Azure OpenAI's GPT-Audio text-to-speech capabilities using the latest `gpt-audio` model with chat completions API. This demo includes an interactive soundboard with multiple voice options, vibe selection, and random content generation.

![Azure OpenAI TTS Soundboard](assets/aoai-tts-soundboard.gif)

## Features

- 🎤 **11 Voice Options**: Choose from Alloy, Ash, Ballad, Coral, Echo, Fable, Nova, Onyx, Sage, Shimmer, and Verse
- 🎭 **Vibe System**: Select different content vibes (Confident, Excited, Friendly, etc.)
- 🎲 **Random Content Generation**: Generate creative content for different scenarios:
  - Children's stories
  - Financial reports  
  - Technical podcasts
- 🎵 **Real-time Audio Generation**: Stream audio directly using Azure OpenAI's gpt-audio model
- 🔄 **Random Voice Selection**: Automatically select random voices for varied audio experiences
- 🎨 **Clean, Professional UI**: Modern, responsive interface built with Gradio

## Prerequisites

- Python 3.8+
- Azure OpenAI Service subscription
- Access to the `gpt-audio` model (requires approval)
- Azure OpenAI API key and endpoint

## Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Azure-Samples/azure-openai-tts-demo.git
cd azure-openai-tts-demo
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-audio-deployment-name

# Optional: For random content generation
AZURE_OPENAI_TEXT_ENDPOINT=https://your-text-resource.cognitiveservices.azure.com/
AZURE_OPENAI_TEXT_API_KEY=your_text_api_key_here
AZURE_OPENAI_TEXT_DEPLOYMENT_NAME=your-gpt-text-deployment-name
AZURE_OPENAI_TEXT_API_VERSION=2024-12-01-preview
```

#### Getting Your Azure OpenAI Credentials:

1. **Create Azure OpenAI Resource**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a new "Azure OpenAI" resource
   - Note the endpoint URL and get API keys from "Keys and Endpoint" section

2. **Deploy GPT-Audio Model**:
   - In Azure OpenAI Studio, go to "Deployments"
   - Create new deployment with model `gpt-audio` (requires approval)
   - Note your deployment name

3. **API Version**:
   - Use `2025-01-01-preview` for gpt-audio model
   - Use `2024-12-01-preview` for text generation models

### 4. Run the Application

#### Interactive Soundboard (Recommended)
```bash
python soundboard.py
```
This launches a web interface at `http://127.0.0.1:7860`

#### Command Line Examples

**Streaming TTS to File:**
```bash
python streaming-tts-to-file-sample.py
```

**Async Streaming TTS:**
```bash
python async-streaming-tts-sample.py
```

## Usage Guide

### Soundboard Interface

1. **Select Voice**: Click any voice button (Alloy, Ash, Ballad, etc.) to select it
2. **Choose Vibe**: Select a content vibe that matches your desired tone
3. **Add Content**: 
   - Use existing script text, or
   - Click "🎪 Generate Random Content" for AI-generated content
4. **Generate Audio**: Click "🎵 Generate Audio" to create speech
5. **Random Selection**: Use "🎲 Random Voice" to automatically pick a voice

### Voice Options

| Voice | Characteristics |
|-------|----------------|
| **Alloy** | Balanced, natural tone |
| **Ash** | Clear, professional |
| **Ballad** | Melodic, storytelling |
| **Coral** | Warm, engaging |
| **Echo** | Resonant, authoritative |
| **Fable** | Narrative, expressive |
| **Nova** | Bright, energetic |
| **Onyx** | Deep, confident |
| **Sage** | Wise, measured |
| **Shimmer** | Light, pleasant |
| **Verse** | Rhythmic, poetic |

### Content Vibes

Choose from various vibes to set the right tone:
- **Confident**: Professional and assured delivery
- **Excited**: Energetic and enthusiastic 
- **Friendly**: Warm and approachable
- **Shouting**: Loud and attention-grabbing
- **Whispering**: Soft and intimate
- **Terrified**: Dramatic and fearful
- **Unfriendly**: Cold and distant
- **Cheerful**: Happy and upbeat
- **Sad**: Melancholic and somber

## API Configuration

### GPT-Audio Model Setup

The demo uses Azure OpenAI's `gpt-audio` model via the Chat Completions API:

```python
# Example API call structure
response = client.chat.completions.create(
    model="gpt-audio",  # Your deployment name
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "mp3"},
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Your text to convert to speech"}
    ]
)
```

### Required API Versions
- **GPT-Audio**: `2025-01-01-preview`
- **Text Models**: `2024-12-01-preview`

## File Structure

```
azure-openai-tts-demo/
├── soundboard.py                    # Main interactive soundboard
├── streaming-tts-to-file-sample.py  # File-based TTS example
├── async-streaming-tts-sample.py    # Async TTS example
├── vibe.json                        # Vibe configurations
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .gitignore                      # Git ignore rules
└── assets/                         # UI assets and icons
    ├── ai_studio_icon_color.png
    ├── aoai-tts-soundboard.gif
    └── *.svg
```

## Troubleshooting

### Common Issues

**1. Module Not Found Errors**
```bash
# Install missing dependencies
pip install python-multipart
pip install --upgrade gradio
```

**2. API Authentication Errors**
- Verify your API key and endpoint in `.env`
- Ensure your Azure OpenAI resource has the gpt-audio model deployed
- Check API version compatibility

**3. Model Access Issues**
- GPT-Audio requires special approval from Azure
- Contact Azure support to request access
- Verify model deployment name matches your configuration

**4. Audio Generation Fails**
- Check if your text content is appropriate (no harmful content)
- Verify voice parameter is valid
- Ensure API quota is not exceeded

### Dependencies Conflicts
```bash
# Upgrade conflicting packages
pip install --upgrade fastapi starlette
pip install --upgrade gradio
```

## Development

### Adding New Voices
Update the `VOICES` list in `soundboard.py`:
```python
VOICES = ["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer", "verse", "new_voice"]
```

### Adding New Vibes
Edit `vibe.json` to add new content vibes:
```json
{
  "new_vibe": {
    "description": "Your vibe description",
    "script": "Sample script content"
  }
}
```

### Customizing UI
Modify the CSS section in `soundboard.py` to customize the appearance.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Azure OpenAI documentation
- Submit issues on GitHub
- Contact Azure support for API access questions

---

**Note**: This demo requires access to Azure OpenAI's `gpt-audio` model, which is currently in preview and requires approval. Make sure you have proper access before setting up the demo.
