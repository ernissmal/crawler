# Project Brief: Lead Scraper

## Executive Summary

**Lead Scraper** is a personal lead generation tool that discovers potential business leads from public sources (company registries, websites) and syncs them directly to an existing Notion database. The tool eliminates the need for expensive lead database subscriptions while providing a systematic, automated approach to lead discovery.

**Target User:** Solo entrepreneur/professional needing cost-effective lead generation
**Key Value:** Replace expensive tools (ZoomInfo, Apollo.io) with a self-hosted, Notion-integrated solution

---

## Problem Statement

### Current Pain Points
1. **Expensive subscriptions** - Professional lead databases cost $100-500+/month
2. **No systematic approach** - Lead discovery is ad-hoc, missing opportunities
3. **Manual research fatigue** - Hours spent hopping between websites, copying data to spreadsheets
4. **Scattered data** - Information exists but isn't organized or actionable

### Impact
- Time wasted on repetitive manual research
- Money spent on tools with features that go unused
- Missed opportunities due to inconsistent prospecting

### Why Now
Personal productivity tools are increasingly viable with modern scraping libraries, APIs, and Notion's robust database capabilities. A focused, personal tool can outperform bloated enterprise solutions for individual use cases.

---

## Proposed Solution

### Core Concept
A Dockerized scraping application that:
1. Accepts search criteria (industry, keywords, location, etc.)
2. Scrapes public data sources (company registries, websites)
3. Extracts lead information matching user's schema
4. Deduplicates against existing Notion entries
5. Pushes new leads directly to the user's Notion database

### Key Differentiators
- **Notion-native** - No separate database; Notion IS the source of truth
- **Deduplication built-in** - Never creates duplicate entries
- **Local-first** - Runs in Docker on your machine, no cloud dependencies
- **Cost: $0** - No subscriptions, no per-lead fees

---

## Target Users

### Primary User: Solo Professional
- **Profile:** Entrepreneur, freelancer, consultant, sales professional
- **Current workflow:** Manual research, spreadsheets, maybe a CRM
- **Pain points:** Time-consuming lead research, expensive tools
- **Goals:** Build a consistent pipeline of quality leads without breaking the bank

---

## Goals & Success Metrics

### Business Objectives
- Reduce lead research time by 80%
- Eliminate paid lead database subscriptions
- Build a sustainable, repeatable lead generation process

### User Success Metrics
- Find 10+ quality leads per search query
- Save 5+ hours per week vs manual research
- Zero duplicate entries in Notion database

### Key Performance Indicators (KPIs)
- **Leads discovered per search:** Target 10-50 per query
- **Time per search:** Under 2 minutes for results
- **Deduplication accuracy:** 100% (no false positives)
- **Notion sync success rate:** 99%+ reliability

---

## MVP Scope

### Core Features (Must Have)

1. **Criteria-based Search**
   - Input: industry, keywords, location, company size hints
   - Output: List of matching companies from public sources

2. **Company Data Extraction**
   - Company name
   - Website
   - Contact email (if publicly available)
   - Phone number (if publicly available)
   - Industry classification
   - Basic company description/notes

3. **Notion Integration**
   - Connect to existing Notion database
   - Map scraped fields to Notion properties
   - Deduplicate by company name/website before insert
   - Push new leads with configurable defaults (status, priority, etc.)

4. **Lead Schema Support**
   Properties to extract/populate:
   - Company name
   - Contact email
   - Industry
   - Lead source (auto-tagged with source URL)
   - Phone number
   - Potential value (default or user-set)
   - Priority (default or user-set)
   - Services (extracted if possible)
   - Status (default: "New")
   - Website
   - Notes (company description, key facts)

5. **Web UI for Search**
   - Simple form to input search criteria
   - Results preview before Notion sync
   - Sync button with confirmation

### Out of Scope for MVP
- LinkedIn scraping (requires authentication, legal complexity)
- CRM features beyond Notion (no Salesforce, HubSpot integrations)
- Scheduled/automated scraping (manual trigger only)
- Multi-user support
- Email enrichment services
- AI-powered lead scoring

### MVP Success Criteria
- Successfully discover leads from 2+ public sources
- Correctly deduplicate against existing Notion database
- Sync 20+ leads to Notion without errors
- Complete search-to-sync workflow in under 3 minutes

---

## Post-MVP Vision

### Phase 2 Features
- Scheduled/recurring searches
- More data sources (additional registries, directories)
- Lead enrichment (auto-fill missing fields from website scraping)
- Search history and saved queries
- Bulk import from CSV

### Long-term Vision
- Browser extension for "save this company" functionality
- AI-powered company categorization
- Similar company discovery (find companies like X)
- Integration with email outreach tools

### Expansion Opportunities
- Multiple Notion database support
- Team/shared usage mode
- API access for automation

---

## Technical Considerations

### Platform Requirements
- **Target Platform:** Docker container (local execution)
- **Host OS:** macOS (primary), Linux compatible
- **Browser:** Modern browsers for web UI
- **Network:** Internet required for scraping and Notion API

### Technology Preferences
- **Frontend:** Architect to decide (simple, lightweight)
- **Backend:** Architect to decide (Python recommended for scraping ecosystem)
- **Database:** None local - Notion as primary storage via API
- **Hosting:** Local Docker, no cloud infrastructure

### Architecture Considerations
- **Repository Structure:** Monorepo (single project)
- **Service Architecture:** Simple web app + scraper workers
- **Integration Requirements:** Notion API (official SDK)
- **Security:** Notion API token stored securely, no user auth needed (personal tool)

### Data Sources (MVP)
1. **Company Registries** - OpenCorporates, local business registries
2. **Website Scraping** - Direct company website parsing for contact info

---

## Constraints & Assumptions

### Constraints
- **Budget:** $0 (self-hosted, no paid APIs in MVP)
- **Timeline:** Personal project, no hard deadline
- **Resources:** Solo developer (AI-assisted)
- **Technical:** Must respect robots.txt, rate limits, legal scraping only

### Key Assumptions
- User has an existing Notion workspace with API access
- User has a Notion database with compatible schema (or will create one)
- Public registries provide sufficient lead data for discovery
- Basic company info is publicly available on company websites

---

## Risks & Open Questions

### Key Risks
- **Data quality:** Public sources may have incomplete/outdated information
- **Rate limiting:** Aggressive scraping may trigger blocks
- **Legal gray areas:** Some websites may have restrictive ToS
- **Notion API limits:** Free tier has rate limits

### Open Questions
- Which specific company registries are most valuable for your use case?
- What's the Notion database schema structure? (need to map fields)
- Are there specific industries or regions to prioritize?
- What's acceptable search latency? (seconds vs minutes)

### Areas Needing Further Research
- OpenCorporates API availability and limits
- Best practices for ethical web scraping
- Notion API pagination and bulk insert patterns

---

## Appendices

### A. Lead Schema (Notion Properties)

| Property | Type | Source | Notes |
|----------|------|--------|-------|
| Company name | Title | Scraped | Primary identifier |
| Contact email | Email | Scraped | May be empty |
| Industry | Select/Multi-select | Scraped/inferred | Categorization |
| Lead source | URL | Auto-generated | Where lead was found |
| Phone number | Phone | Scraped | May be empty |
| Potential value | Number/Select | User-set | Default value option |
| Priority | Select | User-set | High/Medium/Low default |
| Services | Multi-select/Text | Scraped | What company offers |
| Status | Select | Auto: "New" | Workflow status |
| Website | URL | Scraped | Company website |
| Notes | Text | Scraped | Description, key facts |

---

## Next Steps

1. Get user confirmation on project brief
2. Clarify Notion database schema structure
3. Proceed to PRD creation with PM agent
4. Define specific data sources with Architect

---

**PM Handoff:** This Project Brief provides the full context for Lead Scraper. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.
