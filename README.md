# Paraformer Speech Recognition SDK

A speech recognition SDK based on Alibaba Cloud DashScope, supporting the speech-to-text function for multiple audio formats.

## Functional Features

- Support for multiple audio formats: wav, mp3, m4a, flac, acc
- Provision of two speech recognition models: paraformer-v2, paraformer-v1
- Support for hotword recognition (versions v1 and v2)
- Support for multi-channel selection
- Provision of a filler word filtering function
- Support for timestamp calibration
- Provision of a sensitive word filtering function (filtering or replacement)
- Support for speaker diarization
- Customizable number of speakers
- Support for three languages: Chinese, English, and Japanese
- Provision of two input methods: file upload and URL input
- Automatic saving of recognition results, including JSON, text, and SRT subtitle files

## Installation and Operation

### System Requirements

- Python 3.10+
- pip

### Installation Steps

1. Clone the repository:

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or manage the project with UV:

```bash
uv init
uv sync
```

3. Run the application:

```bash
streamlit run main.py
```

Or use UV for management

```bash
.venv\Scripts\streamlit.exe run main.py
```

Open in the browser: http://localhost:8501

## Usage Instructions

1. Enter the API Key and select the model in "Basic Settings".
2. Configure options such as hotwords, audio channels, and filler word filtering in "Advanced Settings".
3. Enable speaker diarization and set the number of speakers in "Speaker Diarization".
4. Select the recognition language (Chinese, English, or Japanese).
5. Select the input method (upload a file or enter a URL).
6. Click the "Start Recognition" button to perform speech recognition.
7. View the recognition results, which will be automatically saved to the output directory.

## Development Guide

### Project Structure

```
paraformer-sdk/
├── output/            # Output directory for recognition results
├── main.py            # Main program
├── config.json        # Configuration file
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

### Configuration File Explanation

The configuration file `config.json` contains the following fields:

- api_key: Alibaba Cloud DashScope API Key
- model: Speech recognition model to use (paraformer-v2 or paraformer-v1)
- vocabulary_id: Hotword ID (version v2)
- phrase_id: Hotword ID (version v1)
- channel_id: List of audio channel indices
- disfluency_removal_enabled: Whether to enable filler word filtering
- timestamp_alignment_enabled: Whether to enable timestamp calibration
- special_word_filter: Sensitive word filtering method ("", "filter", "replace")
- diarization_enabled: Whether to enable speaker diarization
- speaker_count: Number of speakers

### Contribution Process

Welcome to submit Issues and Pull Requests!

1. Fork this project.
2. Create a feature branch (git checkout -b feature/your-feature).
3. Commit changes (git commit -am 'Add some feature').
4. Push to the branch (git push origin feature/your-feature).
5. Create a Pull Request.

## License

MIT License - See the LICENSE file for details.