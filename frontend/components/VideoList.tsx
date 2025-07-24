import React from 'react';
import type { Video } from '../types';
import { EyeIcon } from './Icons';

interface VideoListProps {
  videos: Video[];
  onViewCodes: (video: Video) => void;
}

const VideoList: React.FC<VideoListProps> = ({ videos, onViewCodes }) => {
  if (videos.length === 0) {
    return (
      <div className="text-center py-16">
        <h3 className="text-2xl text-gray-400">No videos found for this channel.</h3>
        <p className="text-gray-500 mt-2">Try processing a new video to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {videos.map((video) => (
        <div key={video.data_path} className="bg-gray-800/50 rounded-lg shadow-lg p-5 flex flex-col justify-between border border-gray-700/50 transition-transform hover:scale-[1.02] hover:border-blue-600/50">
          <div>
            <h4 className="text-lg font-bold text-white truncate mb-2">{video.video}</h4>
            <p className="text-sm text-gray-400 mb-4">
              <span className="font-semibold text-blue-400">{video.total_codes}</span> QR Codes Found
            </p>
          </div>
          <button
            onClick={() => onViewCodes(video)}
            className="w-full mt-2 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gray-700 rounded-md hover:bg-blue-600 transition-colors duration-200"
          >
            <EyeIcon className="w-5 h-5" />
            View Codes
          </button>
        </div>
      ))}
    </div>
  );
};

export default VideoList;