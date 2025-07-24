import React, { useState } from 'react';

interface Props {
  onProcessVideo: (url: string) => void;
  isLoading: boolean;
  error: string | null;
}

const ProcessVideoForm: React.FC<Props> = ({ onProcessVideo, isLoading, error }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    onProcessVideo(url.trim());
    setUrl('');
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <h2 className="text-xl font-bold mb-4">Process YouTube Video</h2>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="YouTube video URL"
        className="w-full px-4 py-2 text-black rounded mb-2"
        disabled={isLoading}
      />
      <button
        type="submit"
        className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50"
        disabled={isLoading}
      >
        {isLoading ? 'Processing...' : 'Process Video'}
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </form>
  );
};

export default ProcessVideoForm;
