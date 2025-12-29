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
      {steps.map((step, index) => {
        const state = step.completed
          ? 'completed'
          : currentStep === step.id
            ? 'current'
            : 'upcoming';

        return (
          <div key={step.id} className={`progress-step ${state}`}>
            <div className="step-marker">
              {step.completed ? '✓' : step.id}
            </div>
            <div className="step-labels">
              <span className="step-title">{step.title}</span>
              <span className="step-status">
                {step.completed ? 'Completed' : currentStep === step.id ? 'In progress' : 'Up next'}
              </span>
            </div>
            {index < steps.length - 1 && <div className="step-connector" />}
          </div>
        );
      })}
    </div>
  );
};
