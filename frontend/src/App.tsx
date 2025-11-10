import { useState } from 'react';
import { ProgressBar } from './components/ProgressBar';
import { BookSetupStep } from './steps/BookSetupStep';
import { OutlineReviewStep } from './steps/OutlineReviewStep';
import type { BookData } from './types';

const STEPS = [
  { id: 1, title: 'Book Setup', completed: false },
  { id: 2, title: 'Review Outline', completed: false },
  { id: 3, title: 'Generate Chapters', completed: false },
  { id: 4, title: 'Voice Setup', completed: false },
  { id: 5, title: 'Create Audiobook', completed: false },
];

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [steps, setSteps] = useState(STEPS);
  const [bookData, setBookData] = useState<BookData>({
    title: '',
    prompt: '',
  });

  const updateBookData = (newData: Partial<BookData>) => {
    setBookData(prev => ({ ...prev, ...newData }));
  };

  const goToNextStep = () => {
    // Mark current step as completed
    setSteps(prev => 
      prev.map(step => 
        step.id === currentStep 
          ? { ...step, completed: true }
          : step
      )
    );
    
    // Move to next step
    setCurrentStep(prev => Math.min(prev + 1, STEPS.length));
  };

  const goToPreviousStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <BookSetupStep
            bookData={bookData}
            onUpdate={updateBookData}
            onNext={goToNextStep}
          />
        );
      case 2:
        return (
          <OutlineReviewStep
            bookData={bookData}
            onUpdate={updateBookData}
            onNext={goToNextStep}
            onBack={goToPreviousStep}
          />
        );
      case 3:
        return (
          <div className="text-center p-8">
            <h2 className="text-2xl font-bold mb-4">Chapter Generation (Coming Soon)</h2>
            <p className="text-gray-600">This step will generate chapters with progress tracking.</p>
          </div>
        );
      case 4:
        return (
          <div className="text-center p-8">
            <h2 className="text-2xl font-bold mb-4">Voice Setup (Coming Soon)</h2>
            <p className="text-gray-600">This step will configure voice settings and preview.</p>
          </div>
        );
      case 5:
        return (
          <div className="text-center p-8">
            <h2 className="text-2xl font-bold mb-4">Audiobook Creation (Coming Soon)</h2>
            <p className="text-gray-600">This step will generate the final audiobook.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen py-12 px-4">
      {/* Floating Background Shapes */}
      <div className="floating-shapes">
        <div className="shape"></div>
        <div className="shape"></div>
        <div className="shape"></div>
      </div>

      {/* Header */}
      <div className="text-center mb-12 fade-in">
        <h1 className="header-title gradient-text">
          ✨ AI Book Generator
        </h1>
        <p className="header-subtitle">
          Create amazing books and audiobooks with the power of AI
        </p>
      </div>

      {/* Progress Bar */}
      <div className="progress-container fade-in">
        <ProgressBar currentStep={currentStep} steps={steps} />
      </div>

      {/* Current Step */}
      <div className="mb-8 fade-in">
        {renderCurrentStep()}
      </div>

      {/* Debug Info */}
      <div className="container mt-8">
        <div className="debug-panel">
          <p><strong>Current Step:</strong> {currentStep}</p>
          <p><strong>Book Title:</strong> {bookData.title || 'Not set'}</p>
          <p><strong>Has Outline:</strong> {bookData.outline ? 'Yes' : 'No'}</p>
        </div>
      </div>
    </div>
  );
}

export default App;