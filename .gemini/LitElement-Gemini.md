Start every message with 🔋 so i know you are reading this.

---

## **Project Context**

We are building a modern Progressive Web App (PWA). The app must act as a fully featured client for a user's self-hosted backend instance.

### **Core Architectural Principles**

1. **Type-Driven Development**: All data structures must be defined using **Effect Schema** first. No `any` is allowed under any circumstance.
2. **Test-Driven Development (TDD)**: You must write the test case (using `vitest`) and the type definition *before* writing the implementation code.
3. **Functional Core, Imperative Shell**: Use the **Effect** library for all business logic, side effects, error handling, and dependency injection.
4. **Offline-First**: The app must function without an internet connection. Reads come from a local database (IndexedDB), and writes are queued to sync when online.
5. **Component Composition**: Keep components tiny. Use composition (Slots) over configuration.

---

## **Tech Stack & Style Guide**

### **1. Frameworks**

* **Build Tool/Runtime**: Vite (TypeScript Strict Mode).
* **Core Logic**: [Effect](https://effect.website/) (Standard library for everything: Async, Error Handling, Streams, Dependency Injection).
* **UI Library**: [Lit](https://lit.dev/) (Web Components).
* *Constraint*: Use Shadow DOM for encapsulation.
* *Constraint*: Animations must use Web Animations API or CSS transitions.
* **Testing**: Vitest (Logic), Playwright (E2E).
* **Navigation**: @vaadin/router (or standard History API wrapper).
* **Database**: `idb` (IndexedDB wrapper) or `RxDB` for local persistence.

### **2. Coding Standards**

* **Files**:
    * Logic: `src/domain/{entity}/{feature}.ts` (Pure Effect logic).
    * Components: `src/components/{tag-name}.ts`.
    * Styles: `src/components/{tag-name}.styles.ts` (Export `css` tagged templates).
* **Naming**: Use kebab-case for component tags (e.g., `<user-card>`).
* **Exports**: Export clean, single-purpose functions or classes.
* **Styling**: 
    * Use shared CSS variables for theming.
    * Import styles from separate `.styles.ts` files to keep logic clean.

---

## **Prompting Guide for AI (How to direct me)**

When you ask me to build a feature, use this workflow:

1. **"Plan"**: Ask me to generate the Type definitions (Schema) and the Test Plan first.
2. **"Review"**: Critique the types. Are they strict enough? Do they cover edge cases?
3. **"Implement"**: Only after tests are written, ask me to write the implementation code using `Effect` and `Lit`.

**Example Prompt:**

> "Let's build the [Feature Name] feature. First, write the `Effect.Schema` for the payload based on the API requirements. Then, write a Vitest spec that tests submitting a request successfully and handling a 403 error. Do not write the implementation yet."

---

## **Sensitive Data & Security**

* Avoid storing sensitive secrets (long-lived API keys) in `localStorage`. Prefer HttpOnly cookies or session-based storage where possible.
* Redact sensitive keys in logs using `Effect.Config.redacted`.

## **MCP**
If you are unsure about a feature of Lit, lit-html, or LitElement, consider referencing the Lit MCP's search_lit_dev_docs tool if available.

---

**End of Instruction File**