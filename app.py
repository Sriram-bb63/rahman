from flask import Flask, render_template, send_from_directory, jsonify, request
import os
import re
from pathlib import Path
from automation import download_audio

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/music'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    """Render the main page with the MP3 player."""
    return render_template('index.html')


@app.route('/get_songs')
def get_songs():
    """API endpoint to get all audio files, returning both display names and full filenames."""
    audio_files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.lower().endswith(('.mp3', '.m4a', '.ogg', '.wav', '.webm')):
            audio_files.append({'display_name': os.path.splitext(f)[0], 'filename': f})  # Send both
    return jsonify(audio_files)


@app.route('/static/music/<filename>')
def serve_audio(filename):
    """Serve the audio file."""
    return send_from_directory(UPLOAD_FOLDER, filename)


# Download as mp3 
@app.route('/download', methods=['POST'])
def download_youtube():
    """Download YouTube audio and save it as MP3."""
    youtube_url = request.form.get('youtube_url')

    if not youtube_url:
        return jsonify({'success': False, 'message': 'No URL provided'}), 400

    # Validate YouTube URL
    if not re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$', youtube_url):
        return jsonify({'success': False, 'message': 'Invalid YouTube URL'}), 400

    try:
        filename = download_audio(youtube_url)
        if filename:
            return jsonify({
                'success': True,
                'message': 'Download completed successfully',
                'filename': filename
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Automation error',
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500



@app.route('/rename_song', methods=['POST'])
def rename_song():
    """Rename a song file."""
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')

    if not old_name or not new_name:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400

    old_path = os.path.join(UPLOAD_FOLDER, old_name)
    old_extension = os.path.splitext(old_name)[1]  # Get the original extension
    new_path = os.path.join(UPLOAD_FOLDER, new_name.strip() + old_extension)  # Preserve extension

    if not os.path.exists(old_path):
        return jsonify({'success': False, 'message': 'File not found'}), 404

    try:
        os.rename(old_path, new_path)
        return jsonify({'success': True, 'message': 'File renamed successfully', 'new_name': os.path.basename(new_path)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
