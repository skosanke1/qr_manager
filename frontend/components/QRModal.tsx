import React from 'react';
import type { Video } from '../types';
import { XMarkIcon } from './Icons';

interface QRModalProps {
  video: Video | null;
  onClose: () => void;
  apiBaseUrl: string;
}

const QRModal: React.FC<QRModalProps> = ({ video, onClose, apiBaseUrl }) => {
  if (!video) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-75 flex justify-center items-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-4 border-b border-gray-700">
          <h3 className="text-xl font-bold text-white truncate pr-4">{video.video}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>
        <div className="p-6 overflow-y-auto">
          {video.codes.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {video.codes.map((qr) => (
                <div key={qr.code} className="bg-gray-700/50 p-3 rounded-lg flex flex-col items-center text-center">
                  <img
                    src={`${apiBaseUrl}/data/${video.data_path}/qr_images/${qr.image}`}
                    alt={qr.code}
                    className="w-full h-auto object-cover rounded-md bg-white mb-3"
                  />
                  <p className="text-xs font-mono text-gray-300 break-all">{qr.code}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No QR codes found for this video.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default QRModal;