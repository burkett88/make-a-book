export interface BookData {
  title: string;
  prompt: string;
  targetDurationMinutes: number;
  outline?: string;
  chapters?: string[];
  voiceSettings?: {
    voice: string;
    speed: number;
    instructions: string;
  };
}

export interface StepData {
  id: number;
  title: string;
  description: string;
  completed: boolean;
}

export type WizardStep = 'setup' | 'outline' | 'chapters' | 'voice' | 'export';
