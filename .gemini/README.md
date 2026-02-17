## .gemini MD files


---

## Using Agents from `.gemini/agents`

The `.gemini/agents` directory contains specialized agent instruction files for different roles and tasks, such as frontend development, mobile development, UI design, code review, and testing automation.

**How AI Should Use These Agents:**

1. **Select the Appropriate Agent:**
	- Choose the agent file that best matches the required role or task (e.g., `frontend-developer.md`, `code-reviewer.md`).
2. **Load the Agent Instructions:**
	- Read the agent's instruction file to understand its capabilities, constraints, and workflow.
3. **Delegate Tasks:**
	- When a task matches an agent's specialty, delegate the task to that agent for focused execution (e.g., UI design, code review, test automation).
4. **Integrate Agent Output:**
	- Use the agent's output as part of the overall project workflow, ensuring it aligns with the main instruction set and project requirements.

**Example Workflow:**

> "For a new feature, use the main project instructions to plan the schema and tests. Then, delegate UI implementation to the `ui-designer.md` agent, and code review to the `code-reviewer.md` agent. Integrate their outputs and ensure all requirements are met."

Agents available:

- `frontend-developer.md`
- `mobile-developer.md`
- `typescript-pro.md`
- `ui-designer.md`
- `react-specialist.md`
- `test-automator.md`
- `code-reviewer.md`