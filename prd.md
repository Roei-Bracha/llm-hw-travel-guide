# Product Requirements Document (PRD): Agent-Based Travel Guide

## 1. Introduction
The **Agent-Based Travel Guide** is a multi-agent system designed to enrich a user's travel experience. By integrating with Google Maps, the system generates a driving route and, for each step, provides curated multimedia content (YouTube videos, music, or historical stories) selected by intelligent agents.

## 2. Objectives
- **Intelligent Content Curation**: Leverage LLMs to find and select the most relevant content for specific locations.
- **Seamless Integration**: Connect with Google Maps Directions API to provide real-world routing.
- **Multi-Agent Collaboration**: Demonstrate orchestration, parallel execution, and inter-agent communication using queues.
- **Robust Architecture**: Implement a clean Python package structure with caching and proper concurrency.

## 3. User Stories
- **As a traveler**, I want to input my start and destination addresses so that I can get a route.
- **As a traveler**, I want to see a video, song, or story for each turn on my route so that I am entertained and informed.
- **As a developer**, I want the system to cache repeated lookups so that performance is optimized and API costs are minimized.

## 4. Functional Requirements

### 4.1 Input Module
- Accept **Start Address** and **Destination Address** from the user.
- Forward inputs to the Mapping Module.

### 4.2 Mapping Module
- **API Integration**: Query Google Maps Directions API.
- **Route Processing**:
  - Extract steps/turns.
  - Assign unique IDs to steps.
  - Parse instructions (e.g., "Turn right") and addresses.
- **Output**: Structured list of route steps.

### 4.3 Scheduler
- Enqueue each route step as a task for processing.

### 4.4 Orchestrator & Agents
- **Concurrency**: Launch 4 parallel threads per step.
- **Agents**:
  1.  **YouTube Agent**: Search for videos using Brave Search (Video) and select relevant ones.
  2.  **Music Agent**: Search for songs using Brave Search and suggest matches.
  3.  **History Agent**: Search for historical facts using Brave Search.
  4.  **Judge Agent**:
      - Wait for all 3 agents.
      - Evaluate outputs based on relevance and quality.
      - Select the best option.
- **Communication**: Use input/output queues for data flow.
- **LLM Integration**: **MUST** use `claude` CLI tool. Agents will be defined via prompt files (Markdown/YAML) passed to the CLI.
- **Web Search**: **MUST** use Brave Search API (Free Tier) for all external information retrieval.

### 4.5 Collector
- Aggregate final results from the Judge Agent.
- Generate a final report containing:
  - Step details (ID, instruction, address).
  - Selected content (Video/Song/Story).
  - Judge's reasoning (optional).

## 5. Non-Functional Requirements
- **Zero Cost**: Use free tiers for all services (OpenRouteService, Brave Search).
- **Performance**: Agents must run in parallel to minimize latency.
- **Caching**: Implement caching for repeated location lookups and route queries.
- **Code Quality**:
  - Modular Python package structure.
  - Use of `__init__.py`.
  - Clean architecture.
- **Reliability**: Handle API failures gracefully (implied).

## 6. System Architecture
- **Input** -> **Mapping** -> **Scheduler** -> **Orchestrator** (Agents + Judge) -> **Collector** -> **Output**
- **Queues**: Used for decoupling components (Scheduler -> Orchestrator, Agents -> Judge, Judge -> Collector).

## 7. Deliverables
- Python source code (package structure).
- `README.md` with run instructions.
- Example output log.
- Architecture documentation.
- Explanation of caching and package structure.
