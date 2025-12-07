# AI Voice Swap & Cover Generator

This Python tool automates the process of creating an AI cover song. It takes an existing song, separates the vocals from the instrumental, and replaces the original singer's voice with a target voice (e.g., your own) using the Replicate API.

## 📋 Features
1.  **Stem Separation:** Automatically splits the input song into Vocals and Instrumental using the `Demucs` model.
2.  **Voice Cloning:** Swaps the isolated vocals with a target voice using Zero-Shot RVC (Retrieval-based Voice Conversion).
3.  **Auto-Mixing:** Recombines the new vocals with the original instrumental to create the final track.

## 🛠 Prerequisites

### 1. Python & Libraries
Ensure you have Python 3.8+ installed. Install the Python dependencies:

```bash
pip install -r requirements.txt
