# Project Implementation Tasks

This file outlines the step-by-step tasks required to build the Agent-Based Travel Guide.

## Phase 1: Project Setup & Core Infrastructure

- [x] **Initialize Project Structure** <!-- id: 1 -->
    - [x] Create directory structure: `agents/`, `core/`, `models/`, `utils/`, `cache/`.
    - [x] Create `__init__.py` in all packages.
    - [x] Create `requirements.txt` (requests, googlemaps, python-dotenv, etc.).
    - [x] Create `.env.example`.
    - [x] **Setup uv**
        - [x] Initialize uv and install dependencies.

- [x] **Implement Configuration & Logging** <!-- id: 2 -->
    - [x] Create `config.py` to load env vars (GOOGLE_MAPS_API_KEY, LLM_API_KEY).
    - [x] Create `utils/logger.py` for consistent logging across threads.

- [x] **Implement LLM Client Abstraction** <!-- id: 3 -->
    - [x] Create `utils/llm_client.py`.
    - [x] Implement `LLMClient` class with a `generate_text` method.
    - [x] Support at least one provider (e.g., OpenAI, Anthropic, or a mock for testing).

- [x] **Implement Data Models** <!-- id: 4 -->
    - [x] Create `models/step.py` for `RouteStep`.
    - [x] Create `models/content.py` for `ContentCandidate` and `SelectedContent`.

## Phase 2: Google Maps Integration

- [x] **Implement Mapping Module** <!-- id: 5 -->
    - [x] Create `core/mapper.py`.
    - [x] Implement `RouteFinder` class.
    - [x] Implement `get_route(start, end)` with caching (check `cache/route_cache.json`).
    - [x] Implement `parse_route(route_json)` to return list of `RouteStep`.
    - [x] **Verification**: Create a test script to fetch a route and print steps.

## Phase 3: Agent Implementation

- [x] **Implement Brave Search Client** <!-- id: 6 -->
    - [x] Create `utils/brave_client.py`.
    - [x] Implement `BraveSearchClient` class with `search_web` and `search_videos` methods.
    - [x] Implement caching for search results.

- [x] **Refactor LLM Client for Claude CLI** <!-- id: 7 -->
    - [x] Update `utils/llm_client.py`.
    - [x] Implement `ClaudeCLIClient` that uses `subprocess` to call `claude`.
    - [x] Ensure it can accept prompt strings.

- [x] **Create Agent Prompts** <!-- id: 8 -->
    - [x] Create `agents/prompts/youtube_agent.md`.
    - [x] Create `agents/prompts/music_agent.md`.
    - [x] Create `agents/prompts/history_agent.md`.
    - [x] Create `agents/prompts/judge_agent.md`.

- [x] **Implement Base Agent** <!-- id: 9 -->
    - [x] Create `agents/base_agent.py`.
    - [x] Define `BaseAgent` class with `input_queue`, `output_queue`, `llm_client`, and `search_client`.
    - [x] Implement method to load prompt templates.

- [x] **Implement Content Agents** <!-- id: 10 -->
    - [x] Create `agents/content_agents.py`.
    - [x] Implement `YouTubeAgent`:
        - [x] Logic: Ask LLM for query -> Search Brave Videos -> Ask LLM to pick video.
    - [x] Implement `MusicAgent`:
        - [x] Logic: Ask LLM for query -> Search Brave Web -> Ask LLM to pick song.
    - [x] Implement `HistoryAgent`:
        - [x] Logic: Ask LLM for query -> Search Brave Web -> Ask LLM to summarize.

- [x] **Implement Judge Agent** <!-- id: 11 -->
    - [x] Create `agents/judge_agent.py`.
    - [x] Implement `JudgeAgent`.
    - [x] Logic: Wait for 3 inputs.
    - [x] Logic: Construct prompt with all options.
    - [x] Logic: Call Claude CLI to decide.


## Phase 4: Orchestration & Concurrency

- [x] **Implement Scheduler** <!-- id: 9 -->
    - [x] Create `core/scheduler.py`.
    - [x] Implement function to take `RouteStep` list and populate the main `TaskQueue`.

- [x] **Implement Orchestrator** <!-- id: 10 -->
    - [x] Create `core/orchestrator.py`.
    - [x] Implement logic to consume from `TaskQueue`.
    - [x] Implement logic to spawn/manage Agent threads/processes for each step.
    - [x] Ensure proper queue wiring (Agent Output -> Judge Input).

- [x] **Implement Collector** <!-- id: 11 -->
    - [x] Create `core/collector.py`.
    - [x] Implement `Collector` class to consume from `CollectorQueue`.
    - [x] Store results and generate final report.

## Phase 5: Integration & CLI

- [x] **Implement Main Entry Point** <!-- id: 12 -->
    - [x] Create `main.py`.
    - [x] Parse CLI arguments (start, destination).
    - [x] Initialize components (Mapper, Scheduler, Orchestrator, Collector).
    - [x] Start execution and wait for completion.
    - [x] Print final itinerary.

- [ ] **Final Verification** <!-- id: 13 -->
    - Run a full end-to-end test with a real route.
    - Verify `cache/` is populated.
    - Verify output contains a mix of video, music, and history.
