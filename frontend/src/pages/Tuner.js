import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Play, Square, Volume2 } from 'lucide-react';

const STANDARD_TUNING = [
  { note: 'G3', frequency: 196.00, string: 'G', label: 'G String (lowest)' },
  { note: 'D4', frequency: 293.66, string: 'D', label: 'D String' },
  { note: 'A4', frequency: 440.00, string: 'A', label: 'A String' },
  { note: 'E5', frequency: 659.25, string: 'E', label: 'E String (highest)' },
];

const ALTERNATIVE_TUNINGS = [
  { name: 'Standard (G-D-A-E)', strings: [196.00, 293.66, 440.00, 659.25] },
  { name: 'Scordatura (G-D-A-Eb)', strings: [196.00, 293.66, 440.00, 622.25] },
  { name: 'Cross Tuning (G-D-G-D)', strings: [196.00, 293.66, 392.00, 587.33] },
];

export default function Tuner() {
  const [activeString, setActiveString] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [tuningIndex, setTuningIndex] = useState(0);
  const audioCtxRef = useRef(null);
  const oscillatorRef = useRef(null);
  const gainRef = useRef(null);

  const playTone = useCallback((frequency) => {
    stopTone();
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    audioCtxRef.current = ctx;

    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();
    oscillatorRef.current = oscillator;
    gainRef.current = gain;

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);
    gain.gain.setValueAtTime(0, ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.1);

    oscillator.connect(gain);
    gain.connect(ctx.destination);
    oscillator.start();
    setIsPlaying(true);
  }, []);

  const stopTone = useCallback(() => {
    if (oscillatorRef.current) {
      try {
        if (gainRef.current && audioCtxRef.current) {
          gainRef.current.gain.linearRampToValueAtTime(0, audioCtxRef.current.currentTime + 0.1);
          setTimeout(() => {
            try { oscillatorRef.current?.stop(); } catch(e) {}
          }, 150);
        }
      } catch(e) {}
      oscillatorRef.current = null;
    }
    if (audioCtxRef.current) {
      setTimeout(() => {
        try { audioCtxRef.current?.close(); } catch(e) {}
        audioCtxRef.current = null;
      }, 200);
    }
    setIsPlaying(false);
    setActiveString(null);
  }, []);

  useEffect(() => { return () => { stopTone(); }; }, [stopTone]);

  const handleStringClick = (idx) => {
    if (activeString === idx && isPlaying) {
      stopTone();
    } else {
      setActiveString(idx);
      playTone(STANDARD_TUNING[idx].frequency);
    }
  };

  return (
    <div className="space-y-8" data-testid="tuner-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-stone-100">Violin Tuner</h1>
        <p className="text-stone-400 font-body text-sm mt-2">Tap a string to hear its reference tone</p>
      </div>

      {/* Tuning selector */}
      <div className="flex gap-2 flex-wrap" data-testid="tuning-selector">
        {ALTERNATIVE_TUNINGS.map((t, i) => (
          <button
            key={i}
            onClick={() => { setTuningIndex(i); stopTone(); }}
            data-testid={`tuning-option-${i}`}
            className={`px-4 py-2 rounded-full text-xs font-body font-medium transition-all ${
              tuningIndex === i ? 'bg-primary text-white' : 'bg-stone-800 text-stone-400 hover:text-stone-200'
            }`}
          >
            {t.name}
          </button>
        ))}
      </div>

      {/* Tuner Visual */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4" data-testid="tuner-strings">
        {STANDARD_TUNING.map((s, idx) => {
          const isActive = activeString === idx && isPlaying;
          return (
            <button
              key={s.string}
              onClick={() => handleStringClick(idx)}
              data-testid={`string-${s.string.toLowerCase()}`}
              className={`relative flex flex-col items-center justify-center p-6 md:p-8 rounded-2xl border transition-all duration-300 ${
                isActive
                  ? 'bg-primary/10 border-primary/40 shadow-lg shadow-primary/10'
                  : 'bg-background-secondary border-stone-800 hover:border-stone-600'
              }`}
            >
              {isActive && (
                <div className="absolute inset-0 rounded-2xl animate-pulse bg-primary/5" />
              )}
              <span className="font-heading text-4xl md:text-5xl font-bold text-stone-100 relative z-10">{s.string}</span>
              <span className="font-mono text-xs text-stone-500 mt-2 relative z-10">{s.frequency.toFixed(2)} Hz</span>
              <span className="text-[10px] text-stone-600 mt-1 relative z-10">{s.label}</span>
              <div className="mt-4 relative z-10">
                {isActive ? (
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <Volume2 size={18} className="text-primary animate-pulse" />
                  </div>
                ) : (
                  <div className="w-10 h-10 rounded-full bg-stone-800 flex items-center justify-center">
                    <Play size={16} className="text-stone-400 ml-0.5" />
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Stop button */}
      {isPlaying && (
        <div className="flex justify-center">
          <button
            onClick={stopTone}
            data-testid="stop-tone-btn"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 font-body font-medium text-sm hover:bg-red-500/20 transition-colors"
          >
            <Square size={16} /> Stop Tone
          </button>
        </div>
      )}

      {/* Instructions */}
      <div className="p-6 rounded-2xl bg-background-secondary border border-stone-800" data-testid="tuner-instructions">
        <h3 className="font-heading text-lg font-bold text-stone-100 mb-3">How to Tune</h3>
        <ol className="space-y-2 text-stone-400 font-body text-sm list-decimal list-inside">
          <li>Tap a string button above to hear its reference pitch.</li>
          <li>Play the corresponding string on your violin.</li>
          <li>If your string sounds lower, tighten the peg slightly. If higher, loosen it.</li>
          <li>Fine-tune using the fine tuners on the tailpiece for small adjustments.</li>
          <li>Always tune from below the pitch up to it, never from above down.</li>
        </ol>
      </div>

      {/* Tuning tips */}
      <div className="p-6 rounded-2xl bg-amber-500/5 border border-amber-500/20">
        <h3 className="font-heading text-lg font-bold text-amber-200 mb-3">Tuning Tips</h3>
        <ul className="space-y-2 text-amber-200/70 font-body text-sm list-disc list-inside">
          <li>Tune in order: A first, then D, G, and finally E.</li>
          <li>The A string is the reference string (440 Hz), often given by an oboe in orchestras.</li>
          <li>New strings go out of tune quickly. Be patient and retune frequently.</li>
          <li>Turn pegs slowly and carefully to avoid breaking strings.</li>
        </ul>
      </div>
    </div>
  );
}
