# Search Providers Guide

Guide for the 7 `search_provider` values implemented in `src/agents/company_research/research.py`.

## Provider Comparison

| Provider | Free Tier | Pricing | Quality | Setup |
|----------|-----------|---------|---------|-------|
| Tavily | 1,000/month | $0.005/query | ⭐⭐⭐⭐⭐ | API key |
| google_adk (Google Programmable Search) | See Google pricing | See Google pricing | ⭐⭐⭐⭐ | API key + Search Engine ID |
| Hybrid | Mixed | Fewer Tavily calls | ⭐⭐⭐⭐ | Tavily + Google keys |
| DuckDuckGo | No API key | Free | ⭐⭐ | `pip install -U ddgs` |
| Bing | 1,000/month | $7/1k | ⭐⭐⭐ | Subscription key |
| Brave | 2,000/month | Paid | ⭐⭐⭐ | API key |
| SerpAPI | Trial | $50/5k | ⭐⭐⭐⭐ | API key |

Prices and free tiers are 2025-10 figures and may have changed.

## 1. Tavily (Best Quality)

**Use for:** Production deployments requiring highest quality

**Setup:**
```bash
pip install tavily-python>=0.3.0
export TAVILY_API_KEY="your_key"
```

**Configuration:**
```python
config = Configuration(search_provider="tavily")
```

**Features:**
- Advanced search depth
- Raw content included
- Best accuracy
- Reliable extraction

**Cost:** $5 per 1,000 searches

## 2. google_adk (Google Programmable Search)

**Note:** the provider value is called `google_adk` for historical reasons. The code calls
`GoogleSearchAPIWrapper` from `langchain-google-community`, i.e. the Google Custom Search JSON API.
It does not use Google ADK, Gemini or Gemini's `google_search` tool; quotas and pricing are those of the Custom Search JSON API.

**Setup:**
```bash
pip install langchain-google-community
export GOOGLE_API_KEY="your_key"
export GOOGLE_CSE_ID="your_programmable_search_engine_id"
```

**Configuration:**
```python
config = Configuration(search_provider="google_adk")
```

**Behavior:**
- The synchronous wrapper runs in a thread (`asyncio.to_thread`)
- If the package or keys are missing, the agent falls back to Tavily

**Limitations:**
- Requires a Google Cloud API key and a Programmable Search Engine
- Returns one text snippet blob per query (less structured than Tavily)
- The `use_gemini_for_google_search` flag is currently unused

## 3. Hybrid (Tavily + Google)

**Use for:** Sending about half of the queries to Tavily and the rest to Google Programmable Search

**Setup:**
```bash
pip install tavily-python langchain-google-community
export TAVILY_API_KEY="your_key"
export GOOGLE_API_KEY="your_key"
export GOOGLE_CSE_ID="your_programmable_search_engine_id"
```

**Configuration:**
```python
config = Configuration(search_provider="hybrid")
```

**Strategy:**
- First half of queries (rounded down): Tavily
- Second half: Google Programmable Search (Tavily if the Google wrapper is unavailable)
- Tavily cost: roughly half of all-Tavily; Google search is billed separately

## 4. DuckDuckGo (Free Testing)

**Use for:** Development and testing

**Setup:**
```bash
pip install -U ddgs   # current langchain-community DuckDuckGo wrapper imports `ddgs`
# No API key needed
```

**Configuration:**
```python
config = Configuration(search_provider="duckduckgo")
```

**Features:**
- Completely free
- No API key needed
- Privacy-focused
- Rate limited

**Limitations:**
- Lower quality results
- Less structured data
- Rate limits

## 5. Bing

**Use for:** Microsoft ecosystem integration

**Setup:**
```bash
export BING_SUBSCRIPTION_KEY="your_key"
```

**Configuration:**
```python
config = Configuration(search_provider="bing")
```

**Pricing:**
- Free: 1,000 queries/month
- Paid: $7 per 1,000 queries

## 6. Brave

**Use for:** Privacy-focused production

**Setup:**
```bash
export BRAVE_API_KEY="your_key"
```

**Configuration:**
```python
config = Configuration(search_provider="brave")
```

**Features:**
- Privacy-focused
- 2,000 free queries/month
- Good quality

## 7. SerpAPI

**Use for:** Google results scraping

**Setup:**
```bash
pip install google-search-results
export SERPAPI_KEY="your_key"
```

**Configuration:**
```python
config = Configuration(search_provider="serpapi")
```

**Pricing:**
- Trial available
- $50 per 5,000 searches

## Provider Selection Decision Tree

```
Need production quality?
├─ Yes
│  ├─ Budget available?
│  │  ├─ Yes → Tavily
│  │  └─ No → Hybrid (fewer Tavily calls)
│  └─ Budget constrained?
│     └─ google_adk (Google Programmable Search, check Google pricing)
└─ No (testing/development)
   └─ DuckDuckGo (no API key)
```

## Error Handling

Search errors are caught per query:

```python
try:
    results = await search_tool.ainvoke(query)
    all_results.extend(results)
except Exception as e:
    print(f"Search error for query '{query}': {e}")
    continue  # Skip to next query
```

What happens on failure:
1. A single query fails: the error is printed and the next query runs
2. `google_adk`/`hybrid` without the Google package or keys: Tavily is used instead
3. `serpapi`/`bing`/`brave` without their package: a DuckDuckGo fallback message is printed, but no fallback search runs
4. `duckduckgo` without `ddgs`: research notes contain an error message and no results

## API Rate Limits

| Provider | Rate Limit | Handling |
|----------|------------|----------|
| Tavily | 100 req/min | Built-in |
| google_adk | Depends on Google quota | Provider-side |
| DuckDuckGo | ~30 req/min | Client-side |
| Others | Varies | Provider-specific |

The agent's rate limiter (0.8 req/sec, `src/common/llm.py`) applies to LLM calls only. Search calls are not rate-limited by the agent.

## Best Practices

1. **Start with free**: Use DuckDuckGo for initial testing
2. **Validate quality**: Test Tavily with 10-20 companies
3. **Optimize cost**: Switch to Hybrid for production
4. **Monitor usage**: Track API costs and adjust
5. **Know the fallbacks**: only `google_adk` and `hybrid` actually fall back (to Tavily)

## Troubleshooting

**Provider not working:**
1. Check API key is set correctly
2. Verify package is installed
3. Check API quota/limits
4. Try fallback provider

**Poor results:**
1. Try higher quality provider (Tavily)
2. Increase `max_search_queries`
3. Improve schema descriptions
4. Use indirect sources for private SMEs
