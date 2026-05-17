# AI Engineer Assignment: Writeup

## 1. Memory
**What did you store after Session 1, and what did you deliberately *not* store? Why?**
- **Stored:** I stored the user's stated goal, financial facts learned (e.g., current account balances, monthly food delivery spending), and specific commitments made (transferring ₹30,000 to the house fund on the 25th). I also stored the conversation history to maintain context.
- **Not Stored:** I did not store the specific transaction details retrieved by tools (e.g., individual Swiggy orders). Instead, I stored the *summarized* insight (total food spending). Storing raw tool output would bloat the memory and might lead to stale data being quoted later; it's better to re-query tools for fresh numbers while keeping the *conclusions* in memory.

## 2. Tools vs. LLM
**Name one decision in your code you gave to the LLM, and one you kept as code. Why each?**
- **LLM Decision:** The decision of *which* tools to call and *how* to interpret the financial data relative to the user's goals (e.g., determining if a ₹80,000 MacBook is "realistic"). This requires financial judgment and context-awareness that is hard to hard-code.
- **Code Decision:** The persistence logic (loading/saving JSON) and the tool execution mapping. These are deterministic tasks where LLM "hallucination" or inefficiency would be a liability.

## 3. AI Usage
**Which parts did you generate with AI? Give one specific example where the AI suggested something and you rejected it — what did it suggest, and why was it wrong?**
- **Generated:** The tool schemas (JSON definitions) and the core agent loop structure were drafted using AI.
- **Rejected Example:** The AI suggested using LangChain's `ConversationSummaryBufferMemory`. I rejected this because the constraints explicitly forbade agent frameworks. I instead implemented a simpler, manual history management and a targeted "fact extraction" prompt which was more lightweight and transparent.

## 4. One week more
**If you had another week, what one thing would you redesign, and why?**
- I would implement a **Semantic Search (RAG) layer** for the memory instead of just appending facts to the prompt. As the conversation grows over months, the prompt would become too large. A vector database (like Chroma or just a simple FAISS index) would allow the agent to pull only the *relevant* memories for the current query, making it much more scalable.
