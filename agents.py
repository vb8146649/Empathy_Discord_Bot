import os
import google.generativeai as genai
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

@dataclass
class AnalysisResult:
    is_toxic: bool
    score: float
    reason: str

class EmpathySystem:
    def __init__(self):
        print("🧠 Empathy Agents Initialized...")

    async def agent_watcher(self, text: str) -> AnalysisResult:
        """
        Agent A: Monitors chat. Returns score and reason.
        """
        prompt = f"""
        Analyze the following text for toxicity, aggression, or passive-aggressiveness.
        Output ONLY a JSON string (no markdown) with keys: "score" (0.0 to 1.0), "reason" (short string), "is_toxic" (boolean, true if score > 0.7).
        
        Text: "{text}"
        """
        try:
            response = await model.generate_content_async(prompt)
            # Simple cleanup to ensure we get valid JSON
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            import json
            data = json.loads(clean_text)
            return AnalysisResult(data['is_toxic'], data['score'], data['reason'])
        except Exception as e:
            print(f"Watcher Error: {e}")
            return AnalysisResult(False, 0.0, "Error in analysis")

    async def agent_diplomat(self, text: str) -> str:
        """
        Agent B: Rewrites message using NVC.
        """
        prompt = f"""
        Rewrite the following toxic message into a single, polite sentence using Non-Violent Communication (NVC).
        
        CRITICAL RULES:
        1. Output ONLY the rewritten sentence. 
        2. Do NOT add preamble like "Here is a rewrite".
        3. Do NOT add bullet points or explanations.
        4. Keep it casual and short (for Discord).
        
        Original: "{text}"
        """
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    async def agent_coach(self, original: str, rewritten: str) -> str:
        """
        Agent C: Drafts a friendly DM to the user explaining why their message was blocked.
        """
        prompt = f"""
        Draft a friendly, non-judgmental DM to a user.
        Tell them their message: "{original}" seemed a bit heated.
        Suggest they send this instead: "{rewritten}"
        Ask if they want to use the new version.
        Keep it under 50 words.
        """
        response = await model.generate_content_async(prompt)
        return response.text.strip()