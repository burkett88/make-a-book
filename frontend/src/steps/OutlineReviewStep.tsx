import { useState } from 'react';
import { StepLayout } from '../components/StepLayout';
import type { BookData } from '../types';
import { regenerateOutline } from '../api';

interface OutlineReviewStepProps {
  bookData: BookData;
  onUpdate: (data: Partial<BookData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const OutlineReviewStep = ({ bookData, onUpdate, onNext, onBack }: OutlineReviewStepProps) => {
  const [feedback, setFeedback] = useState('');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegenerate = async () => {
    if (!feedback.trim()) {
      setError('Add feedback before regenerating.');
      return;
    }

    setIsRegenerating(true);
    setError(null);
    try {
      const updatedOutline = await regenerateOutline({
        title: bookData.title,
        prompt: bookData.prompt,
        feedback,
      });
      onUpdate({ outline: updatedOutline });
      setFeedback('');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error regenerating outline';
      setError(message);
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleApprove = () => {
    onNext();
  };

  const canRegenerate = feedback.trim().length > 0;

  return (
    <StepLayout
      title="Review Your Book Outline"
      description="Edit, regenerate, or approve the outline before moving into drafting."
    >
      <div className="space-y-8">
        {/* Outline Display */}
        <div className="outline-panel">
          <div className="outline-header">
            <div>
              <p className="eyebrow">Outline Draft</p>
              <h3 className="section-title">Generated Outline</h3>
            </div>
            <span className="status-pill">Auto-Saved</span>
          </div>
          <div className="outline-content">
            {bookData.outline ? (
              <pre className="outline-pre">
                {bookData.outline}
              </pre>
            ) : (
              <div className="empty-state">
                <div className="spinner"></div>
                <p>Generating your book outline...</p>
              </div>
            )}
          </div>
        </div>

        {/* Feedback Section */}
        {bookData.outline && (
          <div className="space-y-6">
            <div>
              <label htmlFor="feedback" className="form-label">
                Feedback (Optional)
              </label>
              <textarea
                id="feedback"
                className="form-input"
                rows={4}
                placeholder="Share any feedback to improve the outline..."
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                style={{ resize: 'vertical', minHeight: '120px' }}
              />
            </div>
            {error && (
              <div className="alert error-alert">
                {error}
              </div>
            )}

            <div className="button-row">
              <button
                type="button"
                onClick={onBack}
                className="btn btn-secondary"
              >
                ← Back
              </button>
              
              <button
                type="button"
                onClick={handleRegenerate}
                disabled={isRegenerating || !canRegenerate}
                className="btn btn-ghost"
              >
                {isRegenerating ? (
                  <>
                    <div className="spinner mr-2"></div>
                    Regenerating...
                  </>
                ) : (
                  '🔄 Regenerate with Feedback'
                )}
              </button>
              
              <button
                type="button"
                onClick={handleApprove}
                className="btn btn-primary"
              >
                ✓ Approve & Continue
              </button>
            </div>
          </div>
        )}
      </div>
    </StepLayout>
  );
};
