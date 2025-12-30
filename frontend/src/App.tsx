import { useState } from 'react';
import { ProgressBar } from './components/ProgressBar';
import { BookSetupStep } from './steps/BookSetupStep';
import { OutlineReviewStep } from './steps/OutlineReviewStep';
import { ChapterGenerationStep } from './steps/ChapterGenerationStep';
import { VoiceSetupStep } from './steps/VoiceSetupStep';
import { AudiobookStep } from './steps/AudiobookStep';
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
  const [showWorkflowModal, setShowWorkflowModal] = useState(true);
  const [bookData, setBookData] = useState<BookData>({
    title: '',
    prompt: '',
    targetDurationMinutes: 5,
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
          <ChapterGenerationStep
            bookData={bookData}
            onUpdate={updateBookData}
            onNext={goToNextStep}
            onBack={goToPreviousStep}
          />
        );
      case 4:
        return (
          <VoiceSetupStep
            bookData={bookData}
            onUpdate={updateBookData}
            onNext={goToNextStep}
            onBack={goToPreviousStep}
          />
        );
      case 5:
        return (
          <AudiobookStep
            bookData={bookData}
            onBack={goToPreviousStep}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="app">
      {showWorkflowModal && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal-card reveal">
            <div className="modal-header">
              <div>
                <p className="eyebrow">Workflow</p>
                <h2 className="modal-title">Build your audiobook, step by step</h2>
              </div>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => setShowWorkflowModal(false)}
                aria-label="Close workflow overview"
              >
                Close
              </button>
            </div>
            <p className="modal-copy">
              Approve the plan, refine the draft, and select the narration voice that fits your story.
            </p>
            <div className="metric-grid">
              <div className="metric">
                <span className="metric-label">Est. Time</span>
                <span className="metric-value">6-10 min</span>
              </div>
            </div>
            <div className="modal-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setShowWorkflowModal(false)}
              >
                Get started
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="topbar reveal">
        <div className="topbar-main">
          <div className="brand">
            <span className="brand-mark">✶</span>
            <div>
              <div className="brand-title">Storystack</div>
              <div className="brand-subtitle">Build your audiobook</div>
            </div>
          </div>
          <div className="topbar-actions">
            <button
              type="button"
              className="icon-button"
              onClick={() => setShowWorkflowModal(true)}
              aria-label="Open workflow overview"
              title="Workflow overview"
            >
              ?
            </button>
          </div>
        </div>

        <section className="progress-banner">
          <div className="progress-banner-header">
            <p className="eyebrow">Progress</p>
            <span className="progress-summary">Step {currentStep} of {steps.length}</span>
          </div>
          <ProgressBar currentStep={currentStep} steps={steps} />
        </section>
      </header>

      <main className="layout">
        <section className="content content-full">
          <div className="content-header reveal">
            <div>
              <p className="eyebrow">Project</p>
              <h1 className="page-title">{bookData.title || 'Untitled Book'}</h1>
            </div>
          </div>

          <div className="content-body reveal">
            {renderCurrentStep()}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
