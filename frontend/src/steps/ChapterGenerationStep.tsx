import { useState, type FC } from 'react';
import { StepLayout } from '../components/StepLayout';
import type { BookData } from '../types';
import { generateChapters } from '../api';

interface ChapterGenerationStepProps {
  bookData: BookData;
  onUpdate: (data: Partial<BookData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const ChapterGenerationStep: FC<ChapterGenerationStepProps> = ({
  bookData,
  onUpdate,
  onNext,
  onBack,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateChapters = async () => {
    if (!bookData.outline) {
      setError('Outline is required before generating chapters.');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const chapters = await generateChapters({
        title: bookData.title,
        outline: bookData.outline,
      });
      onUpdate({ chapters });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to generate chapters';
      setError(message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleContinue = () => {
    if (bookData.chapters?.length) {
      onNext();
    }
  };

  return (
    <StepLayout
      title="Generate the Full Draft"
      description="Turn the approved outline into a complete manuscript, chapter by chapter."
    >
      <div className="chapter-grid">
        <div className="chapter-panel">
          <h3 className="section-title">Draft Settings</h3>
          <p className="muted-text">
            We will generate chapters based on your outline. This can take several minutes depending on length.
          </p>

          {error && (
            <div className="alert error-alert">
              {error}
            </div>
          )}

          <div className="button-row">
            <button type="button" className="btn btn-secondary" onClick={onBack}>
              ← Back
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleGenerateChapters}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <span className="flex items-center">
                  <span className="spinner"></span>
                  Generating Chapters...
                </span>
              ) : (
                'Generate Chapters'
              )}
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={handleContinue}
              disabled={!bookData.chapters?.length}
            >
              Continue to Voice Setup
            </button>
          </div>
        </div>

        <div className="chapter-panel">
          <h3 className="section-title">Chapter Output</h3>
          <p className="muted-text">
            {bookData.chapters?.length
              ? `Generated ${bookData.chapters.length} chapters.`
              : 'No chapters generated yet.'}
          </p>

          <div className="chapter-list">
            {bookData.chapters?.map((chapter, index) => (
              <article key={index} className="chapter-card">
                <h4>Chapter {index + 1}</h4>
                <p>{chapter.slice(0, 240)}{chapter.length > 240 ? '…' : ''}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </StepLayout>
  );
};
