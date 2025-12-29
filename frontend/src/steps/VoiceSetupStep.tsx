import { useEffect, useMemo, useState, type FC } from 'react';
import { StepLayout } from '../components/StepLayout';
import type { BookData } from '../types';
import { generateVoicePreview } from '../api';

interface VoiceSetupStepProps {
  bookData: BookData;
  onUpdate: (data: Partial<BookData>) => void;
  onNext: () => void;
  onBack: () => void;
}

const DEFAULT_INSTRUCTIONS =
  "Read with excitement and clarity. Use varied intonation, subtle pauses, and a confident storyteller tone.";

const VOICE_OPTIONS = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];

export const VoiceSetupStep: FC<VoiceSetupStepProps> = ({
  bookData,
  onUpdate,
  onNext,
  onBack,
}) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fallbackSettings = useMemo(() => ({
    voice: 'fable',
    speed: 1,
    instructions: DEFAULT_INSTRUCTIONS,
  }), []);

  const voiceSettings = bookData.voiceSettings ?? fallbackSettings;

  useEffect(() => {
    if (!bookData.voiceSettings) {
      onUpdate({ voiceSettings: fallbackSettings });
    }
  }, [bookData.voiceSettings, onUpdate, fallbackSettings]);

  const previewText = useMemo(() => {
    if (bookData.chapters?.length) {
      return bookData.chapters[0];
    }
    if (bookData.outline) {
      return bookData.outline;
    }
    return bookData.prompt || 'This is a voice preview of your book.';
  }, [bookData.chapters, bookData.outline, bookData.prompt]);

  const handlePreview = async () => {
    setIsPreviewing(true);
    setError(null);
    try {
      const blob = await generateVoicePreview({
        voice: voiceSettings.voice,
        speed: voiceSettings.speed,
        instructions: voiceSettings.instructions,
        text: previewText,
      });
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate preview';
      setError(message);
    } finally {
      setIsPreviewing(false);
    }
  };

  const updateVoiceSettings = (updates: Partial<typeof voiceSettings>) => {
    onUpdate({
      voiceSettings: {
        ...voiceSettings,
        ...updates,
      },
    });
  };

  return (
    <StepLayout
      title="Voice Direction"
      description="Choose a narrator voice and set the delivery style before rendering audio."
    >
      <div className="voice-grid">
        <div className="voice-panel">
          <label className="form-label" htmlFor="voice">
            Voice Profile
          </label>
          <select
            id="voice"
            className="form-input"
            value={voiceSettings.voice}
            onChange={(event) => updateVoiceSettings({ voice: event.target.value })}
          >
            {VOICE_OPTIONS.map((voice) => (
              <option key={voice} value={voice}>
                {voice.charAt(0).toUpperCase() + voice.slice(1)}
              </option>
            ))}
          </select>

          <label className="form-label" htmlFor="speed">
            Speech Speed ({voiceSettings.speed.toFixed(2)}x)
          </label>
          <input
            id="speed"
            type="range"
            min={0.7}
            max={1.3}
            step={0.05}
            value={voiceSettings.speed}
            onChange={(event) => updateVoiceSettings({ speed: Number(event.target.value) })}
          />

          <label className="form-label" htmlFor="instructions">
            Voice Instructions
          </label>
          <textarea
            id="instructions"
            className="form-input"
            rows={4}
            value={voiceSettings.instructions}
            onChange={(event) => updateVoiceSettings({ instructions: event.target.value })}
          />

          {error && (
            <div className="alert error-alert">
              {error}
            </div>
          )}

          <div className="button-row">
            <button className="btn btn-secondary" type="button" onClick={onBack}>
              ← Back
            </button>
            <button
              className="btn btn-primary"
              type="button"
              onClick={handlePreview}
              disabled={isPreviewing}
            >
              {isPreviewing ? 'Rendering Preview...' : 'Preview Voice'}
            </button>
            <button className="btn btn-ghost" type="button" onClick={onNext}>
              Continue to Audiobook
            </button>
          </div>
        </div>

        <div className="voice-panel">
          <h3 className="section-title">Preview Output</h3>
          <p className="muted-text">Listen to a short excerpt using your current voice settings.</p>

          {previewUrl ? (
            <audio controls src={previewUrl} className="audio-player" />
          ) : (
            <div className="empty-state">
              <div className="spinner"></div>
              <p>No preview generated yet.</p>
            </div>
          )}

          <div className="preview-text">
            <p className="eyebrow">Preview text</p>
            <p>{previewText.slice(0, 260)}{previewText.length > 260 ? '…' : ''}</p>
          </div>
        </div>
      </div>
    </StepLayout>
  );
};
