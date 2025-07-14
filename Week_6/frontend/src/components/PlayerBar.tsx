import React, { useEffect, useRef } from 'react';
import { usePlayer } from '../context/PlayerContext';
import { AudioPlayer } from './AudioPlayer';

export const PlayerBar: React.FC = () => {
  const { queue, currentIndex, playing, play, pause, next, prev, volume, setVolume } = usePlayer();
  const currentSong = queue[currentIndex];
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  if (!currentSong) return null;

  return (
    <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#222', color: '#fff', padding: 12, display: 'flex', alignItems: 'center', zIndex: 100 }}>
      {currentSong.album_art && <img src={currentSong.album_art} alt="album art" style={{ width: 40, height: 40, marginRight: 12 }} />}
      <div style={{ flex: 1 }}>
        <div>{currentSong.name} {currentSong.artist && <>by {currentSong.artist.name}</>}</div>
        <AudioPlayer songUrl={`/songs/${currentSong.id}/stream`} songName={currentSong.name} />
      </div>
      <button onClick={prev} style={{ marginLeft: 8 }}>Prev</button>
      {playing ? (
        <button onClick={pause} style={{ marginLeft: 8 }}>Pause</button>
      ) : (
        <button onClick={() => play(currentSong, queue)} style={{ marginLeft: 8 }}>Play</button>
      )}
      <button onClick={next} style={{ marginLeft: 8 }}>Next</button>
      <input
        type="range"
        min={0}
        max={1}
        step={0.01}
        value={volume}
        onChange={e => setVolume(Number(e.target.value))}
        style={{ marginLeft: 16, width: 100 }}
      />
      {currentSong && (
        <audio ref={audioRef} src={currentSong.audio_url} autoPlay={playing} />
      )}
    </div>
  );
}; 