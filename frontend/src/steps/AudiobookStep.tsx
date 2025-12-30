import { useMemo, useState, type FC } from 'react';
import { StepLayout } from '../components/StepLayout';
import type { BookData } from '../types';
import { getAudiobookStatus, startAudiobook } from '../api';

interface AudiobookStepProps {
  bookData: BookData;
  onBack: () => void;
}

export const AudiobookStep: FC<AudiobookStepProps> = ({ bookData, onBack }) => {
  const [includeOutline, setIncludeOutline] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ folder: string; audioFiles: string[] } | null>(null);
  const [progress, setProgress] = useState(0);
  const [completedChapters, setCompletedChapters] = useState(0);
  const [totalChapters, setTotalChapters] = useState(0);
  const fallbackSettings = useMemo(() => ({
    voice: 'fable',
    speed: 1,
    instructions: 'Read with excitement and clarity. Use varied intonation, subtle pauses, and a confident storyteller tone.',
  }), []);

  const handleGenerate = async () => {
    if (!bookData.chapters?.length || !bookData.outline) {
      setError('Chapters and outline are required before generating the audiobook.');
      return;
    }

    const voiceSettings = bookData.voiceSettings ?? fallbackSettings;

    setIsGenerating(true);
    setError(null);

    try {
      setResult(null);
      setProgress(0);
      setCompletedChapters(0);
      setTotalChapters(0);

      const job = await startAudiobook({
        title: bookData.title,
        outline: bookData.outline,
        chapters: bookData.chapters,
        voice: voiceSettings.voice,
        speed: voiceSettings.speed,
        includeOutline,
        instructions: voiceSettings.instructions,
      });

      setTotalChapters(job.total_chapters);

      let isComplete = false;
      while (!isComplete) {
        const status = await getAudiobookStatus(job.job_id);
        setProgress(status.progress);
        setCompletedChapters(status.completed_chapters);
        setTotalChapters(status.total_chapters);

        if (status.status === 'completed' && status.result) {
          setResult({ folder: status.result.folder, audioFiles: status.result.audio_files });
          isComplete = true;
          break;
        }

        if (status.status === 'error') {
          throw new Error(status.error ?? 'Failed to generate audiobook');
        }

        await new Promise((resolve) => setTimeout(resolve, 1500));
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate audiobook';
      setError(message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <StepLayout
      title="Render the Audiobook"
      description="Generate voice files, save text assets, and package the final audiobook output."
    >
      <div className="voice-grid">
        <div className="voice-panel">
          <h3 className="section-title">Generation Options</h3>
          <p className="muted-text">Choose which assets to include before you render audio.</p>

          <label className="toggle-row">
            <input
              type="checkbox"
              checked={includeOutline}
              onChange={(event) => setIncludeOutline(event.target.checked)}
            />
            Include outline narration
          </label>

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
              onClick={handleGenerate}
              disabled={isGenerating}
            >
              {isGenerating ? 'Generating Audiobook...' : 'Generate Audiobook'}
            </button>
          </div>

          {isGenerating && (
            <div className="progress-block">
              <div className="progress-meta">
                <span className="progress-label">Generating chapters</span>
                <span className="progress-percent">{progress}%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
              </div>
              <p className="progress-footnote">
                {completedChapters} of {totalChapters} chapters rendered
              </p>
            </div>
          )}
        </div>

        <div className="voice-panel">
          <h3 className="section-title">Output Summary</h3>
          <p className="muted-text">Your audio files will appear in the project folder.</p>

          {result ? (
            <div className="result-panel">
              <p><strong>Folder:</strong> {result.folder}</p>
              <p><strong>Audio files:</strong> {result.audioFiles.length}</p>
              <div className="chapter-list">
                {result.audioFiles.map((file) => (
                  <div key={file} className="chapter-card">
                    {file}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="spinner"></div>
              <p>No audiobook generated yet.</p>
            </div>
          )}
        </div>
      </div>
    </StepLayout>
  );
};
