# QR Code Management System

This is a full-stack application designed to process YouTube videos, extract QR codes from them, and display the results in a user-friendly web interface. The application is built with a React/TypeScript frontend and a Python/Flask backend.

## Features

- **Channel Management**: Add, delete, and switch between different YouTube channels.
- **Video Processing**: Submit a YouTube video URL to be downloaded and scanned for QR codes.
- **QR Code Gallery**: View all extracted QR codes for a specific video in a modal gallery.
- **Organized View**: Videos are grouped by their associated channel.
- **Backend API**: A Flask-based REST API handles video processing and data retrieval.

## Tech Stack

- **Frontend**:
  - React
  - TypeScript
  - Tailwind CSS
- **Backend**:
  - Python 3
  - Flask
  - OpenCV (`opencv-python`)
  - Pyzbar (`pyzbar`)
  - yt-dlp
  - Pillow
  - qrcode

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Node.js** (v16 or later)
- **Python** (v3.8 or later) and `pip`
- **yt-dlp**: A command-line program to download videos from YouTube.
  - Installation instructions can be found here: [https://github.com/yt-dlp/yt-dlp#installation](https://github.com/yt-dlp/yt-dlp#installation)

---

## How to Run the Application

Follow these steps to set up and run the project locally. The application consists of two main parts: the backend server and the frontend client. Both must be running simultaneously.

### 1. Backend Setup (Flask Server)

The backend is responsible for all the heavy lifting, including downloading and processing videos.

1.  **Navigate to the Backend Directory**:
    Place the `app.py` file in a dedicated backend folder.

2.  **Create a `requirements.txt` file** in the same directory with the following content:
    ```
    Flask
    opencv-python
    pyzbar
    Pillow
    qrcode
    requests
    werkzeug
    ```

3.  **Create and Activate a Virtual Environment**:
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```sh
    # Create the virtual environment
    python -m venv venv

    # Activate it
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

4.  **Install Dependencies**:
    With your virtual environment active, install the required Python packages.
    ```sh
    pip install -r requirements.txt
    ```
    *Note: `pyzbar` may have additional system-level dependencies. Please refer to the [pyzbar documentation](https://pypi.org/project/pyzbar/) for OS-specific installation steps if you encounter issues.*

5.  **Run the Flask Server**:
    ```sh
    python app.py
    ```
    The backend server will start and listen on `http://localhost:5000`. You should see output indicating the server is running.

### 2. Frontend Setup (React App)

The frontend is a static React application that communicates with the backend. It is served directly to the browser without a complex build step.

1.  **Navigate to the Frontend Directory**:
    Place all the frontend files (`index.html`, `index.tsx`, `App.tsx`, `components/`, etc.) in a dedicated frontend folder.

2.  **Serve the Frontend Files**:
    You need a simple HTTP server to serve the `index.html` file and its assets. The easiest way is to use `npx serve`.
    ```sh
    # This command will serve the current directory on port 3000 by default.
    # To specify port 3003 as in the project description:
    npx serve -l 3003
    ```

3.  **Access the Application**:
    Once both servers are running, open your web browser and navigate to:
    **[http://localhost:3003](http://localhost:3003)**

---

## Development Mode (Frontend-Only)

If you want to work on the frontend UI without running the Python backend, you can use the built-in mock data.

1.  Open the `App.tsx` file.
2.  Find the `USE_MOCK_DATA` constant at the top of the file.
3.  Set its value to `true`:
    ```typescript
    const USE_MOCK_DATA = true;
    ```
4.  Restart the frontend server (or let it hot-reload if configured). The app will now use predefined mock data for channels and videos, and API calls will be simulated.

## Backend API Endpoints

- `GET /videos`: Retrieves a list of all processed videos and their metadata.
- `POST /process_video`: Accepts a JSON body `{ "url": "...", "channel": "..." }` to start processing a new YouTube video.
