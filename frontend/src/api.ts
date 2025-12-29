const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface OutlineRequest {
  title: string;
  prompt: string;
}

export interface OutlineFeedbackRequest {
  title: string;
  prompt: string;
  feedback: string;
}

export interface ChaptersRequest {
  title: string;
  outline: string;
}

export interface VoicePreviewRequest {
  voice: string;
  speed: number;
  instructions?: string;
  text: string;
}

export interface AudiobookRequest {
  title: string;
  outline: string;
  chapters: string[];
  voice: string;
  speed: number;
  includeOutline: boolean;
  instructions?: string;
}

interface OutlineResponse {
  outline: string;
}

interface ChaptersResponse {
  chapters: string[];
}

interface AudiobookResponse {
  folder: string;
  audio_files: string[];
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = 'Request failed';
    try {
      const data = await response.json();
      if (typeof data?.detail === 'string') {
        message = data.detail;
      }
    } catch {
      // Ignore JSON parsing errors.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function generateOutline(payload: OutlineRequest): Promise<string> {
  const response = await fetch(`${API_BASE}/api/outline`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await handleResponse<OutlineResponse>(response);
  return data.outline;
}

export async function regenerateOutline(payload: OutlineFeedbackRequest): Promise<string> {
  const response = await fetch(`${API_BASE}/api/outline/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await handleResponse<OutlineResponse>(response);
  return data.outline;
}

export async function generateChapters(payload: ChaptersRequest): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/chapters`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await handleResponse<ChaptersResponse>(response);
  return data.chapters;
}

export async function generateVoicePreview(payload: VoicePreviewRequest): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/voice/preview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = 'Preview request failed';
    try {
      const data = await response.json();
      if (typeof data?.detail === 'string') {
        message = data.detail;
      }
    } catch {
      // Ignore JSON parsing errors.
    }
    throw new Error(message);
  }

  return response.blob();
}

export async function generateAudiobook(payload: AudiobookRequest): Promise<AudiobookResponse> {
  const response = await fetch(`${API_BASE}/api/audiobook`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: payload.title,
      outline: payload.outline,
      chapters: payload.chapters,
      voice: payload.voice,
      speed: payload.speed,
      include_outline: payload.includeOutline,
      instructions: payload.instructions,
    }),
  });

  const data = await handleResponse<AudiobookResponse>(response);
  return data;
}
