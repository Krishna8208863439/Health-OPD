export type TriageState = 
  | 'INITIAL'
  | 'ASKING_SEVERITY'
  | 'ASKING_DURATION'
  | 'DIAGNOSING'
  | 'DIAGNOSED'
  | 'COMPLETED';

export interface TriageContext {
  initialSymptoms: string;
  severity: 'mild' | 'moderate' | 'severe' | null;
  durationDays: number | null;
  followUpAnswers: string[];
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'system' | 'ai';
  text: string;
  timestamp: Date;
}

export interface TriageMachineState {
  currentState: TriageState;
  context: TriageContext;
  messages: ChatMessage[];
}

export type TriageEvent =
  | { type: 'START' }
  | { type: 'SUBMIT_SYMPTOMS'; symptoms: string }
  | { type: 'SUBMIT_SEVERITY'; severity: 'mild' | 'moderate' | 'severe' }
  | { type: 'SUBMIT_DURATION'; days: number }
  | { type: 'RECEIVE_DIAGNOSIS'; suspectedAilment: string; medicine: string; disclaimer: string }
  | { type: 'ADD_TO_CART' }
  | { type: 'RESET' };

/**
 * State machine reducer that determines the next state based on the current state and event.
 */
export const triageReducer = (
  state: TriageMachineState, 
  event: TriageEvent
): TriageMachineState => {
  const timestamp = new Date();

  switch (event.type) {
    case 'START':
      if (state.currentState !== 'INITIAL') return state;
      return {
        ...state,
        currentState: 'INITIAL',
        messages: [
          {
            id: `msg-sys-${Date.now()}`,
            sender: 'system',
            text: "Hello! I am your AI Symptom Triage Assistant. Please describe what symptoms you are experiencing today.",
            timestamp
          }
        ]
      };

    case 'SUBMIT_SYMPTOMS':
      if (state.currentState !== 'INITIAL') return state;
      return {
        currentState: 'ASKING_SEVERITY',
        context: {
          ...state.context,
          initialSymptoms: event.symptoms
        },
        messages: [
          ...state.messages,
          {
            id: `msg-usr-${Date.now()}`,
            sender: 'user',
            text: event.symptoms,
            timestamp
          },
          {
            id: `msg-sys-${Date.now() + 1}`,
            sender: 'system',
            text: "Understood. How severe would you rate these symptoms? Please select Mild, Moderate, or Severe.",
            timestamp
          }
        ]
      };

    case 'SUBMIT_SEVERITY':
      if (state.currentState !== 'ASKING_SEVERITY') return state;
      return {
        currentState: 'ASKING_DURATION',
        context: {
          ...state.context,
          severity: event.severity
        },
        messages: [
          ...state.messages,
          {
            id: `msg-usr-${Date.now()}`,
            sender: 'user',
            text: `I'd rate it as ${event.severity.toUpperCase()}.`,
            timestamp
          },
          {
            id: `msg-sys-${Date.now() + 1}`,
            sender: 'system',
            text: "How long have you been experiencing these symptoms? (Enter number of days)",
            timestamp
          }
        ]
      };

    case 'SUBMIT_DURATION':
      if (state.currentState !== 'ASKING_DURATION') return state;
      return {
        currentState: 'DIAGNOSING',
        context: {
          ...state.context,
          durationDays: event.days
        },
        messages: [
          ...state.messages,
          {
            id: `msg-usr-${Date.now()}`,
            sender: 'user',
            text: `For about ${event.days} day(s).`,
            timestamp
          },
          {
            id: `msg-sys-${Date.now() + 1}`,
            sender: 'system',
            text: "Analyzing your profile and searching clinical recommendations... Please wait.",
            timestamp
          }
        ]
      };

    case 'RECEIVE_DIAGNOSIS':
      if (state.currentState !== 'DIAGNOSING') return state;
      return {
        currentState: 'DIAGNOSED',
        context: state.context,
        messages: [
          ...state.messages,
          {
            id: `msg-ai-${Date.now()}`,
            sender: 'ai',
            text: `Based on your symptom details, here is our virtual assessment:\n\n` +
                 `🩺 **Suspected Ailment:** ${event.suspectedAilment}\n` +
                 `💊 **Recommended OTC Medicine:** ${event.medicine}\n\n` +
                 `⚠️ **Clinical Disclaimer:** ${event.disclaimer}`,
            timestamp
          }
        ]
      };

    case 'ADD_TO_CART':
      if (state.currentState !== 'DIAGNOSED') return state;
      return {
        ...state,
        currentState: 'COMPLETED',
        messages: [
          ...state.messages,
          {
            id: `msg-sys-${Date.now()}`,
            sender: 'system',
            text: "The recommended OTC medicine has been successfully added to your cart. You can review your cart items below.",
            timestamp
          }
        ]
      };

    case 'RESET':
      return {
        currentState: 'INITIAL',
        context: {
          initialSymptoms: '',
          severity: null,
          durationDays: null,
          followUpAnswers: []
        },
        messages: [
          {
            id: `msg-sys-${Date.now()}`,
            sender: 'system',
            text: "Chat reset. Please describe your symptoms to start a new assessment.",
            timestamp
          }
        ]
      };

    default:
      return state;
  }
};

/**
 * Initial empty state config
 */
export const initialTriageState: TriageMachineState = {
  currentState: 'INITIAL',
  context: {
    initialSymptoms: '',
    severity: null,
    durationDays: null,
    followUpAnswers: []
  },
  messages: []
};
