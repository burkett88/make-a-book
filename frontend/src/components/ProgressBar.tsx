import type { FC } from 'react';

interface Step {
  id: number;
  title: string;
  completed: boolean;
}

interface ProgressBarProps {
  currentStep: number;
  steps: Step[];
}

export const ProgressBar: FC<ProgressBarProps> = ({ currentStep, steps }) => {
  return (
    <div className="progress-rail">
      {steps.map((step) => {
        const state = step.completed
          ? 'completed'
          : currentStep === step.id
            ? 'current'
            : 'upcoming';

        const statusLabel = step.completed
          ? 'Completed'
          : currentStep === step.id
            ? 'In progress'
            : 'Up next';

        return (
          <div
            key={step.id}
            className={`progress-step ${state}`}
            title={`${step.title} · ${statusLabel}`}
          >
            <div className="step-marker">
              {step.completed ? '✓' : step.id}
            </div>
            <div className="step-labels">
              <span className="step-title">{step.title}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
