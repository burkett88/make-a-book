import { useState, type FC } from 'react';
import { StepLayout } from '../components/StepLayout';
import type { BookData } from '../types';
import { generateOutline } from '../api';

interface BookSetupStepProps {
  bookData: BookData;
  onUpdate: (data: Partial<BookData>) => void;
  onNext: () => void;
}

export const BookSetupStep: FC<BookSetupStepProps> = ({ 
  bookData, 
  onUpdate, 
  onNext 
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateOutline = async () => {
    if (!bookData.title.trim() || !bookData.prompt.trim()) return;
    
    setIsGenerating(true);
    setError(null);
    
    try {
      const outline = await generateOutline({
        title: bookData.title,
        prompt: bookData.prompt,
      });
      onUpdate({ outline });
      onNext();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to generate outline';
      setError(message);
    } finally {
      setIsGenerating(false);
    }
  };

  const canProceed = bookData.title.trim() && bookData.prompt.trim();

  return (
    <StepLayout
      title="Define the Book Brief"
      description="Give the editorial engine a clear premise so the outline stays focused and publish-ready."
    >
      <div className="space-y-6">
        {/* Book Title */}
        <div>
          <label htmlFor="title" className="form-label">
            Book Title
          </label>
          <input
            type="text"
            id="title"
            value={bookData.title}
            onChange={(e) => onUpdate({ title: e.target.value })}
            placeholder="Enter your book title..."
            className="form-input"
          />
        </div>

        {/* Book Prompt */}
        <div>
          <label htmlFor="prompt" className="form-label">
            Book Topic/Prompt
          </label>
          <textarea
            id="prompt"
            value={bookData.prompt}
            onChange={(e) => onUpdate({ prompt: e.target.value })}
            placeholder="Describe what your book should be about..."
            rows={5}
            className="form-input"
            style={{resize: 'none'}}
          />
        </div>

        {error && (
          <div className="alert error-alert">
            {error}
          </div>
        )}
        <div className="hint-card">
          <p className="hint-title">Pro tip</p>
          <p className="hint-body">
            Mention the audience, tone, and outcome you want the reader to achieve. Clear constraints lead to better
            outlines.
          </p>
        </div>

        {/* Generate Button */}
        <div className="flex justify-center mt-4">
          <button
            onClick={handleGenerateOutline}
            disabled={!canProceed || isGenerating}
            className="btn btn-primary"
          >
            {isGenerating ? (
              <span className="flex items-center">
                <div className="spinner" style={{marginRight: '0.75rem'}}></div>
                Generating Outline...
              </span>
            ) : (
              'Generate Outline'
            )}
          </button>
        </div>
      </div>
    </StepLayout>
  );
};
