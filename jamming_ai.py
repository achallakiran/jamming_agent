import replicate
import requests
from pydub import AudioSegment
import os

# --- CONFIGURATION ---
# Get this from https://replicate.com/account/api-tokens
REPLICATE_API_TOKEN = "r8_API_KEY"

# File Paths
ORIGINAL_SONG = "ed_sheeran_perfect.mp3"
MY_VOICE_SAMPLE = "my_voice_reference.mp3" # 10-20 sec clear recording of you singing
OUTPUT_FILENAME = "perfect_my_version.mp3"

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

def download_file(url, filename):
    """Helper to download audio from Replicate's servers"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return filename
    else:
        raise Exception(f"Failed to download {url}")

def main():
    print(f"🚀 Starting AI Cover Generation for: {ORIGINAL_SONG}")

    # ---------------------------------------------------------
    # STEP 1: SEPARATION (Using Demucs via Replicate)
    # ---------------------------------------------------------
    print("\n--- Phase 1: Separating Vocals & Instrumental ---")
    print("Uploading song to Replicate...")
    
    # We use the 'cjwbw/demucs' model for separation
    model_separation = "cjwbw/demucs:f7071661608670c53d5a15998a12c8e31006815343467c6999a43a051838883d"
    
    output_separation = replicate.run(
        model_separation,
        input={"audio": open(ORIGINAL_SONG, "rb")}
    )
    
    # Demucs returns links for bass, drums, other, vocals. We need Vocals + Other (Instrumental)
    # Note: The output format from this model is usually a dictionary or object. 
    # We extract the specific URLs.
    
    url_vocals = output_separation['vocals']
    
    print("Separation complete. Downloading stems...")
    download_file(url_vocals, "temp_vocals.mp3")
    download_file(output_separation['bass'], "temp_bass.mp3")
    download_file(output_separation['drums'], "temp_drums.mp3")
    download_file(output_separation['other'], "temp_other.mp3")

    # Mix instrumental locally to save API costs/time
    print("Mixing instrumental track...")
    inst_mix = AudioSegment.from_file("temp_bass.mp3") + \
               AudioSegment.from_file("temp_drums.mp3") + \
               AudioSegment.from_file("temp_other.mp3")
    inst_mix.export("temp_instrumental.mp3", format="mp3")

    # ---------------------------------------------------------
    # STEP 2: VOICE CONVERSION (Zero-Shot RVC)
    # ---------------------------------------------------------
    print("\n--- Phase 2: Converting Vocals to Your Voice ---")
    print("Sending vocals and your voice sample to AI...")

    # We use a Zero-Shot RVC model. 
    # 'zsxkib/realistic-voice-cloning' is a popular choice for this.
    # Note: Model versions change. Check https://replicate.com/zsxkib/realistic-voice-cloning for updates.
    model_conversion = "zsxkib/realistic-voice-cloning:0a9c7c558af4c0f20667c1bd1260ce32a2879944a0b9e44e1398660c077b9550"

    output_conversion = replicate.run(
        model_conversion,
        input={
            "input_audio": open("temp_vocals.mp3", "rb"),
            "monitor_audio": open(MY_VOICE_SAMPLE, "rb"), # Your voice reference
            "pitch_change": "no-change", # or "12" for +1 octave, "-12" for -1 octave
            "f0_method": "rmvpe", # Best algorithm for singing
            "index_rate": 0, # 0 for zero-shot (using the monitor_audio directly)
            "protect": 0.33
        }
    )

    print("Conversion complete. Downloading your vocals...")
    download_file(output_conversion, "temp_my_vocals.mp3")

    # ---------------------------------------------------------
    # STEP 3: FINAL MIXING
    # ---------------------------------------------------------
    print("\n--- Phase 3: Mixing Final Track ---")
    
    # Load the converted vocals and the instrumental
    my_vocals = AudioSegment.from_file("temp_my_vocals.mp3")
    instrumental = AudioSegment.from_file("temp_instrumental.mp3")

    # Optional: Add Reverb to vocals to make them sit better in the mix
    # (Pydub doesn't have native reverb, usually you mix dry, but volume balance helps)
    # Reduce instrumental volume slightly if vocals are buried
    final_song = instrumental.overlay(my_vocals, position=0)

    final_song.export(OUTPUT_FILENAME, format="mp3")
    
    print(f"\n🎉 SUCCESS! Your song is ready: {OUTPUT_FILENAME}")
    
    # Cleanup temp files
    files_to_remove = ["temp_vocals.mp3", "temp_bass.mp3", "temp_drums.mp3", 
                       "temp_other.mp3", "temp_instrumental.mp3", "temp_my_vocals.mp3"]
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
