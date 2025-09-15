# Azure TTS GPTAudio Demo

A comprehensive demonstration of Azure OpenAI's GPT-Audio text-to-speech capabilities using the latest `gpt-audio` model with chat completions API. This demo features a modern dark-themed interface with an interactive soundboard, multiple voice options, vibe selection, and AI-powered random content generation using GPT-5 Nano.

<!-- GitHub supports direct video links that auto-embed as players -->
![Azure TTS GPTAudio Demo](assets/gptaudio-demorepo.gif)

<!-- Alternative: If you have an MP4, you can also use: -->
<!-- 
Upload your MP4 to GitHub Issues/Discussions as an attachment, then copy the URL:
![Demo Video](https://user-images.githubusercontent.com/your-video-url.mp4)

Or use the assets folder approach:
<img src="assets/gptaudio-demorepo.mp4" width="800" alt="Azure TTS GPTAudio Demo" />
-->

## Features

- 🎤 **11 Voice Options**: Choose from Alloy, Ash, Ballad, Coral, Echo, Fable, Nova, Onyx, Sage, Shimmer, and Verse
- 🎭 **Vibe System**: Select different content vibes (Confident, Excited, Friendly, etc.)
- 🤖 **AI-Powered Content Generation**: Dynamic content creation using GPT-5 Nano for three scenarios:
  - 🧸 Children's stories with moral lessons
  - 📊 Professional financial reports  
  - 🎧 Engaging technology podcasts
- 🎵 **Real-time Audio Generation**: Stream audio directly using Azure OpenAI's gpt-audio model
- 🔄 **Random Voice Selection**: Automatically select random voices for varied audio experiences
- � **Modern Dark Theme**: Professional dark interface optimized for large viewports with excellent readability
- 📱 **Fully Responsive Design**: Scales beautifully from mobile to 4K displays
- 🎨 **Glassmorphism UI**: Modern design with backdrop blur effects and smooth animations

## Prerequisites

- Python 3.8+
- Azure OpenAI Service subscription
- Access to the `gpt-audio`
- Access to GPT-5 Nano model ( for dynamic content generation)
- Azure OpenAI API key and endpoint

## Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/olivMertens/azure-tts-gptaudio-demo.git
cd azure-tts-gptaudio-demo
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

# Optional: GPT-5 Nano for dynamic content generation
AZURE_OPENAI_NANO_DEPLOYMENT_NAME=gpt-5-nano

# Legacy: For fallback text generation (if GPT-5 Nano not available)
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

3. **Deploy GPT-5 Nano (Optional)**:
   - In Azure OpenAI Studio, create a deployment with `gpt-5-nano`
   - This enables dynamic AI-generated content for the random generator
   - If not available, the app will use fallback static content

4. **API Version**:
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

**MP3 File Generation:**
The application generates audio in MP3 format directly from Azure OpenAI's GPT-Audio model. All generated audio files are automatically created as high-quality MP3s suitable for:
- Direct playback in web browsers
- Download and offline listening
- Integration with other audio applications
- Professional audio workflows

The streaming audio generation ensures efficient MP3 creation with optimal file sizes and quality.

**Async Streaming TTS:**
```bash
python async-streaming-tts-sample.py
```

## Usage Guide

### Soundboard Interface (Dark Theme)

The interface features a modern dark theme optimized for large viewports with excellent readability:

1. **Select Voice**: Click any voice button to select it (highlighted in red when active)
2. **Choose Vibe**: Select a content vibe that matches your desired tone (highlighted in purple when active)
3. **Generate Content**: 
   - Use existing script text, or
   - Click "🎪 Generate Random Content" for AI-generated content using GPT-5 Nano
   - Each click randomly generates one of three content types:
     - 🧸 **Children's Story**: Warm, educational tales with moral lessons
     - 📊 **Financial Report**: Professional business presentations
     - 🎧 **Tech Podcast**: Conversational technology discussions
4. **Generate Audio**: Click "🎵 Generate Audio" to create speech with your selected voice and content
5. **Random Selection**: Use "🎲 Random Voice" to automatically pick a voice

### Dark Theme Features

- **Full Viewport**: Utilizes entire screen space for immersive experience
- **High Contrast**: White text on dark backgrounds for excellent readability
- **Smooth Animations**: Professional hover effects and transitions
- **Glassmorphism**: Semi-transparent panels with backdrop blur effects
- **Responsive Grid**: Adapts from 6 columns on large screens to mobile-friendly layouts

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

### AI-Powered Content Generation

The "🎪 Generate Random Content" button uses GPT-5 Nano to create dynamic, fresh content:

**🧸 Children's Stories**
- Warm, educational tales with clear moral lessons
- Child-friendly language optimized for TTS
- Engaging characters and simple narratives

**📊 Financial Reports**
- Professional quarterly business summaries
- Realistic metrics, percentages, and data
- Authoritative tone suitable for investor presentations

**🎧 Tech Podcasts**
- Conversational discussions about emerging technology
- Informative yet engaging podcast-style content
- Natural speaking patterns with enthusiasm and examples

Each click generates completely new content using AI, ensuring variety and freshness in your audio testing.

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
azure-tts-gptaudio-demo/
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
- GPT-5 Nano may not be available in all regions
- Contact Azure support to request access to both models
- Verify model deployment names match your configuration
- If GPT-5 Nano is unavailable, content generation will use static fallback content

**4. Content Generation Issues**
- If GPT-5 Nano content generation fails, the app automatically falls back to static content
- Check console logs for GPT-5 Nano availability messages
- Verify `AZURE_OPENAI_NANO_DEPLOYMENT_NAME` environment variable is set correctly

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
