from typing import Dict, Any, List
import random
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class ABSimulatorNode:
    """
    A/B Testing Simulator Node for LangGraph.
    Generates variations of copy, runs them against a 'Simulated Audience Agent'
    to predict engagement, and selects the winner to proceed.
    """
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a base piece of copy from the state and generates an A/B test.
        """
        original_copy = state.get("draft_content", "")
        if not original_copy:
            return {"ab_test_winner": "", "ab_test_logs": "No copy to test."}
            
        print("[A/B Simulator] Generating Alternative Copy (Variant B)...")
        variant_b = await self._generate_variant(original_copy)
        
        print(f"[A/B Simulator] Running simulated audience test between Variant A (original) and Variant B...")
        winner, rationale = await self._simulate_audience_test(original_copy, variant_b)
        
        print(f"[A/B Simulator] Winner selected: {winner}")
        
        return {
            "draft_content": original_copy if winner == "Variant A" else variant_b,
            "ab_test_logs": rationale,
            "ab_test_winner": winner
        }

    async def _generate_variant(self, original_copy: str) -> str:
        prompt = ChatPromptTemplate.from_template(
            "You are an expert copywriter. Take the following marketing copy and rewrite it to have a completely different tone (e.g., if it's professional, make it punchy and casual).\n\nOriginal Copy:\n{copy}"
        )
        chain = prompt | self.llm
        response = await chain.ainvoke({"copy": original_copy})
        return response.content

    async def _simulate_audience_test(self, copy_a: str, copy_b: str) -> tuple[str, str]:
        prompt = ChatPromptTemplate.from_template(
            "You are a simulated target audience for a tech product. Read these two variations of marketing copy and determine which one would result in a higher click-through rate (CTR).\n\n"
            "Variant A:\n{copy_a}\n\n"
            "Variant B:\n{copy_b}\n\n"
            "Respond with exactly 'Variant A' or 'Variant B' followed by a newline, and then your rationale."
        )
        chain = prompt | self.llm
        try:
            response = await chain.ainvoke({"copy_a": copy_a, "copy_b": copy_b})
            text = response.content.strip()
            winner = "Variant B" if "Variant B" in text.split("\n")[0] else "Variant A"
            return winner, text
        except Exception:
            # Fallback
            winner = random.choice(["Variant A", "Variant B"])
            return winner, f"API Error. Randomly selected {winner}"
