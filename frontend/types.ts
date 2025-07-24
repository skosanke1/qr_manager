export interface QRCodeData {
  code: string;
  image: string; // e.g., "qr_001.png"
}

export interface Video {
  channel: string;
  video: string; // Title of the video
  total_codes: number;
  codes: QRCodeData[];
  data_path: string; // e.g., "@pokerev/some_video_title" to construct image URLs
}

// Type for the raw video data from the backend GET /videos endpoint
export interface RawVideo {
  video: string;
  total_codes: number;
  codes: QRCodeData[];
  // The backend might be updated to include these:
  channel?: string;
  data_path?: string;
}