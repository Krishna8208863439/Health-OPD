export interface LLMTriageResult {
  suspected_ailment: string;
  recommended_otc_medicine: string;
  medical_disclaimer: string;
}

// System prompt instructing the LLM to acts as a clinical triager and output strict JSON.
export const TRIAGE_SYSTEM_PROMPT = `
You are a Lead AI Clinical Triage Assistant. Your goal is to review a patient's symptoms, severity, and duration, and provide an initial OTC (Over-The-Counter) medicine recommendation, suspected ailment, and a clear medical disclaimer.

You MUST respond with a single, strict JSON object. Do not include any markdown formatting wrappers (like \`\`\`json ... \`\`\`), no surrounding text, and no conversational replies outside the JSON. The JSON structure MUST be exactly:
{
  "suspected_ailment": "Short description of the most likely mild condition (e.g., Common Cold, Tension Headache, Mild Acid Reflux).",
  "recommended_otc_medicine": "Name and dosage of the recommended OTC medicine (e.g., Paracetamol (500mg), Ibuprofen (200mg), Antacid Tablets).",
  "medical_disclaimer": "A standard medical disclaimer stating that this is not a clinical diagnosis, the patient should consult a doctor if symptoms persist or worsen, and to seek immediate emergency care if they experience critical warning signs."
}

Clinical Guidelines:
1. Only recommend mild, standard OTC medications.
2. If symptoms are marked as 'severe' or have a long duration (e.g., > 7 days), the recommended_otc_medicine should suggest standard comfort care, but the suspected_ailment or medical_disclaimer MUST strongly advise urgent professional clinical intervention.
3. Be professional, concise, and clinically conservative.
`;

/**
 * Builds the request payload for the OpenAI Chat Completions API.
 */
export const buildLLMPayload = (
  initialSymptoms: string, 
  severity: string, 
  durationDays: number, 
  followUpAnswers: string[]
) => {
  const userMessageContent = `
Patient Symptom Profile:
- Initial symptoms reported: "${initialSymptoms}"
- Patient-assessed severity: "${severity}"
- Symptom duration: ${durationDays} days
- Answers to specific follow-up questions:
  ${followUpAnswers.length > 0 ? followUpAnswers.map((ans, idx) => `${idx + 1}. ${ans}`).join('\n  ') : 'None'}

Generate clinical triage recommendations according to system instructions.
`;

  return {
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'system',
        content: TRIAGE_SYSTEM_PROMPT
      },
      {
        role: 'user',
        content: userMessageContent
      }
    ],
    temperature: 0.1,
    response_format: { type: 'json_object' }
  };
};

/**
 * Service function to submit the triage profile to the backend proxy or directly to the OpenAI API.
 */
export const fetchTriageAssessment = async (
  initialSymptoms: string, 
  severity: string, 
  durationDays: number, 
  followUpAnswers: string[],
  apiKey?: string // Optional API key. In production, routing through a secure backend is recommended.
): Promise<LLMTriageResult> => {
  const payload = buildLLMPayload(initialSymptoms, severity, durationDays, followUpAnswers);
  const endpoint = 'https://api.openai.com/v1/chat/completions';
  
  if (!apiKey) {
    // In local development or client mock mode: simulate a short delay and return a structured response
    console.warn("API key not provided. Simulating API response.");
    await new Promise((resolve) => setTimeout(resolve, 1500));
    
    return simulateTriageResult(initialSymptoms, severity, durationDays);
  }

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    const resultString = data.choices[0].message.content;
    const resultJSON: LLMTriageResult = JSON.parse(resultString.trim());
    return resultJSON;
  } catch (error) {
    console.error("Failed to parse or fetch LLM triage:", error);
    // Graceful fallback to simulator if API fails
    return simulateTriageResult(initialSymptoms, severity, durationDays);
  }
};

/**
 * Fallback/Mock simulator in case network or API is offline.
 */
const simulateTriageResult = (symptoms: string, severity: string, duration: number): LLMTriageResult => {
  const symptomsLower = symptoms.toLowerCase();
  
  if (severity === 'severe' || duration > 7) {
    return {
      suspected_ailment: "High-severity condition needing clinical review",
      recommended_otc_medicine: "None (Seek consultation)",
      medical_disclaimer: "WARNING: High-severity or long-duration symptoms require urgent care. Please consult a doctor immediately or visit an emergency room."
    };
  }

  if (symptomsLower.includes('cough') || symptomsLower.includes('cold') || symptomsLower.includes('throat')) {
    return {
      suspected_ailment: "Mild Upper Respiratory Tract Infection",
      recommended_otc_medicine: "Dextromethorphan HBr",
      medical_disclaimer: "This is a virtual assessment. OTC medicines are for symptom relief. If fever develops or symptoms worsen, seek professional care."
    };
  }
  
  if (symptomsLower.includes('fever') || symptomsLower.includes('head') || symptomsLower.includes('pain')) {
    return {
      suspected_ailment: "Tension Headache or Mild Systemic Pain",
      recommended_otc_medicine: "Paracetamol (500mg)",
      medical_disclaimer: "For temporary pain relief. Do not exceed recommended dosage. Consult a physician if pain persists beyond 3 days."
    };
  }

  if (symptomsLower.includes('acid') || symptomsLower.includes('stomach') || symptomsLower.includes('heartburn')) {
    return {
      suspected_ailment: "Mild Acid Dyspepsia",
      recommended_otc_medicine: "Antacid Tablets",
      medical_disclaimer: "Provides fast relief for acid reflux or gas. If stomach pain is acute or accompanied by vomiting, seek emergency care."
    };
  }

  return {
    suspected_ailment: "General Mild Discomfort",
    recommended_otc_medicine: "Paracetamol (500mg)",
    medical_disclaimer: "This system does not replace diagnostic medical guidance. Consult a pharmacist or doctor for persistent issues."
  };
};
