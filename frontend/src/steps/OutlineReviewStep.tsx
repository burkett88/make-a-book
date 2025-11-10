import { useState } from 'react';
import { StepLayout } from '../components/StepLayout';
import type { BookData } from '../types';

interface OutlineReviewStepProps {
  bookData: BookData;
  onUpdate: (data: Partial<BookData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const OutlineReviewStep = ({ bookData, onUpdate, onNext, onBack }: OutlineReviewStepProps) => {
  const [feedback, setFeedback] = useState('');
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock updated outline
      const updatedOutline = `
# ${bookData.title}

## Chapter 1: The Beginning
A compelling introduction that sets the stage for our journey, incorporating your feedback: "${feedback}"

## Chapter 2: Building Foundation
Essential concepts and frameworks that will guide the reader through the core material.

## Chapter 3: Deep Dive
Advanced techniques and methodologies with practical examples.

## Chapter 4: Implementation
Real-world applications and case studies demonstrating the concepts in action.

## Chapter 5: Mastery
Advanced strategies and expert insights for achieving excellence.

## Chapter 6: Future Perspectives
Looking ahead at trends and developments in this field.

## Conclusion
Bringing everything together with actionable takeaways and next steps.
      `.trim();
      
      onUpdate({ outline: updatedOutline });
      setFeedback('');
    } catch (error) {
      console.error('Error regenerating outline:', error);
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleApprove = () => {
    onNext();
  };

  return (
    <StepLayout
      title="Review Your Book Outline"
      description="Review the generated outline and provide feedback or approve to continue"
    >
      <div className="space-y-8">
        {/* Outline Display */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4 gradient-text">Generated Outline</h3>
          <div className="outline-content">
            {bookData.outline ? (
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
                {bookData.outline}
              </pre>
            ) : (
              <div className="text-center py-12">
                <div className="spinner mx-auto mb-4"></div>
                <p className="text-gray-500">Generating your book outline...</p>
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

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
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
                disabled={isRegenerating}
                className="btn btn-outline"
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