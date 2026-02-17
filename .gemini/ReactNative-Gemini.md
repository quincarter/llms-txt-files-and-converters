Start every message with 🔋 so i know you are reading this.

---

## **Project Context**

We are building a cross-platform (iOS, Android, Web) mobile application. The app must act as a fully featured client for a user's self-hosted backend instance.

### **Core Architectural Principles**

1. **Type-Driven Development**: All data structures must be defined using **Effect Schema** first. No `any` is allowed under any circumstance.
2. **Test-Driven Development (TDD)**: You must write the test case (using `vitest` or `jest`) and the type definition *before* writing the implementation code.
3. **Functional Core, Imperative Shell**: Use the **Effect** library for all business logic, side effects, error handling, and dependency injection.
4. **Offline-First**: The app must function without an internet connection. Reads come from a local database (SQLite via Expo), and writes are queued to sync when online.
5. **Component Composition**: Keep components tiny. Use composition over configuration.

---

## **Tech Stack & Style Guide**

### **1. Frameworks**

* **Runtime**: Expo (Managed Workflow).
* **Language**: TypeScript (Strict Mode).
* **Core Logic**: [Effect](https://effect.website/) (Standard library for everything: Async, Error Handling, Streams, Dependency Injection).
* **UI Library**: React Native Paper (Material Design 3).
* *Constraint*: All Cards must have rounded edges (`theme.roundness = 2` or higher).
* *Constraint*: Animations must be smooth (use `react-native-reanimated`).
* **Testing**: Jest, Playwright
* **Navigation**: Expo Router (File-based routing).
* **Database**: `expo-sqlite` (for local persistence).

### **2. Coding Standards**

* **Files**:
    * Logic: `src/domain/{entity}/{feature}.ts` (Pure Effect logic).
    * Components: `src/components/{Name}.tsx`.
    * Styles: `src/components/{Name}.styles.ts` (Do not use inline styles. Use strict StyleSheet objects).
* **Exports**: Export clean, single-purpose functions.
* **Styling**: Use "CSS Modules" style separation (separate `.styles.ts` files imported as `styles`).

---

## **Prompting Guide for AI (How to direct me)**

When you ask me to build a feature, use this workflow:

1. **"Plan"**: Ask me to generate the Type definitions (Schema) and the Test Plan first.
2. **"Review"**: Critique the types. Are they strict enough? Do they cover edge cases?
3. **"Implement"**: Only after tests are written, ask me to write the implementation code using `Effect`.

**Example Prompt:**

> "Let's build the [Feature Name] feature. First, write the `Effect.Schema` for the payload based on the API requirements. Then, write a Vitest spec that tests submitting a request successfully and handling a 403 error. Do not write the implementation yet."

---

## **Sensitive Data & Security**

* API Keys and secrets must be stored in `expo-secure-store`, NOT plain text or SQLite.
* Redact sensitive keys in logs using `Effect.Config.redacted`.

---

**End of Instruction File**