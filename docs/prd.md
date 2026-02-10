# Lead Scraper Product Requirements Document (PRD)

---

## Goals

- **Eliminate expensive lead database subscriptions** - Replace tools like ZoomInfo and Apollo.io ($100-500+/month) with a $0 self-hosted solution
- **Reduce lead research time by 80%** - Automate the repetitive discovery and data entry workflow
- **Achieve systematic, repeatable lead generation** - Replace ad-hoc research with a structured process
- **Maintain zero duplicate entries** - Intelligent deduplication against existing Notion database
- **Enable fast search-to-sync workflow** - Complete discovery to Notion sync in under 3 minutes

## Background Context

Solo professionals and entrepreneurs face a common dilemma: professional lead databases offer powerful discovery capabilities but at enterprise price points that don't make sense for individual users. The current alternatives—manual research across company registries, websites, and directories—are time-consuming and inconsistent, leading to missed opportunities and scattered data across spreadsheets.

Lead Scraper addresses this gap by providing a Dockerized, local-first application that scrapes public data sources (company registries, websites), extracts lead information to a configurable schema, and syncs directly to the user's existing Notion database. By leveraging Notion as the source of truth and building deduplication into the core workflow, the tool delivers enterprise-grade lead discovery capabilities at zero cost.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-02-10 | 0.1 | Initial PRD draft | John (PM) |

---

## Requirements

### Functional Requirements

- **FR1:** The system shall accept search criteria including industry, keywords, location, and company size hints via a web interface
- **FR2:** The system shall scrape company data from at least 2 public sources (company registries like OpenCorporates, and direct website parsing)
- **FR3:** The system shall extract and populate lead properties: Company name, Website, Contact email, Phone number, Industry, Services, and Notes/description
- **FR4:** The system shall connect to an existing Notion database using the official Notion API
- **FR5:** The system shall map scraped fields to corresponding Notion database properties based on user configuration
- **FR6:** The system shall deduplicate leads by company name and/or website URL before inserting into Notion
- **FR7:** The system shall display a preview of discovered leads before syncing to Notion
- **FR8:** The system shall auto-tag each lead with the source URL where it was discovered
- **FR9:** The system shall set configurable default values for Status (default: "New"), Priority, and Potential Value on new leads
- **FR10:** The system shall provide a sync confirmation before pushing leads to Notion

### Non-Functional Requirements

- **NFR1:** The system shall complete a search-to-results workflow in under 2 minutes
- **NFR2:** The system shall achieve 100% deduplication accuracy (no false positives creating duplicates)
- **NFR3:** The system shall maintain 99%+ Notion sync success rate
- **NFR4:** The system shall run as a Docker container on macOS (primary) and Linux
- **NFR5:** The system shall operate with $0 infrastructure cost (no paid APIs, local execution only)
- **NFR6:** The system shall respect robots.txt and implement rate limiting for ethical scraping
- **NFR7:** The system shall securely store the Notion API token (environment variables, no hardcoding)
- **NFR8:** The system shall function for a single user without authentication requirements

---

## User Interface Design Goals

### Overall UX Vision

A minimalist, utility-first interface that prioritizes speed and clarity over aesthetics. The UI should feel like a professional developer tool—clean, functional, with immediate feedback. Think "CLI-friendly with a browser interface" rather than polished consumer app.

### Key Interaction Paradigms

- **Form-driven search:** Single form with all search parameters visible upfront
- **Table-based results:** Scannable list with inline editing/selection before sync
- **Progressive disclosure:** Advanced options collapsed by default
- **Immediate feedback:** Loading states, success/error toasts, sync progress

### Core Screens and Views

1. **Search Screen** - Primary interface with search criteria form, recent searches history
2. **Results Preview** - Table view of discovered leads with checkbox selection, inline data preview
3. **Sync Confirmation** - Modal or panel showing selected leads, Notion mapping preview, sync button
4. **Settings/Configuration** - Notion connection setup, field mapping, default values configuration

### Accessibility

None (personal tool, single user)

### Branding

No specific branding requirements. Use system defaults or a minimal CSS framework for clean styling without design overhead.

### Target Devices and Platforms

Web Responsive - Browser-based, optimized for desktop use but responsive for tablet/mobile access.

---

## Technical Assumptions

### Repository Structure: Monorepo

Single repository containing all application code (backend, frontend templates, Docker configuration). Simplifies deployment and version management for a personal tool.

### Service Architecture

Simple web application with integrated scraper workers. No microservices—a monolithic Python application that handles:
- Web UI serving (Jinja2 templates)
- API endpoints for search/sync operations
- Background scraping tasks
- Notion API integration

### Testing Requirements

Unit tests for core business logic (scraping, deduplication, Notion sync). Manual testing for UI workflows. No complex E2E testing infrastructure needed for MVP—focus on reliable core functionality.

### Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| Runtime | Python | 3.13.x | Latest stable, LTS until 2029 |
| Web Framework | FastAPI | 0.128.6 | Modern async, auto-docs, type hints |
| HTML Parsing | BeautifulSoup4 | 4.14.3 | Industry standard, robust parsing |
| HTTP Client | httpx | 0.28.1 | Async support, modern API |
| Notion SDK | notion-client | 2.7.0 | Official SDK, full API coverage |
| ASGI Server | uvicorn | 0.40.0 | High-performance, FastAPI standard |
| Frontend | Jinja2 + HTMX | Latest | Server-rendered, minimal JS complexity |
| Styling | Pico CSS / Simple.css | Latest | Classless CSS, zero config |
| Container | Docker | Latest | Local deployment, reproducible |

### Additional Technical Assumptions and Requests

- No local database required—Notion serves as the sole data store
- Environment variables for all configuration (Notion token, rate limits)
- Dockerfile with multi-stage build for minimal image size
- Docker Compose for easy local development
- Async/await patterns for non-blocking scraping operations
- Structured logging for debugging scrape failures

---

## Epic List

**Epic 1: Foundation & First Scraper**
Establish project infrastructure with Docker/FastAPI and deliver a working website scraper that displays discovered leads in a basic results table.

**Epic 2: Notion Integration & Deduplication**
Connect to Notion API, implement field mapping and deduplication logic, and enable syncing discovered leads to the user's existing Notion database.

**Epic 3: Search Refinement & Second Data Source**
Add the second data source (company registry), implement search criteria filtering, and polish the UI with preview/confirmation workflow.

---

## Epic 1: Foundation & First Scraper

**Goal:** Build the foundational project infrastructure (FastAPI, Docker, templates) and implement a working website scraper that extracts company information from a given URL. By the end of this epic, a user can enter a website URL and see extracted lead data displayed in a results table.

### Story 1.1: Project Foundation with Health Check

**As a** developer,
**I want** the project scaffolded with FastAPI, Docker, and a health endpoint,
**so that** I can run the application locally with `docker-compose up` and verify it works.

**Acceptance Criteria:**
1. Project structure created with `app/`, `templates/`, `static/`, `tests/` directories
2. FastAPI application initializes with uvicorn
3. `/health` endpoint returns `{"status": "ok"}`
4. `Dockerfile` uses multi-stage build with Python 3.13
5. `docker-compose.yml` runs the app on port 8000
6. Running `docker-compose up` starts the app successfully
7. `.env.example` file documents required environment variables

### Story 1.2: Search Input UI

**As a** user,
**I want** a web page with a form to enter a website URL,
**so that** I can specify which company website to scrape for leads.

**Acceptance Criteria:**
1. Home page (`/`) renders a Jinja2 template with search form
2. Form includes URL input field with placeholder text
3. Form submits via POST to `/scrape` endpoint
4. Basic styling applied (Pico CSS or Simple.css)
5. Form validates URL format before submission (client-side)
6. Loading indicator appears on form submit

### Story 1.3: Website Scraper Core

**As a** user,
**I want** the system to scrape a company website and extract contact information,
**so that** I can discover lead data from public web pages.

**Acceptance Criteria:**
1. Scraper fetches URL content using httpx with timeout handling
2. BeautifulSoup parses HTML and extracts: company name, email addresses, phone numbers
3. Scraper attempts to extract company description from meta tags or about sections
4. Respects robots.txt before scraping (checks disallow rules)
5. Rate limiting implemented (configurable delay between requests)
6. Graceful error handling for unreachable URLs, timeouts, invalid HTML
7. Extracted data returned as structured Lead object
8. Source URL automatically captured as lead source field

### Story 1.4: Results Display Table

**As a** user,
**I want** to see the scraped lead data displayed in a table,
**so that** I can review what information was extracted.

**Acceptance Criteria:**
1. Results page displays extracted data in HTML table format
2. Table columns: Company Name, Website, Email, Phone, Description, Source
3. Empty fields display "Not found" placeholder
4. Results page includes "Scrape Another" button to return to search
5. Basic success/error messaging displayed (toast or alert)
6. Results stored in session for current browsing session
7. Multiple scrape results accumulate in table (not replaced)

---

## Epic 2: Notion Integration & Deduplication

**Goal:** Connect the application to Notion via the official API, enable field mapping configuration, implement deduplication logic to prevent duplicate entries, and allow users to sync discovered leads to their Notion database with one click.

### Story 2.1: Notion Connection & Database Discovery

**As a** user,
**I want** to connect my Notion account and select my leads database,
**so that** the app knows where to sync discovered leads.

**Acceptance Criteria:**
1. Settings page (`/settings`) accessible from navigation
2. Notion API token input field with secure storage (environment variable)
3. "Test Connection" button verifies API token validity
4. On successful connection, display list of accessible databases
5. User can select target database from dropdown
6. Selected database ID stored in configuration
7. Connection status indicator shown on main UI (connected/disconnected)

### Story 2.2: Field Mapping Configuration

**As a** user,
**I want** to map scraped lead fields to my Notion database properties,
**so that** data syncs correctly to my existing schema.

**Acceptance Criteria:**
1. Settings page displays Notion database properties after database selection
2. For each scraped field (Company name, Email, Phone, Website, Description, Source), show dropdown of available Notion properties
3. Property type validation (email field maps to email/text property, URL to URL property, etc.)
4. "Title" property automatically mapped to Company name
5. Mapping configuration persisted between sessions
6. Default value configuration for Status (default: "New"), Priority, Potential Value
7. Visual indicator for unmapped/invalid mappings

### Story 2.3: Deduplication Logic

**As a** user,
**I want** the system to identify duplicate leads before syncing,
**so that** I never create duplicate entries in my Notion database.

**Acceptance Criteria:**
1. Before sync, query Notion database for existing entries
2. Match duplicates by company name (case-insensitive, fuzzy match optional)
3. Match duplicates by website URL (domain normalization: ignore www, trailing slashes)
4. Results table marks duplicate leads with visual indicator (icon/badge)
5. Duplicate leads excluded from sync by default (can be toggled)
6. Duplicate detection runs automatically when results are displayed
7. Show count of duplicates found vs. new leads

### Story 2.4: Sync Leads to Notion

**As a** user,
**I want** to sync selected leads to my Notion database with one click,
**so that** discovered leads are saved to my existing workflow.

**Acceptance Criteria:**
1. Checkbox selection on results table to choose leads for sync
2. "Select All New" button selects all non-duplicate leads
3. "Sync to Notion" button triggers sync for selected leads
4. Confirmation modal shows count and field mapping preview
5. Progress indicator during sync (X of Y synced)
6. Success/failure status displayed per lead after sync
7. Synced leads marked in table (checkmark or status change)
8. Error handling with retry option for failed syncs
9. Post-sync summary: X synced, Y failed, Z skipped (duplicates)

---

## Epic 3: Search Refinement & Second Data Source

**Goal:** Expand discovery capabilities by adding a company registry data source (OpenCorporates or similar), implementing full search criteria filtering (industry, keywords, location), and polishing the search-to-sync workflow with preview enhancements and recent search history.

### Story 3.1: Company Registry Integration

**As a** user,
**I want** to search company registries for businesses by name or keywords,
**so that** I can discover leads beyond direct website scraping.

**Acceptance Criteria:**
1. Integration with OpenCorporates API (or alternative free registry)
2. Search by company name, keywords, or jurisdiction
3. Extract company data: name, registration number, address, status, incorporation date
4. Map registry data to Lead schema (company name, notes, source URL)
5. Handle API rate limiting with backoff and retry
6. Graceful degradation if registry unavailable (show message, continue with website scraping)
7. Source URL tagged as registry entry link
8. Results combined with website scraper results in unified table

### Story 3.2: Advanced Search Criteria Form

**As a** user,
**I want** to filter searches by industry, location, and keywords,
**so that** I can discover targeted leads matching my criteria.

**Acceptance Criteria:**
1. Search form expanded with: Industry (dropdown/text), Location (country/region), Keywords, Company size hints
2. All criteria optional (can search with just one field)
3. Industry dropdown populated with common categories
4. Location supports country-level filtering at minimum
5. Keywords applied to company name and description matching
6. Form state preserved on results page for refinement
7. "Clear Filters" button resets form
8. Search submitted to both data sources (website + registry) in parallel

### Story 3.3: Enhanced Results Preview

**As a** user,
**I want** to preview full lead details before syncing,
**so that** I can verify data quality and make informed selections.

**Acceptance Criteria:**
1. Results table sortable by column (name, source, sync status)
2. Click row to expand inline detail panel or modal
3. Detail view shows all extracted fields with source attribution
4. Data source indicator per lead (Website vs Registry)
5. Edit capability for individual fields before sync
6. Bulk selection tools: Select All, Select None, Invert Selection
7. Lead count summary: Total, New, Duplicates, Selected

### Story 3.4: Recent Searches & UI Polish

**As a** user,
**I want** to see my recent searches and quickly re-run them,
**so that** I can efficiently work through lead discovery sessions.

**Acceptance Criteria:**
1. Recent searches list on home page (last 10 searches)
2. Each entry shows: search criteria summary, date, result count
3. Click recent search to pre-fill form and optionally re-run
4. Delete individual searches from history
5. Navigation header with links: Search, Results, Settings
6. Responsive layout works on tablet (min 768px width)
7. Loading states and skeleton UI during searches
8. Final confirmation modal before Notion sync with summary stats

---

## Checklist Results Report

### Executive Summary

| Metric | Assessment |
|--------|------------|
| **Overall PRD Completeness** | 92% |
| **MVP Scope Appropriateness** | Just Right |
| **Readiness for Architecture Phase** | **Ready** |

**Most Critical Observation:** PRD is comprehensive with well-structured epics and AI-agent-sized stories. Minor gaps are acceptable for a personal tool with no multi-user or enterprise requirements.

### Category Statuses

| Category | Status | Critical Issues |
|----------|--------|-----------------|
| 1. Problem Definition & Context | PASS | None - clear problem statement, quantified impact |
| 2. MVP Scope Definition | PARTIAL | MVP success criteria could be more explicit in PRD body |
| 3. User Experience Requirements | PASS | Accessibility intentionally scoped out (acceptable for personal tool) |
| 4. Functional Requirements | PASS | FR1-10 are testable and unambiguous |
| 5. Non-Functional Requirements | PARTIAL | NFR5 ($0 cost) clear; monitoring/logging strategy could be stronger |
| 6. Epic & Story Structure | PASS | Excellent sequencing, vertical slices, AI-agent sized |
| 7. Technical Guidance | PASS | Complete technology stack with specific versions |
| 8. Cross-Functional Requirements | PARTIAL | Integration testing approach lightweight (acceptable for MVP) |
| 9. Clarity & Communication | PASS | Clear language, consistent terminology |

### Top Issues by Priority

**HIGH:**
- Validate OpenCorporates API access before Epic 3 development (free tier limits, authentication requirements)
- Specify deduplication algorithm test cases for edge cases (similar names, URL variations)

**MEDIUM:**
- Add health dashboard endpoint showing scrape status and Notion connection state
- Document retry/backoff strategy for Notion API rate limits

**LOW:**
- Consider JSON structured logging with correlation IDs for debugging
- Add metrics for scrape success rates in NFRs

### Recommendations

1. **Before Architecture:** Confirm OpenCorporates API availability and rate limits for free tier
2. **Story 2.3 Enhancement:** Add acceptance criteria for deduplication edge cases (e.g., "ABC Inc" vs "ABC Incorporated")
3. **NFR Addition:** Consider adding NFR for structured logging format
4. **Epic 1 Consideration:** Story 1.1 should verify Docker multi-stage build produces image under 200MB

### Final Decision

**READY FOR ARCHITECT** - The PRD is comprehensive, properly structured, and ready for architectural design. The 3-epic structure with 12 stories follows agile best practices with logical sequencing. Each story is appropriately sized for AI agent execution. Minor gaps identified are acceptable for a personal tool MVP.

---

## Next Steps

### UX Expert Prompt

Review the Lead Scraper PRD (`docs/prd.md`) focusing on the User Interface Design Goals section. The application is a utility-first developer tool with 4 core screens: Search, Results Preview, Sync Confirmation, and Settings. Create wireframes or screen flows prioritizing speed and clarity over aesthetics. Use Pico CSS or Simple.css for classless styling. Key interaction paradigms: form-driven search, table-based results with inline editing, progressive disclosure for advanced options. No accessibility requirements—this is a single-user personal tool.

### Architect Prompt

Create the technical architecture for Lead Scraper based on `docs/prd.md`. Key constraints: Python 3.13.x + FastAPI 0.128.6 monolith, Docker deployment, Notion as sole data store (no local database), $0 infrastructure cost. Focus areas: async scraping patterns with httpx, deduplication algorithm design (company name fuzzy matching, URL normalization), Notion API integration patterns with rate limit handling, and OpenCorporates fallback strategy. Deliver architecture document with component diagrams, API specifications, and data flow diagrams.

