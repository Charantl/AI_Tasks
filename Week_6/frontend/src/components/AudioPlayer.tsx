import React, { useRef, useState } from 'react';

interface AudioPlayerProps {
  songUrl: string;
  songName: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ songUrl, songName }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setProgress(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return;
    setDuration(audioRef.current.duration);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = Number(e.target.value);
    setProgress(Number(e.target.value));
  };

  return (
    <div>
      <div>{songName}</div>
      <audio
        ref={audioRef}
        src={songUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setPlaying(false)}
        controls={false}
      />
      <button onClick={togglePlay}>{playing ? 'Pause' : 'Play'}</button>
      <input
        type="range"
        min={0}
        max={duration}
        value={progress}
        onChange={handleSeek}
        style={{ width: 200 }}
      />
      <span>
        {Math.floor(progress)} / {Math.floor(duration)} sec
      </span>
    </div>
  );
}; 