import type { FC, ReactNode } from 'react';

interface StepLayoutProps {
  title: string;
  description: string;
  children: ReactNode;
}

export const StepLayout: FC<StepLayoutProps> = ({ title, description, children }) => {
  return (
    <div className="container">
      <div className="card">
        <div className="text-center mb-8">
          <h2 className="step-title gradient-text">{title}</h2>
          <p className="step-description">{description}</p>
        </div>
        
        <div className="space-y-8">
          {children}
        </div>
      </div>
    </div>
  );
};