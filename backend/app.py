import os
import re
import cv2
import qrcode
import shutil
import string
import threading
import queue
import json
import requests
import subprocess
import time
import urllib.parse
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyzbar.pyzbar import decode
from PIL import Image
from werkzeug.utils import secure_filename
from flask import send_from_directory
import json
import subprocess

app = Flask(__name__)
CORS(app)  # Allow all origins for dev/testing
frame_queue = queue.Queue(maxsize=100)
seen_data_lock = threading.Lock()
CODE_PATTERN = re.compile(r'^[A-Z0-9]{3,4}-[A-Z0-9]{4}-[A-Z0-9]{3}-[A-Z0-9]{3}$')

DATA_DIR = "data"
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")

VM_USER = "server03"
VM_IP = "192.168.0.101"
VM_TARGET_DIR = f"/home/{VM_USER}/Desktop/files/files/codecards"

def safe_filename(name):
    allowed = string.ascii_letters + string.digits + " -_"
    return ''.join(c if c in allowed else "_" for c in name)

def generate_qr_image(code, path):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)

def extract_channel_from_url(url):
    # Extracts @channelname from the URL
    match = re.search(r'@[\w\d_-]+', url)
    if match:
        return match.group()
    return "unknown_channel"

def get_youtube_channel(url):
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        channel_name = data.get("uploader") or data.get("channel") or "unknown_channel"
        if channel_name and not channel_name.startswith('@'):
            channel_name = '@' + channel_name
        return channel_name
    except Exception as e:
        print(f"[get_youtube_channel] Failed to get uploader for {url}: {e}")
        return "unknown_channel"


def download_video(url, output_path):
    # Uses yt-dlp (or youtube-dl fallback)
    cmd = f'yt-dlp -o "{output_path}" "{url}"'
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def codes_updater():
    while True:
        code = codes_update_queue.get()
        if code is None:
            codes_update_queue.task_done()
            break
        try:
            update_video_codes(channel, video_base, code, output_dir)
        except Exception as e:
            print(f"[codes_updater] Exception updating codes: {e}")
        codes_update_queue.task_done()


def process_video_frames(video_path, output_dir, channel, video_base, num_workers=4):
    output_txt = os.path.join(output_dir, "qr_output.txt")

    if os.path.exists(output_txt):
        os.remove(output_txt)

    # Ensure qr_output.txt exists (empty)
    with open(output_txt, "w", encoding="utf-8") as f:
        pass

    seen_data = set()
    codes_update_queue = queue.Queue()

    def save_data_to_file(data):
        with seen_data_lock:
            if data not in seen_data:
                with open(output_txt, "a", encoding="utf-8") as f:
                    f.write(data + "\n")
                seen_data.add(data)
                print(f"[process_video_frames] New code detected: {data}")
                codes_update_queue.put(data)

    def qr_worker():
        while True:
            frame = frame_queue.get()
            if frame is None:
                frame_queue.task_done()
                break
            decoded = decode(frame)
            for obj in decoded:
                qr_data = obj.data.decode('utf-8').strip().upper()
                if CODE_PATTERN.match(qr_data):
                    save_data_to_file(qr_data)
            frame_queue.task_done()

    def codes_updater():
        while True:
            code = codes_update_queue.get()
            if code is None:
                codes_update_queue.task_done()
                break
            try:
                update_video_codes(channel, video_base, code, output_dir)
            except Exception as e:
                print(f"[codes_updater] Exception updating codes: {e}")
            codes_update_queue.task_done()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Error opening video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(1 * 60 * fps))  # Skip 1 min

    threads = [threading.Thread(target=qr_worker) for _ in range(num_workers)]
    for t in threads:
        t.start()

    updater_thread = threading.Thread(target=codes_updater)
    updater_thread.start()

    print(f"[process_video_frames] Starting frame reading for video '{video_base}'")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        try:
            frame_queue.put(frame, timeout=1)
        except queue.Full:
            time.sleep(0.05)
            try:
                frame_queue.put(frame, timeout=1)
            except queue.Full:
                print("[process_video_frames] Frame queue still full after wait, skipping frame.")

    cap.release()
    for _ in threads:
        frame_queue.put(None)
    frame_queue.join()
    for t in threads:
        t.join()

    codes_update_queue.put(None)
    codes_update_queue.join()
    updater_thread.join()

    print(f"[process_video_frames] Finished processing frames for video '{video_base}'")


@app.route("/channels/<channel>", methods=["DELETE"])
def delete_channel(channel):
    channels_data = load_channels()
    if channel not in channels_data:
        return jsonify({"error": "Channel not found"}), 404
    del channels_data[channel]
    save_channels(channels_data)
    return jsonify({"message": f"Channel {channel} deleted"})


from datetime import datetime

def load_channels():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(CHANNELS_FILE):
        return {}

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure upload_date exists and sort videos by upload_date desc
    for channel, entry in data.items():
        if not isinstance(entry, dict):
            continue
        videos = entry.get("videos", [])
        for video in videos:
            # Add upload_date default if missing
            if "upload_date" not in video:
                video["upload_date"] = "1970-01-01T00:00:00"

        # Sort videos by upload_date descending
        try:
            videos.sort(key=lambda v: datetime.fromisoformat(v["upload_date"]), reverse=True)
        except Exception as e:
            print(f"[load_channels] Warning: failed to sort videos for {channel}: {e}")

        entry["videos"] = videos
        data[channel] = entry

    return data


def save_channels(data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[save_channels] Saved channels.json with keys: {list(data.keys())}")



def generate_outputs(output_dir, output_txt, video_name):
    valid_codes = []
    with open(output_txt, "r", encoding="utf-8") as f:
        for line in f:
            code = line.strip().upper()
            if CODE_PATTERN.match(code):
                valid_codes.append(code)

    # Save metadata JSON with codes only
    metadata_path = os.path.join(output_dir, "data.json")
    with open(metadata_path, "w", encoding="utf-8") as jf:
        json.dump({
            "video": video_name,
            "total_codes": len(valid_codes),
            "codes": valid_codes
        }, jf, indent=2)

    # Skip generating PNG images and PDFs on backend

    return {
        "json": metadata_path,
        "codes": valid_codes
    }

def sanitize_title(title):
    # Allow letters, digits, dash, underscore; replace others with underscore
    allowed = string.ascii_letters + string.digits + "-_"
    return ''.join(c if c in allowed else '_' for c in title)

def get_youtube_title(url):
    try:
        # Run yt-dlp to get the video title
        result = subprocess.run(
            ['yt-dlp', '--get-title', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        title = result.stdout.strip()
        return title
    except Exception as e:
        print(f"[get_youtube_title] Failed to get title for {url}: {e}")
        return None

def update_video_codes(channel, video_base, code, output_dir):
    """Add code to channels.json incrementally."""
    with seen_data_lock:
        channels_data = load_channels()
        if channel not in channels_data:
            channels_data[channel] = {"channel_id": None, "videos": []}

        channel_entry = channels_data[channel]
        videos = channel_entry.get("videos", [])

        # Find video entry or create one
        video_entry = next((v for v in videos if v["video"] == video_base), None)
        if not video_entry:
            video_entry = {
                "video": video_base,
                "upload_date": upload_date,  # pass this in or use default, adjust function signature
                "total_codes": 0,
                "codes": [],
                "data_path": os.path.relpath(output_dir, DATA_DIR)
            }
            videos.append(video_entry)
            print(f"[update_video_codes] Created new video entry for '{video_base}' in channel '{channel}'")
        # Add code if not present
        if code not in (c["code"] for c in video_entry["codes"]):
            img_dir = os.path.join(output_dir, "qr_images")
            os.makedirs(img_dir, exist_ok=True)
            img_name = f"qr_{video_entry['total_codes']:03d}.png"
            img_path = os.path.join(img_dir, img_name)
            generate_qr_image(code, img_path)
            video_entry["codes"].append({"code": code, "image": img_name})
            video_entry["total_codes"] = len(video_entry["codes"])
            print(f"[update_video_codes] Added code '{code}' to video '{video_base}'")

        channel_entry["videos"] = videos
        channels_data[channel] = channel_entry

        save_channels(channels_data)


@app.route("/process_video", methods=["POST"])
def process_video():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing video URL"}), 400

    channel = get_youtube_channel(url)
    print(f"[process_video] Extracted channel from metadata: {channel}")

    title = get_youtube_title(url)
    if not title:
        return jsonify({"error": "Failed to retrieve video title"}), 500

    video_base = sanitize_title(title)
    upload_date = get_youtube_upload_date(url)

    channel_dir = os.path.join(DATA_DIR, channel)
    os.makedirs(channel_dir, exist_ok=True)

    output_dir = os.path.join(channel_dir, video_base)
    os.makedirs(output_dir, exist_ok=True)

    video_path = os.path.join(output_dir, video_base + ".mp4")

    channels_data = load_channels()
    if channel not in channels_data:
        channels_data[channel] = {"channel_id": None, "videos": []}
        print(f"[process_video] Added new channel '{channel}' before processing")
        save_channels(channels_data)

    channel_entry = channels_data[channel]
    videos_list = channel_entry.get("videos", [])

    video_exists = any(v["video"] == video_base for v in videos_list)
    if not video_exists:
        videos_list.append({
            "video": video_base,
            "upload_date": upload_date,
            "total_codes": 0,
            "codes": [],
            "data_path": os.path.relpath(output_dir, DATA_DIR),
        })
        channel_entry["videos"] = videos_list
        channels_data[channel] = channel_entry
        print(f"[process_video] Added video entry '{video_base}' to channel '{channel}' before processing")
        save_channels(channels_data)

    if not os.path.exists(video_path):
        success = download_video(url, video_path)
        if not success:
            return jsonify({"error": "Failed to download video"}), 500

    try:
        output_txt = process_video_frames(video_path, output_dir, channel, video_base)
        result = generate_outputs(output_dir, output_txt, video_base)

        # Update total_codes and codes
        channels_data = load_channels()
        channel_entry = channels_data.get(channel, {"videos": []})
        videos = channel_entry.get("videos", [])
        for v in videos:
            if v["video"] == video_base:
                v["total_codes"] = len(result["codes"])
                v["codes"] = [{"code": c, "image": f"qr_{i:03d}.png"} for i, c in enumerate(result["codes"])]
                break
        channel_entry["videos"] = videos
        channels_data[channel] = channel_entry
        save_channels(channels_data)

        print(f"[process_video] Finished processing video '{video_base}' for channel '{channel}'")

        return jsonify({
            "status": "complete",
            "channel": channel,
            "video": video_base,
            "total_codes": len(result["codes"]),
            "data_path": os.path.relpath(output_dir, DATA_DIR)
        })
    except Exception as e:
        print(f"[process_video] Exception: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

def fix_channels_file():
    data = load_channels()
    changed = False
    for k, v in list(data.items()):
        if isinstance(v, list):  # ← legacy format
            data[k] = {
                "channel_id": None,
                "videos": v
            }
            print(f"[fix_channels_file] Fixed entry for {k}")
            changed = True
    if changed:
        save_channels(data)

# Run once at startup
fix_channels_file()


@app.route("/videos", methods=["GET"])
def list_videos():
    channels_data = load_channels()
    response = []
    for channel, entry in channels_data.items():
        if not isinstance(entry, dict):
            print(f"[list_videos] Skipping malformed entry for channel: {channel}")
            continue

        for video in entry.get("videos", []):
            response.append({
                "channel": channel,
                "video": video.get("video"),
                "total_codes": video.get("total_codes"),
                "codes": video.get("codes"),
                "data_path": video.get("data_path")
            })
    return jsonify(response)


CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")


from flask import abort

@app.route("/channels", methods=["GET"])
def get_channels():
    channels_data = load_channels()
    return jsonify({"channels": list(channels_data.keys())})


@app.route("/channels", methods=["POST"])
def add_channel():
    data = request.json
    new_channel = data.get("channel")
    print(f"Received request to add channel: {new_channel}")
    if not new_channel:
        return jsonify({"error": "No channel provided"}), 400
    channels_data = load_channels()
    if new_channel not in channels_data:
        channels_data[new_channel] = {
            "channel_id": None,
            "videos": []
        }
        save_channels(channels_data)
    return jsonify({"message": "Channel added"})

def get_youtube_upload_date(url):
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        # upload_date is YYYYMMDD string
        raw_date = data.get("upload_date")
        if raw_date and len(raw_date) == 8:
            # Convert to ISO 8601: YYYY-MM-DDT00:00:00
            return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}T00:00:00"
        else:
            return None
    except Exception as e:
        print(f"[get_youtube_upload_date] Failed to get upload date for {url}: {e}")
        return None


@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)
@app.route("/refresh_channel/<channel_handle>", methods=["POST"])
def refresh_channel(channel_handle):
    channels_data = load_channels()
    if channel_handle not in channels_data:
        return jsonify({"error": f"Channel '{channel_handle}' not found"}), 404

    channel_entry = channels_data[channel_handle]
    channel_id = channel_entry.get("channel_id")
    if not channel_id:
        return jsonify({"error": f"Channel ID not found for '{channel_handle}'"}), 400

    uploads_playlist = f"UU{channel_id[2:]}"  # Uploads playlist uses 'UU' prefix

    try:
        # Use yt-dlp to fetch the most recent video metadata
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print-json", f"https://www.youtube.com/playlist?list={uploads_playlist}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Parse only the first line (latest video)
        first_video_json = result.stdout.strip().splitlines()[0]
        video_data = json.loads(first_video_json)
        video_id = video_data.get("id")
        if not video_id:
            return jsonify({"error": "Failed to extract video ID"}), 500

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Check if already processed
        existing_videos = [v["video"] for v in channel_entry.get("videos", [])]
        video_title = get_youtube_title(video_url)
        if not video_title:
            return jsonify({"error": "Failed to get video title"}), 500

        video_base = sanitize_title(video_title)
        if video_base in existing_videos:
            return jsonify({"message": "Video already processed", "video": video_base})

        # Process the video (reuse existing route's logic)
        print(f"[refresh_channel] New video found: {video_url}")
        request_data = {"url": video_url}
        with app.test_request_context(json=request_data):
            return process_video()

    except subprocess.CalledProcessError as e:
        print(f"[refresh_channel] yt-dlp error: {e.stderr}")
        return jsonify({"error": "Failed to retrieve playlist"}), 500
    except Exception as e:
        print(f"[refresh_channel] Exception: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


