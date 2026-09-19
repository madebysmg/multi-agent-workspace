---
name: Company Deep Research Agent
description: Build an AI agent that performs deep web research on companies using LangGraph with a research-extraction-reflection iterative loop. Supports 7 web search providers (including DuckDuckGo, which needs no API key), with rate limiting, deduplication, and token management. Use this when the user wants to automatically search the web for company information, extract structured JSON data, implement quality evaluation loops, or build research automation.
allowed-tools: Write, Edit, Read, Bash
---

# Company Deep Research Agent

Build a web research agent that automatically searches the web, extracts structured information, and iteratively improves research quality.

## When to Use This Skill

Use this skill when building agents that need to:
- Automatically search the web for company information
- Extract structured data from web searches (JSON schema-driven)
- Implement quality evaluation loops (reflection phase)
- Handle private SME research (non-public companies)
- Add rate limiting and basic error handling

## Target Use Case: Private SME Research

This system is optimized for **private/unlisted companies** (10-1,000 employees) where structured data is limited. Research uses both direct sources (company websites, news) and indirect sources (public company filings, VC portfolios, government records).

## Architecture Overview

The agent uses a three-phase research loop:

```
1. RESEARCH → Generate queries → Execute web searches → Deduplicate → Collect notes
              ↓
2. EXTRACTION → Parse notes → Extract to JSON schema → Format output
              ↓
3. REFLECTION → Evaluate completeness → Identify gaps → Generate follow-ups
              ↓
         [Complete or Loop Back to Step 1]
```

**Built-in safeguards:**
- Rate limiting: 0.8 req/sec (Anthropic Tier 1 compliance)
- URL deduplication: Prevents duplicate API calls
- Token limits: Max 1,000 tokens per source
- Error handling: failed queries are logged and skipped; `google_adk`/`hybrid` fall back to Tavily

## Implementation Guide

### 1. Project Structure

Create the following directory structure:

```
src/agents/company_research/
├── __init__.py
├── configuration.py    # Config with 7 search providers
├── state.py           # ResearchState, DEFAULT_SCHEMA
├── prompts.py         # Centralized prompts
├── research.py        # Research phase (7 providers)
├── extraction.py      # JSON extraction
├── reflection.py      # Quality evaluation
└── graph.py           # LangGraph workflow

src/common/
├── llm.py             # LLM with rate limiting
└── utils.py           # Reusable functions (deduplication, formatting)
```

### 2. Implementation Steps

**Start with the existing implementation:**
The codebase already contains a complete implementation at `src/agents/company_research/`. Use this as the foundation:

1. **Configuration** (`configuration.py`): Supports 7 search provider values (`tavily`, `google_adk`, `hybrid`, `serpapi`, `bing`, `duckduckgo`, `brave`)

2. **Shared utilities** (`src/common/llm.py`, `src/common/utils.py`, `prompts.py`):
   - Rate limiting via `InMemoryRateLimiter` (0.8 req/sec)
   - URL deduplication via `deduplicate_sources()`
   - Token management via `format_sources(max_tokens_per_source=1000)`
   - Centralized prompts for query generation, extraction, reflection

3. **Three-phase workflow** (`research.py`, `extraction.py`, `reflection.py`):
   - Research: Query generation + multi-provider web search
   - Extraction: JSON schema-driven data extraction
   - Reflection: Quality evaluation + follow-up query generation

4. **Graph orchestration** (`graph.py`):
   - LangGraph state machine with conditional routing
   - Automatic iteration until completeness threshold (85%) or max iterations

### 3. Search Provider Selection

Choose based on budget and quality needs:

| Provider | Free Tier | Cost | Quality | Use Case |
|----------|-----------|------|---------|----------|
| **Tavily** | 1,000/month | $0.005/query | ⭐⭐⭐⭐⭐ | Production (best) |
| **google_adk** | See Google pricing | See Google pricing | ⭐⭐⭐⭐ | Google Programmable Search (Custom Search JSON API) |
| **Hybrid** | Mixed | Lower Tavily usage | ⭐⭐⭐⭐ | Half Tavily, half Google |
| **DuckDuckGo** | No API key | Free | ⭐⭐ | Testing |

`google_adk` is a historical name: it calls `GoogleSearchAPIWrapper` from `langchain-google-community` (needs `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`) and does not use Google ADK or Gemini. If the wrapper cannot be created, `google_adk` and `hybrid` fall back to Tavily.

Every provider has a branch in `research.py`. `serpapi`, `bing` and `brave` only print a fallback message when their package is missing; they do not re-run the search with another provider.

### 3.5 LLM Selection (Cost Optimization)

Choose the right LLM based on your budget and quality needs:

| LLM | Cost (Input/Output per 1M) | Monthly Cost* | Quality | Use Case |
|-----|---------------------------|---------------|---------|----------|
| **DeepSeek** | $0.028/$0.42 (cached) | **$20** | ⭐⭐⭐ | **Production (lowest cost)** ⭐⭐⭐ |
| **Qwen-Flash** | $0.05/$0.40 | **$19** | ⭐⭐⭐ | OpenAI-compatible, low cost |
| **Gemini 2.0 Flash** | $0.10/$0.40 | **$22** | ⭐⭐⭐⭐ | Google ecosystem |
| **Claude Sonnet 4.5** | $3/$15 | **$40** (cached) | ⭐⭐⭐⭐⭐ | **Best quality** (default) |

*Design estimate for 1,000 companies/month, LLM cost only

> **Note**: `src/common/llm.py` currently always creates `ChatAnthropic`, so only Claude model names work as-is. DeepSeek, Qwen or Gemini require changing `get_llm()` first (see `references/LLM_SELECTION.md`). Prices are 2025-10 figures.

**For latest pricing and new models**: See `references/LLM_SELECTION.md` which references the central pricing document (`docs/LLM_CLOUD_PRICING_2025.md`).

**Quick start:**
- **Development**: default Claude model + DuckDuckGo (no search API key)
- **Lower LLM cost**: DeepSeek/Qwen/Gemini after adapting `get_llm()` (estimates in LLM_SELECTION.md)
- **Quality-first**: Claude Sonnet 4.5 + Tavily or hybrid search

### 4. Usage Example

```python
import asyncio
from src.agents.company_research import (
    Configuration, DEFAULT_SCHEMA, build_research_graph
)

async def main():
    # Configure with free provider
    config = Configuration(
        max_search_queries=3,
        max_search_results=3,
        search_provider="duckduckgo"  # Free
    )

    graph = build_research_graph(config)

    # Run research
    result = await graph.ainvoke({
        "company_name": "Anthropic",
        "extraction_schema": DEFAULT_SCHEMA,
        "user_context": "Focus on AI safety research",
        "research_queries": [],
        "search_results": [],
        "research_notes": "",
        "extracted_data": {},
        "reflection_count": 0,
        "missing_fields": [],
        "follow_up_queries": [],
        "is_complete": False,
        "messages": []
    })

    print(result["extracted_data"])

asyncio.run(main())
```

### 5. Customization

**Custom schemas:**
Replace `DEFAULT_SCHEMA` with domain-specific schemas (e.g., tech startups, financial analysis).

**Cost optimization:**
Use `search_provider="hybrid"` to send the first half of each query batch to Tavily and the rest to Google Programmable Search. This roughly halves Tavily calls; Google search has its own pricing.

**Rate limiting:**
For Anthropic Tier 2, adjust in `llm.py`:
```python
_rate_limiter = InMemoryRateLimiter(
    requests_per_second=16.6,  # ~1,000 req/min
)
```

## Production Best Practices

1. **Start simple**: Use DuckDuckGo (free) for development
2. **Test quality**: Try Tavily with sample companies
3. **Optimize cost**: Switch to Hybrid for production
4. **Monitor performance**: Target 85%+ schema completeness
5. **Set API keys**: Export `TAVILY_API_KEY`, `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` (for `google_adk`/`hybrid`), etc.

## Estimated Metrics

These are design-stage estimates from 2025-10, not measurements. The repository contains no benchmark.

- **Processing time**: 45-90 seconds per company
- **API calls**: 3-9 per company (with deduplication)
- **Search cost (Tavily)**: ~$0.015-0.045 per company
- **LLM cost (Claude)**: ~$0.02-0.04 per company (cached)
- **LLM cost (DeepSeek, after adapting `get_llm()`)**: ~$0.002-0.003 per company (cached)
- **Total cost (Claude + Tavily)**: ~$0.035-0.085 per company
- **Target schema completeness**: 85%+

## Reference Materials

For detailed implementation guidance, see:
- `references/IMPLEMENTATION_GUIDE.md` - Complete code examples for all 10 files
- `references/SEARCH_PROVIDERS.md` - Detailed guide for all 7 search providers
- `references/LLM_SELECTION.md` - LLM cost optimization guide (references central pricing doc)
- `references/TROUBLESHOOTING.md` - Common issues and solutions
- `references/PRODUCTION_CHECKLIST.md` - Pre-deployment validation

**Central Documents** (always up-to-date):
- `docs/LLM_CLOUD_PRICING_2025.md` - Comprehensive LLM pricing comparison

## Dependencies

```bash
# Core
pip install langgraph>=0.2.0 langchain>=0.3.0 langchain-anthropic>=0.2.0
pip install langchain-community>=0.3.0 pydantic>=2.0.0

# Search providers (install as needed)
pip install tavily-python>=0.3.0          # Tavily
pip install langchain-google-community    # google_adk / hybrid (Google Programmable Search)
pip install -U ddgs                       # DuckDuckGo (no API key)
```

## Quick Start Workflow

1. **Use existing code**: Check `src/agents/company_research/` - complete implementation exists
2. **Test locally**: Run `PYTHONPATH=. python examples/free_research_duckduckgo.py` (DuckDuckGo search)
3. **Customize**: Adjust schema, provider, or rate limits
4. **Deploy**: Use production checklist in references

This skill builds on the existing code in `src/agents/company_research/` (a prototype without automated tests). Focus on configuration and customization rather than building from scratch.
