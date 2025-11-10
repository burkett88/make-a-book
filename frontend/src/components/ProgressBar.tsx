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
    <div style={{maxWidth: '900px', margin: '0 auto'}}>
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center" style={{flex: index < steps.length - 1 ? '1' : 'none'}}>
            {/* Step Circle */}
            <div className="flex" style={{flexDirection: 'column', alignItems: 'center', minWidth: '100px'}}>
              <div
                style={{
                  width: '3rem',
                  height: '3rem',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: '700',
                  fontSize: '1rem',
                  background: step.completed 
                    ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                    : currentStep === step.id 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'rgba(255, 255, 255, 0.3)',
                  color: step.completed || currentStep === step.id ? 'white' : '#9ca3af',
                  border: '2px solid rgba(255, 255, 255, 0.2)',
                  backdropFilter: 'blur(10px)',
                  boxShadow: step.completed || currentStep === step.id 
                    ? '0 10px 25px rgba(0, 0, 0, 0.15)' 
                    : 'none',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  transform: currentStep === step.id ? 'scale(1.1)' : 'scale(1)'
                }}
              >
                {step.completed ? '✓' : step.id}
              </div>
              <span
                style={{
                  marginTop: '0.75rem',
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: step.completed || currentStep === step.id ? 'rgba(255, 255, 255, 0.95)' : 'rgba(255, 255, 255, 0.7)',
                  textAlign: 'center',
                  lineHeight: '1.2',
                  transition: 'color 0.3s ease'
                }}
              >
                {step.title}
              </span>
            </div>
            
            {/* Connecting Line */}
            {index < steps.length - 1 && (
              <div
                style={{
                  flexGrow: 1,
                  height: '3px',
                  margin: '0 1.5rem',
                  borderRadius: '2px',
                  background: step.completed 
                    ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                    : 'rgba(255, 255, 255, 0.2)',
                  transition: 'all 0.4s ease',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                {/* Animated shine effect */}
                {step.completed && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: '-100%',
                      width: '100%',
                      height: '100%',
                      background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)',
                      animation: 'shine 2s ease-in-out infinite'
                    }}
                  />
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};