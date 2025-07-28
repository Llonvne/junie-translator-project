# Junie Translator Web Application Architecture

## Overview

The Junie Translator Web Application will be structured into the following layers:

1. **Entity Layer**: Core data structures
2. **AI Layer**: AI service integration
3. **API Layer**: REST API endpoints
4. **Infra Layer**: Configuration and initialization
5. **WebUI Layer**: Vue3+Vite frontend

## Layer Details

### 1. Entity Layer

The Entity Layer will contain the core data structures used throughout the application:

- **SRT**: Represents SRT subtitle files and entries
  - `SubtitleEntry`: Already exists in current codebase
  - `SrtFile`: New class to represent a complete SRT file

- **AI Models**: Represents AI configuration and models
  - `AIProvider`: Configuration for an AI provider
  - `AIModel`: Configuration for a specific AI model

- **Prompts**: Represents translation prompts
  - `PromptTemplate`: Template for translation prompts
  - `PromptStyle`: Collection of prompt templates for a specific style

- **Config**: Application configuration
  - `AppConfig`: Application-wide configuration

### 2. AI Layer

The AI Layer will handle the interaction with AI services:

- **TranslatorService**: Interface for translation services (already exists)
  - `AIProviderTranslator`: Implementation using AI providers (already exists)
  - `MockTranslator`: Mock implementation for testing (already exists)

- **TranslationManager**: New class to manage translation requests
  - Handles batching and rate limiting
  - Provides both synchronous and asynchronous methods

### 3. API Layer

The API Layer will expose REST endpoints for the WebUI:

- **FastAPI Application**: Main API application
  - `app.py`: FastAPI application entry point

- **Routers**:
  - `config_router.py`: Endpoints for configuration
  - `translation_router.py`: Endpoints for translation
  - `srt_router.py`: Endpoints for SRT file operations

- **DTOs** (Data Transfer Objects):
  - Request and response models for API endpoints

### 4. Infra Layer

The Infra Layer will handle configuration, initialization, and dependencies:

- **Configuration**:
  - `config_loader.py`: Loads configuration from files
  - `environment.py`: Handles environment variables

- **Dependency Injection**:
  - `container.py`: Manages dependencies and their lifecycle

- **Initialization**:
  - `startup.py`: Initializes the application

### 5. WebUI Layer

The WebUI Layer will provide the user interface:

- **Vue3 Application**:
  - `index.html`: Entry point
  - `main.js`: Application initialization

- **Components**:
  - `App.vue`: Root component
  - `Header.vue`: Application header
  - `Footer.vue`: Application footer
  - `SrtUpload.vue`: SRT file upload
  - `TranslationForm.vue`: Translation form
  - `TranslationResult.vue`: Translation results
  - `ConfigSettings.vue`: Configuration settings

- **Services**:
  - `api.js`: API client for backend communication

- **Store**:
  - `index.js`: Vuex store
  - `modules/`: Store modules

## Interactions Between Layers

1. **WebUI → API**: The WebUI communicates with the backend through the API Layer using HTTP requests.

2. **API → AI**: The API Layer delegates translation requests to the AI Layer.

3. **AI → Entity**: The AI Layer uses entities from the Entity Layer for translation.

4. **Infra → All**: The Infra Layer provides configuration and dependencies to all other layers.

## File Structure

```
junie-translator-project/
├── src/
│   ├── junie_translator_project/
│   │   ├── entity/           # Entity Layer
│   │   │   ├── __init__.py
│   │   │   ├── srt.py
│   │   │   ├── ai_model.py
│   │   │   ├── prompt.py
│   │   │   └── config.py
│   │   ├── ai/               # AI Layer
│   │   │   ├── __init__.py
│   │   │   ├── translator.py
│   │   │   └── translation_manager.py
│   │   ├── api/              # API Layer
│   │   │   ├── __init__.py
│   │   │   ├── app.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config_router.py
│   │   │   │   ├── translation_router.py
│   │   │   │   └── srt_router.py
│   │   │   └── dto/
│   │   │       ├── __init__.py
│   │   │       ├── config_dto.py
│   │   │       ├── translation_dto.py
│   │   │       └── srt_dto.py
│   │   ├── infra/            # Infra Layer
│   │   │   ├── __init__.py
│   │   │   ├── config_loader.py
│   │   │   ├── environment.py
│   │   │   ├── container.py
│   │   │   └── startup.py
│   │   ├── __init__.py
│   │   ├── cli.py            # CLI entry point (existing)
│   │   └── main.py           # Main application logic (existing)
│   └── webui/                # WebUI Layer
│       ├── public/
│       │   └── index.html
│       ├── src/
│       │   ├── components/
│       │   │   ├── App.vue
│       │   │   ├── Header.vue
│       │   │   ├── Footer.vue
│       │   │   ├── SrtUpload.vue
│       │   │   ├── TranslationForm.vue
│       │   │   ├── TranslationResult.vue
│       │   │   └── ConfigSettings.vue
│       │   ├── services/
│       │   │   └── api.js
│       │   ├── store/
│       │   │   ├── index.js
│       │   │   └── modules/
│       │   │       ├── config.js
│       │   │       ├── translation.js
│       │   │       └── srt.js
│       │   ├── assets/
│       │   │   └── styles/
│       │   │       └── main.css
│       │   └── main.js
│       ├── package.json
│       └── vite.config.js
├── config.json               # Configuration (existing)
├── aiprovider.json           # AI provider configuration (existing)
├── prompts.json              # Translation prompts (existing)
└── pyproject.toml            # Python project configuration (existing)
```

## Implementation Strategy

1. **Refactor Existing Code**:
   - Move existing code to the appropriate layers
   - Adapt existing classes to fit the new architecture

2. **Implement New Components**:
   - Develop new components for each layer
   - Ensure proper interaction between layers

3. **Develop API Layer**:
   - Implement FastAPI application
   - Define endpoints and DTOs

4. **Develop WebUI**:
   - Set up Vue3+Vite project
   - Implement components and services

5. **Integration**:
   - Connect WebUI to API
   - Test end-to-end functionality