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
      <header className="topbar reveal">
        <div className="brand">
          <span className="brand-mark">✶</span>
          <div>
            <div className="brand-title">Book Foundry</div>
            <div className="brand-subtitle">AI Editorial Studio</div>
          </div>
        </div>
        <div className="topbar-actions">
          <button type="button" className="btn btn-ghost">Documentation</button>
          <button type="button" className="btn btn-primary">New Project</button>
        </div>
      </header>

      <main className="layout">
        <aside className="sidebar stagger">
          <div className="sidebar-card">
            <p className="eyebrow">Workflow</p>
            <h2 className="sidebar-title">Turn a prompt into a publish-ready book.</h2>
            <p className="sidebar-copy">
              Outline, draft, and voice your story with a production-grade workflow that keeps you in control.
            </p>
            <div className="metric-grid">
              <div className="metric">
                <span className="metric-label">Est. Time</span>
                <span className="metric-value">6-10 min</span>
              </div>
              <div className="metric">
                <span className="metric-label">Output</span>
                <span className="metric-value">Markdown + Audio</span>
              </div>
              <div className="metric">
                <span className="metric-label">Quality Mode</span>
                <span className="metric-value">Editorial</span>
              </div>
            </div>
          </div>

          <div className="sidebar-card">
            <p className="eyebrow">Progress</p>
            <ProgressBar currentStep={currentStep} steps={steps} />
          </div>

          <div className="sidebar-card">
            <p className="eyebrow">Guidance</p>
            <ul className="tip-list">
              <li>Start with a strong premise and a clear reader promise.</li>
              <li>Use feedback to push for clarity and pacing.</li>
              <li>Lock the outline before drafting chapters.</li>
            </ul>
          </div>
        </aside>

        <section className="content">
          <div className="content-header reveal">
            <div>
              <p className="eyebrow">Project</p>
              <h1 className="page-title">{bookData.title || 'Untitled Book'}</h1>
              <p className="page-subtitle">
                Shape the narrative arc, refine the outline, and prepare for chapter drafting.
              </p>
            </div>
            <div className="header-actions">
              <button type="button" className="btn btn-secondary">Save Draft</button>
              <button type="button" className="btn btn-primary">Publish</button>
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
