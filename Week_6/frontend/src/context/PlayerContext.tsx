import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

export interface Song {
  id: string;
  name: string;
  artist?: { id: string; name: string };
  album_art?: string;
}

interface PlayerContextType {
  queue: Song[];
  currentIndex: number;
  playing: boolean;
  volume: number;
  play: (song: Song, queue?: Song[]) => void;
  pause: () => void;
  next: () => void;
  prev: () => void;
  setVolume: (v: number) => void;
}

const PlayerContext = createContext<PlayerContextType | undefined>(undefined);

export const PlayerProvider = ({ children }: { children: ReactNode }) => {
  const [queue, setQueue] = useState<Song[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [volume, setVolume] = useState(1);

  const play = (song: Song, newQueue?: Song[]) => {
    if (newQueue) {
      setQueue(newQueue);
      setCurrentIndex(newQueue.findIndex(s => s.id === song.id));
    } else {
      if (!queue.length) setQueue([song]);
      setCurrentIndex(queue.findIndex(s => s.id === song.id));
    }
    setPlaying(true);
  };

  const pause = () => setPlaying(false);
  const next = () => setCurrentIndex(i => (i + 1 < queue.length ? i + 1 : 0));
  const prev = () => setCurrentIndex(i => (i - 1 >= 0 ? i - 1 : queue.length - 1));

  return (
    <PlayerContext.Provider value={{ queue, currentIndex, playing, volume, play, pause, next, prev, setVolume }}>
      {children}
    </PlayerContext.Provider>
  );
};

export const usePlayer = () => {
  const ctx = useContext(PlayerContext);
  if (!ctx) throw new Error('usePlayer must be used within PlayerProvider');
  return ctx;
}; 