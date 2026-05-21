
---

# Finance Agent

> A lightweight, zero-framework autonomous AI finance companion built using the official Google GenAI SDK. It remembers a user’s long-term goals across sessions, maintains strict tool-calling discipline, and uses explicit code logic for calculations to ensure deterministic accuracy.

---

## 🏗️ Core Architecture & Design Philosophy

This repository implements a production-grade agent loop designed around **four core principles**:

1. **Zero Agent Frameworks:** To demonstrate raw architecture and optimal control over the execution lifecycle, this project uses **no** LangChain, LlamaIndex, or CrewAI. The agent loop, message handling, and tool execution state machine are written entirely in native Python.
2. **Strict Compute Isolation (Code vs. LLM):** * **LLM for Judgment:** High-level contextual reasoning, intent detection, goal alignment, and conversational synthesis are delegated entirely to `gemini-2.5-flash`.
* **Code for Arithmetic:** The model is explicitly prevented from doing math. Tool outputs—such as raw transaction lines or upcoming bills—are dynamically intercepted and parsed via deterministic Python functions (`process_tool_result`) before being relayed to the model. This guarantees 100% computational accuracy and eliminates financial hallucinations.


3. **Session-End Memory Compression:** Instead of passing unbounded conversation histories that bloat context windows and increase latency/token costs, an asymmetrical memory layer summarizes the conversation at the end of each session. It distills deep behavioral nuances and commits them to a permanent, disk-persisted `memory.json` knowledge base.
4. **Tool-Over-Memory Discipline:** When a user asks about their financial status three days later, the agent is instructed to **never** quote numbers from old logs. It proactively re-queries live state tools (`get_account_balance`, `get_upcoming_bills`) to evaluate constraints against fresh real-world data.

---

## 📁 Project Structure

```bash
your-agent/
├── agent.py            # Core agent loop, Gemini configuration, and tool processing pipeline
├── tools.py            # Assignment-provided financial tool stubs and mock database matrices
├── run_session_1.py    # Automated runner executing Monday's financial planning sequence
├── run_session_2.py    # Automated runner executing Thursday's spontaneous purchase evaluation
├── sessions.md         # Exact evaluation transcript scripts
├── writeup.md          # Engineering answers to architectural and evaluation questions
├── memory.json         # Disk-persisted long-term memory layer (Created/Updated at runtime)
├── .env                # Protected environment credential repository
└── .gitignore          # Repository-wide build and cache ignore configuration

```

---

## 🛠️ Execution Pipeline & Lifecycle Management

To simulate real-world passage of time, the project uses two separate test-harness runners acting upon the same underlying disk storage:

### **Session 1 (Monday, Nov 3) — Budgeting & Goal Commitments**

* **Context:** The user just received their monthly post-tax salary of ₹1,20,000.
* **Process:** The agent computes recent spending patterns, flags an over-indexing on food delivery apps, balances the remaining budget against upcoming fixed liabilities, and accepts a hard commitment from the user to isolate ₹30,000 for a house down payment fund.
* **Memory Lifecycle:** At session shutdown, the loop triggers `extract_learned_facts()`. The full transcript is summarized into explicit, non-volatile bullet points (e.g., *"User committed to cutting food delivery in half and saving ₹30,000 this month"*), and saved to `memory.json`.

### **Session 2 (Thursday, Nov 6) — Spontaneous Purchase Evaluation**

* **Context:** The user returns with a spontaneous request: *"Should I buy my colleague's used MacBook for ₹80,000?"*
* **Process:** To maximize speed and avoid trailing noise, the runtime reads the compiled `learned_facts` rather than reading raw historical turns.
* **Tool vs. Memory Balance:** The agent references the ₹30,000 house fund commitment from memory but **safeguards execution** by executing fresh tool calls to check current bank accounts (which reflect a newly debited rent transaction) and outstanding credit card bills. It delivers an objective, context-aware financial health check.

---

## 🚀 Installation & Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd finance-agent

```

### 2. Configure Environment Variables

Create a `.env` file in the root directory and add your Google Gemini API key:

```env
GEMINI_API_KEY=AIzaSyYourActualGeminiKeyGoesHere

```

### 3. Execution Sequence

#### Run Session 1 (Monday Sequence):

Ensure `CURRENT_SESSION = 1` inside `tools.py`, then execute:

```bash
python run_session_1.py

```

*This initializes a fresh `memory.json`, walks through the 4-turn onboarding dialogue, extracts user commitments, and writes the summarized facts to disk.*

#### Run Session 2 (Thursday Sequence):

First, open `tools.py` and flip the environment tracker toggle to session 2:

```python
# tools.py
CURRENT_SESSION = 2

```

Now, trigger the spontaneous decision evaluation:

```bash
python run_session_2.py

```

*The agent will ingest the `memory.json` state, automatically call real-time tools to cross-examine current liquid cash balances, detect that rent has been paid, and evaluate if the ₹80,000 laptop compromises the user's home goal.*

---

## 💡 Architectural Decisions (Deep-Dive Writeup Summary)

* **Why Storing "Learned Facts" beats raw RAG/Vector Embedding:** Financial tracking depends on absolute contextual continuity. Vector chunk retrieval often slices up chronological conversations, losing track of historical updates. Storing consolidated statements instead provides an accurate snapshot of the user's profile across sessions.
* **Deterministic Middleware:** The `process_tool_result` acts as a firewall between raw data and the LLM. For instance, parsing a list of Swiggy expenses into a single summed total reduces model input length, eliminates mathematical inaccuracies, and lowers token utilization fees.
* **Future Extension Plans:** Given an additional week of development, a Python-native *Financial Scenario Planner* tool would be integrated. This tool would ingest potential adjustments (e.g., *"reduce leisure spend by 15% over 6 months"*) and run simulations entirely in code. This allows the agent to deliver actionable data projections without relying on the LLM for predictive mathematical forecasting.
