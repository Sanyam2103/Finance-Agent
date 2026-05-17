# AI Engineer Assignment: Writeup

## 1. Memory
**What did you store after Session 1, and what did you deliberately *not* store? Why?**
- **Stored:** I specifically stored learned facts which i achieved by summarizing the entire conversation history via another agent.
I also stored the conversation history but it is not being actively used after creating learned facts.
- **Not Stored:** I did not store the specific transaction details retrieved by tools (e.g., individual Swiggy orders). Instead, I stored the *summarized* insight (total food spending). Storing raw tool output would bloat the memory and might lead to stale data being quoted later; it's better to re-query tools for fresh numbers while keeping the *conclusions* in memory.

## 2. Tools vs. LLM
**Name one decision in your code you gave to the LLM, and one you kept as code. Why each?**
- **LLM Decision:** The decision of *which* tools to call and *how* to interpret the financial data relative to the user's goals (e.g., determining if a ₹80,000 MacBook is "realistic"). This requires financial judgment and context-awareness that is hard to hard-code.
- **Code Decision:** The persistence logic (loading/saving JSON), the summarization / total of different expenses because the cost to do it outside of LLM is way cheaper and more reliable. and the tool execution mapping. These are deterministic tasks where LLM "hallucination" or inefficiency would be a liability.

## 3. AI Usage
**Which parts did you generate with AI? Give one specific example where the AI suggested something and you rejected it — what did it suggest, and why was it wrong?**
- **Generated:** The tool schemas (JSON definitions) and the core agent loop structure were drafted using AI.
- **Rejected Example:** The AI suggested implemeting RAG architecture instead of storing learned fact which i rejected because it had to be very sophisticatedly retrieved and augmented, which in the case of finance, very possibly could have given facts/statements that were not needed.

## 4. One week more
**If you had another week, what one thing would you redesign, and why?**
- I would add a "Financial Scenario Planner" tool that performs "what-if" analyses directly in Python. The LLM would translate complex user goals (e.g., "How can I afford a car?") into a set of financial adjustments to test. This tool would then run a simulation and return a concrete, actionable plan, allowing the agent to provide strategic advice on financial trade-offs instead of just answering simple look up, without relying on the LLM for any of the calculations.
