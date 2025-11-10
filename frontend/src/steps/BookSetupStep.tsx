import { useState, type FC } from 'react';
import { StepLayout } from '../components/StepLayout';
import type { BookData } from '../types';

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

  const handleGenerateOutline = async () => {
    if (!bookData.title.trim() || !bookData.prompt.trim()) return;
    
    setIsGenerating(true);
    
    try {
      // TODO: Call API to generate outline
      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockOutline = `# ${bookData.title}

## Chapter 1: Foundation
An engaging introduction that establishes the core concepts and sets the stage for the reader's journey through ${bookData.title.toLowerCase()}.

## Chapter 2: Core Principles  
Building upon the foundation, this chapter explores the essential principles and frameworks that underpin the main subject matter.

## Chapter 3: Practical Applications
Real-world examples and case studies that demonstrate how the concepts can be applied in practice.

## Chapter 4: Advanced Techniques
Deep dive into sophisticated methodologies and advanced strategies for mastery.

## Chapter 5: Integration & Implementation
How to integrate everything learned into a cohesive system and implement it effectively.

## Chapter 6: Future Perspectives
Looking ahead at emerging trends, innovations, and the evolution of this field.

## Conclusion
Synthesizing key insights and providing actionable next steps for continued growth and development.`;
      
      onUpdate({ outline: mockOutline });
      onNext();
    } catch (error) {
      console.error('Failed to generate outline:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const canProceed = bookData.title.trim() && bookData.prompt.trim();

  return (
    <StepLayout
      title="Let's Create Your Book"
      description="Tell us about your book idea and we'll help you create an amazing story!"
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

        {/* Generate Button */}
        <div className="flex justify-center mt-4">
          <button
            onClick={handleGenerateOutline}
            disabled={!canProceed || isGenerating}
            className={`btn ${canProceed && !isGenerating ? 'btn-primary' : ''}`}
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