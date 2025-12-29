import type { FC, ReactNode } from 'react';

interface StepLayoutProps {
  title: string;
  description: string;
  children: ReactNode;
}

export const StepLayout: FC<StepLayoutProps> = ({ title, description, children }) => {
  return (
    <div className="panel step-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Studio Step</p>
          <h2 className="step-title">{title}</h2>
          <p className="step-description">{description}</p>
        </div>
        <div className="panel-meta">
          <span className="status-pill">Draft Mode</span>
        </div>
      </div>

      <div className="panel-body">
        {children}
      </div>
    </div>
  );
};
