
# **Project Assignment: “Agent-Based Travel Guide”**

## **Overview**

In this project, you will build a multi-agent system that functions as an intelligent travel guide. The system receives a start address and a destination from the user, queries the Google Maps Directions API to obtain a driving route, and for each step along the route it generates accompanying content: a YouTube video, a relevant song, or a short historical story about the location.

For each location/turn on the route, three agents will compete to propose content, and a judge agent will select the best option. The final output is a complete list of all route steps together with the selected content for each one.

## **Project Objectives**

1. Design and implement a system composed of multiple cooperating agents.
2. Integrate with the Google Maps Directions API.
3. Use queues for communication between system components.
4. Implement agent orchestration, scheduling, and parallel execution.
5. Build LLM-powered agents (via CLI tools like Claude Code / llama-cli or via direct API calls).
6. Demonstrate proper Python package structure, including `__init__.py` files and caching.
7. Produce a route summary enriched with selected content for each turn.

---

# **System Architecture**

## **1. Input Module**

A user-facing component that receives:

* Start address
* Destination address

This module forwards the input to the mapping module.

## **2. Mapping Module (Google Maps Integration)**

This module connects to the Google Maps Directions API and:

* Sends a request with origin and destination
* Retrieves the full driving route
* Extracts all steps/turns from the response
* Assigns a unique ID for each step
* Produces a structured list of:

  * Ordered steps
  * Relevant addresses
  * Instruction text supplied by Google (turn right, continue straight, etc.)

These steps are then passed to the scheduler.

## **3. Scheduler**

The scheduler takes all route steps and enqueues them as individual tasks in a queue.

## **4. Orchestrator**

The orchestrator processes the task queue.
For each step, it launches four parallel threads:

1. **YouTube Agent** – finds a video relevant to the location
2. **Music Agent** – finds a song that matches the place or vibe
3. **History Agent** – retrieves a historical fact or a short story about the location
4. **Judge Agent** – waits for all three agents' outputs, then selects the best/most interesting one

### **Communication**

* Each agent writes its result into its own output queue
* The judge agent has an input queue where it collects results
* When all three responses arrive, the judge decides and places the chosen result in a “collector queue”

## **5. Collector**

A dedicated component that:

* Receives all judge outputs
* Stores the final results
* Prints or writes the final route overview containing:

  * All steps
  * Addresses
  * The selected content (song / video / story) for each step

---

# **Agent Behavior Requirements**

## **Agents must behave like true agents**

That means:

* They should not simply return the first item they find.
* Each agent must analyze several options and choose the best one based on reasoning.
* Each agent should use an LLM, either via:

  * CLI tools (Claude Code, llama-cli, etc.)

    **OR**
  * API calls using an API key.

### **Examples**

**YouTube Agent**

* Searches for multiple videos
* Analyzes titles, descriptions, or comments
* Selects the most suitable video

**Music Agent**

* Suggests a song that fits the location’s atmosphere or cultural context

**History Agent**

* Retrieves and summarizes relevant historical information
* Produces a coherent and meaningful short story

---

# **Judge Agent Requirements**

The judge agent must:

1. Wait until it receives all three agent outputs
2. Apply scoring “skills” (functions you will implement), such as:

   * What makes a video relevant?
   * What qualifies as a suitable song?
   * What makes a story interesting and connected to the location?
3. Choose the best overall option
4. Send the final selected content to the collector

---

# **Technical Requirements**

### **Python Package Structure**

* Code must be split across modules and packages
* Each package must include an `__init__.py`
* Demonstrate understanding of imports and clean architecture

### **Python Cache**

* Implement caching for repeated lookups
  (e.g., multiple steps referring to the same street or area)

### **Queues (Python Queue / multiprocessing.Queue)**

* Queues must be used for:

  * Task scheduling
  * Agent communication
  * Judge coordination

### **Threading / Multiprocessing**

* Three agents execute in parallel
* The judge waits for all three
* A separate collector thread runs in the background

### **Google Maps API**

* Mandatory use of the Directions API
* Must extract and process real route steps

### **LLM Usage**

Must be demonstrated using:

* CLI tools **or**
* API-key based LLM calls

---

# **Final Output Requirements**

Produce a complete route report listing:

For **each step**:

* Step ID
* Instruction (turn right, continue straight, etc.)
* Address (if applicable)
* The content chosen by the judge (video/song/story)
* *(Optional but recommended)* reasoning from the judge

---

# **Deliverables**

1. **Complete code** organized into a Python package structure
2. **Run instructions (README)**
3. **Example output from a real run**
4. **Short architecture explanation**
5. **Explanation of how caching and `__init__.py` were used**
