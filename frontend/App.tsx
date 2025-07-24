import React, { useState, useEffect, useCallback, useMemo } from 'react';
import type { Video } from './types';
import ChannelList from './components/ChannelList';
import VideoList from './components/VideoList';
import ProcessVideoForm from './components/ProcessVideoForm';
import QRModal from './components/QRModal';
import { Spinner } from './components/Icons';
import { MOCK_CHANNELS, MOCK_VIDEOS } from './mockData';

const API_BASE_URL = 'http://localhost:5000';
const USE_MOCK_DATA = false;

const App: React.FC = () => {
  const [channels, setChannels] = useState<string[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalVideo, setModalVideo] = useState<Video | null>(null);

  const fetchVideos = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (USE_MOCK_DATA) {
        setVideos(MOCK_VIDEOS);
        return MOCK_VIDEOS;
      }

      const response = await fetch(`${API_BASE_URL}/videos`);
      if (!response.ok) throw new Error('Failed to fetch videos from server.');

      const data: Video[] = await response.json();
      setVideos(data);
      return data;

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchChannels = useCallback(async () => {
    setError(null);
    try {
      if (USE_MOCK_DATA) {
        const mockChannels = ["@pokerev", "@ctr"];
        setChannels(mockChannels);
        if (!selectedChannel && mockChannels.length > 0) {
          setSelectedChannel(mockChannels[0]);
        }
        return;
      }

      const res = await fetch(`${API_BASE_URL}/channels`);
      if (!res.ok) throw new Error('Failed to fetch channels');
      const data = await res.json();
      const sortedChannels = (data.channels || []).sort();
      setChannels(sortedChannels);
      if (!selectedChannel && sortedChannels.length > 0) {
        setSelectedChannel(sortedChannels[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load channels');
    }
  }, [selectedChannel]);

  useEffect(() => {
    fetchChannels();
    fetchVideos().then(() => {});
  }, [fetchChannels, fetchVideos]);

  const handleAddChannel = async (channel: string) => {
    setError(null);
    try {
      if (USE_MOCK_DATA) {
        setChannels(prev => [...prev, channel].sort());
        setSelectedChannel(channel);
        return;
      }

      const res = await fetch(`${API_BASE_URL}/channels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Failed to add channel');
      }

      await fetchChannels();
      setSelectedChannel(channel);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error adding channel');
    }
  };

  const handleDeleteChannel = async (channel: string) => {
    setError(null);
    try {
      if (USE_MOCK_DATA) {
        setChannels(prev => prev.filter(c => c !== channel));
        setVideos(prev => prev.filter(v => v.channel !== channel));
        if (selectedChannel === channel) {
          setSelectedChannel(channels.length > 1 ? channels.filter(c => c !== channel)[0] : null);
        }
        return;
      }

      const res = await fetch(`${API_BASE_URL}/channels/${encodeURIComponent(channel)}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Failed to delete channel');
      }

      await fetchChannels();
      await fetchVideos();

      if (selectedChannel === channel) {
        setSelectedChannel(channels.length > 1 ? channels.filter(c => c !== channel)[0] : null);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error deleting channel');
    }
  };

  const filteredVideos = useMemo(() => {
    if (!selectedChannel) return [];
    return videos.filter(video => video.channel === selectedChannel);
  }, [videos, selectedChannel]);

 const handleProcessVideo = async (url: string) => {
  setIsProcessing(true);
  setError(null);
  try {
    const response = await fetch(`${API_BASE_URL}/process_video`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }), // Remove channel
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.error || 'Failed to process video.');
    }

    await fetchChannels();
    await fetchVideos();

  } catch (err) {
    setError(err instanceof Error ? err.message : 'An unknown processing error occurred.');
  } finally {
    setIsProcessing(false);
  }
};

const handleRefreshChannel = async (channel: string) => {
  setIsProcessing(true);
  setError(null);
  try {
    const res = await fetch(`${API_BASE_URL}/refresh_channel/${encodeURIComponent(channel)}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.error || 'Failed to refresh channel');
    }
    // Refresh videos and channels after processing
    await fetchChannels();
    await fetchVideos();
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Error refreshing channel');
  } finally {
    setIsProcessing(false);
  }
};


  return (
    <>
      <div className="flex h-screen bg-gray-900 text-white font-sans">
        <ChannelList
  channels={channels}
  selectedChannel={selectedChannel}
  onSelectChannel={setSelectedChannel}
  onAddChannel={handleAddChannel}
  onDeleteChannel={handleDeleteChannel}
  onRefreshChannel={handleRefreshChannel}  // <-- new prop here
/>

        <main className="flex-1 p-8 overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center items-center h-full">
              <Spinner className="w-12 h-12 text-blue-500" />
            </div>
          ) : (
            <>
              <ProcessVideoForm 
  onProcessVideo={handleProcessVideo}
  isLoading={isProcessing}
  error={error}
/>
              {selectedChannel ? (
                <VideoList videos={filteredVideos} onViewCodes={setModalVideo} />
              ) : (
                <div className="text-center py-16">
                  <h3 className="text-2xl text-gray-400">Select a channel</h3>
                  <p className="text-gray-500 mt-2">Choose a channel from the sidebar to view its videos, or add a new one.</p>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      <QRModal video={modalVideo} onClose={() => setModalVideo(null)} apiBaseUrl={API_BASE_URL} />
    </>
  );
};

export default App;
