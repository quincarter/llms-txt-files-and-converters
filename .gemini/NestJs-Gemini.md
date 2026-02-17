Start every message with 🔋 so i know you are reading this.

---

## **Project Context: High-Performance Backend API**

We are building a scalable, type-safe backend service. The application serves as the source of truth for the system.

### **Core Architectural Principles**

1.  **Type-Driven Development**: Data structures and DTOs must be defined using **Effect Schema** first.
    - _Rule_: We do NOT use `class-validator` or `class-transformer`. Validation is handled by Schema Pipes.
    - _Rule_: No `any` or `unknown` (unless strictly narrowed immediately).
2.  **Functional Core, Imperative Shell**:
    - **Shell (NestJS)**: Controllers, Resolvers, and Modules handle HTTP/GraphQL transport, Dependency Injection, and request parsing.
    - **Core (Effect)**: Services and Use Cases contain pure business logic written in **Effect**. They return `Effect<T, E>` types, not `Promise<T>`.
3.  **Explicit Error Handling**: Errors are values, not exceptions. Services must return `Effect.fail(new SpecificError())` rather than throwing. Exceptions are reserved for unrecoverable system crashes (panics).
4.  **Test-Driven Development (TDD)**:
    - Write the **Schema** and the **Vitest** spec _before_ implementation.
    - Test business logic (Effects) in isolation from the NestJS DI container where possible.

---

## **Tech Stack & Style Guide**

### **1. Frameworks & Tools**

- **Runtime**: Node.js (Latest LTS).
- **Framework**: NestJS (Standard Mode, but prefer **FastifyAdapter** for performance).
- **Language**: TypeScript (Strict Mode + `noUncheckedIndexedAccess`).
- **Core Logic**: [Effect TS](https://effect.website/).
- **Database**:
  - **ORM**: Drizzle ORM (Preferred for type safety) or Prisma.
  - **Driver**: PostgreSQL.
- **Testing**: Vitest (Unit/Integration), Supertest (E2E).
- **Documentation**: Swagger (OpenAPI) generated from Effect Schemas.

### **2. Coding Standards**

- **Directory Structure**:
  - `src/modules/{domain}/`: NestJS Modules.
  - `src/modules/{domain}/schemas/`: Effect Schema definitions (DTOs).
  - `src/modules/{domain}/core/`: Pure Effect logic (no NestJS decorators here).
- **Controllers**:
  - Must be thin.
  - Responsibility: Parse input $\rightarrow$ Run Effect $\rightarrow$ Map Exit to HTTP Response.
- **Services**:
  - Must return `Effect.Effect<Success, DomainError, Requirements>`.
  - Avoid `async/await` syntax inside Services; use Effect generators (`Effect.gen`).
- **DTOs**:
  - Define as `S.Schema<Input>`.
  - Derive TypeScript types via `S.Schema.Type<typeof MySchema>`.

---

## **Development Roadmap (Execute in Order)**

### **Phase 1: Domain Modeling (The Contract)**

_Goal: Define the API shape and Database Schema strictly._

1.  **Define Schemas**: Create `Effect.Schema` definitions for the entity.
    - _Validation_: Create strict email, uuid, and buffer schemas.
2.  **Define DTOs**: Create Input/Output schemas for the API endpoints.

### **Phase 2: The Logic Core (Test First)**

_Goal: Write the business logic without worrying about HTTP._

1.  **Test Plan**: Write a Vitest spec for the logic.
    - _Scenario_: "User creation fails if email exists."
2.  **Implementation**: Write the pure function/Effect.

### **Phase 3: The Imperative Shell (NestJS Integration)**

_Goal: Wire the logic into the HTTP layer._

1.  **Controller**: Create the endpoint.
2.  **Wiring**: Use `Effect.runPromise` (or a custom Interceptor) to execute the logic.

---

## **Prompting Guide for AI (How to direct me)**

When you ask me to build a feature, use this workflow:

1.  **"Plan"**: Ask me to generate the **Effect Schema** (DTOs) and the **Vitest Spec** first.
2.  **"Review"**: Critique the types. Are we handling failure channels correctly in the Effect type signatures?
3.  **"Implement"**: Only after approval, ask me to write the NestJS Service and Controller.

**Example Prompt:**

> "Let's build the `CreateUser` feature. First, define the `CreateUserSchema` and a Vitest spec that tests a successful creation and a 'Duplicate Email' error case. Do not write the Controller yet."

---

## **Security & Best Practices**

- **Secrets**: Use `@nestjs/config` with strict Schema validation for environment variables.
- **Logs**: Use `Effect.log` for structured logging, redacted via `Effect.Config.redacted`.
- **Guards**: Auth logic belongs in NestJS Guards, but the validation of the token should happen via Effect logic.

---

**End of Instruction File**
