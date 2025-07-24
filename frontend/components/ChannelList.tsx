import React, { useState } from 'react';
import { PlusIcon, TrashIcon } from './Icons';

interface ChannelListProps {
  channels: string[];
  selectedChannel: string | null;
  onSelectChannel: (channel: string) => void;
  onAddChannel: (channel: string) => void;
  onDeleteChannel: (channel: string) => void;
  onRefreshChannel: (channel: string) => void;  // <-- Add this
}


const ChannelList: React.FC<ChannelListProps> = ({ channels, selectedChannel, onSelectChannel, onAddChannel, onDeleteChannel, onRefreshChannel }) => {
  const [newChannel, setNewChannel] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddClick = () => {
    setIsAdding(true);
  };
  
  const handleAddChannel = (e: React.FormEvent) => {
    e.preventDefault();
    if (newChannel.trim() && !channels.includes(newChannel.trim())) {
      onAddChannel(newChannel.trim());
      setNewChannel('');
      setIsAdding(false);
    }
  };

  const handleDelete = (e: React.MouseEvent, channel: string) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete channel "${channel}"? This cannot be undone.`)) {
      onDeleteChannel(channel);
    }
  };

  return (
    <aside className="w-64 bg-gray-900/70 border-r border-gray-700/50 p-4 flex flex-col">
      <h2 className="text-xl font-bold text-white mb-4">Channels</h2>
      <div className="flex-grow overflow-y-auto">
        <ul>
          {channels.map((channel) => (
            <li key={channel} className="mb-2">
  <button
    onClick={() => onSelectChannel(channel)}
    className={`w-full text-left px-3 py-2 rounded-md flex justify-between items-center transition-colors duration-200 ${
      selectedChannel === channel
        ? 'bg-blue-600 text-white'
        : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'
    }`}
  >
    <span>{channel}</span>
    {selectedChannel === channel && (
      <div className="flex gap-2">
        <button
          onClick={(e) => { e.stopPropagation(); onRefreshChannel(channel); }}
          title="Refresh Latest Video"
          className="text-green-400 hover:text-green-600 p-1 rounded-full hover:bg-green-700/20"
        >
          ⟳
        </button>

        <button
          onClick={(e) => handleDelete(e, channel)}
          title="Delete Channel"
          className="text-blue-200 hover:text-white p-1 rounded-full hover:bg-white/20"
        >
          <TrashIcon className="w-4 h-4" />
        </button>
      </div>
    )}
  </button>
</li>

          ))}
        </ul>
      </div>

      {isAdding ? (
        <form onSubmit={handleAddChannel} className="mt-4">
          <input
            type="text"
            value={newChannel}
            onChange={(e) => setNewChannel(e.target.value)}
            placeholder="e.g., @newchannel"
            className="w-full bg-gray-700 text-white px-3 py-2 rounded-md border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
          />
          <div className="flex justify-end gap-2 mt-2">
            <button type="button" onClick={() => setIsAdding(false)} className="px-3 py-1 text-sm rounded-md text-gray-300 hover:bg-gray-700">Cancel</button>
            <button type="submit" className="px-3 py-1 text-sm rounded-md bg-blue-600 hover:bg-blue-700 text-white">Add</button>
          </div>
        </form>
      ) : (
        <button
          onClick={handleAddClick}
          className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gray-700/80 rounded-md hover:bg-gray-700 transition-colors duration-200"
        >
          <PlusIcon className="w-5 h-5" />
          Add Channel
        </button>
      )}
    </aside>
  );
};

export default ChannelList;