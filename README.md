QR Code Video Processing Flask App
This project provides a Flask backend for processing YouTube videos to extract QR codes from frames, generate QR images, and manage metadata in JSON. It uses yt-dlp to download videos and extract metadata.


Prerequisites
Python 3.8 or higher
yt-dlp (command-line tool)
ffmpeg (for video processing)
pip package manager

Installing yt-dlp
On Ubuntu:
sudo apt update
sudo apt install yt-dlp ffmpeg

On Windows:
Download from https://github.com/yt-dlp/yt-dlp/releases/latest

Installing ffmpeg
On Ubuntu:
sudo apt install ffmpeg

On Windows:
Download from https://ffmpeg.org/download.html

Setup Instructions
1. Clone or copy the project
git clone https://github.com/skosanke/qr_manager
cd your-repo-folder

2. Create and activate Python virtual environment
On Ubuntu / macOS
python3 -m venv venv
source venv/bin/activate

On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate

4. Install dependencies
pip install -r requirements.txt

5. Run the Flask app
python app.py
By default, the Flask server will listen on all interfaces at port 5000:


Front End
Prerequisites
Node.js (version 16 or higher recommended)

npm (comes with Node.js) or yarn

Setup Instructions
1. Navigate to the frontend directory
If your React app is inside a subfolder like frontend/, change into that directory.
Otherwise, run these commands in your project root if React code is there.
cd frontend

2. Install dependencies
Using npm:
npm install

Or using yarn:
yarn install

3. Configure API base URL (optional)
By default, the React app points to:
const API_BASE_URL = 'http://localhost:5000';
If your Flask backend is running on a different host or port, update this URL in your React app's App.tsx or equivalent config file.

4. Start the development server
Using npm:
npm start

Or yarn:
yarn start
This will start the React development server on http://localhost:3000.

5. Open the app in your browser
Visit http://localhost:3000 to use the frontend interface.

Build for production
To create an optimized build for deployment:
npm run build
or
yarn build

This outputs static files to the build/ folder that can be served by any static file server or integrated with your backend.

