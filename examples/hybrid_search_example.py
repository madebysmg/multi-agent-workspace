"""
Example using the hybrid search strategy (Tavily + Google search).

This example demonstrates:
- First half of the queries use Tavily
- Second half of the queries use Google Programmable Search
  (the same wrapper as the "google_adk" provider)
- If the Google wrapper cannot be created, all queries go to Tavily

Requirements:
- TAVILY_API_KEY and ANTHROPIC_API_KEY in .env
- Optional: pip install langchain-google-community, plus GOOGLE_API_KEY and
  GOOGLE_CSE_ID in .env, for the Google half

Run from the repository root:
    PYTHONPATH=. python examples/hybrid_search_example.py
"""
import os
import json
import asyncio
from dotenv import load_dotenv

from src.agents.company_research import Configuration, DEFAULT_SCHEMA, build_research_graph

# Load environment variables
load_dotenv()


async def main():
    """Run company research with hybrid search strategy."""

    # Configuration with hybrid search
    config = Configuration(
        max_search_queries=6,  # More queries to show hybrid split
        max_search_results=3,
        max_reflection_steps=1,
        llm_model="claude-sonnet-4-5-20250929",  # Latest Claude Sonnet 4.5
        temperature=0.7,
        search_provider="hybrid"  # Tavily + Google Programmable Search
    )

    print("=" * 80)
    print("COMPANY RESEARCH WITH HYBRID SEARCH STRATEGY")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Search provider: {config.search_provider} (HYBRID)")
    print(f"  Max search queries: {config.max_search_queries}")
    print(f"  Strategy: First half Tavily, second half Google search")
    print(f"  Max search results: {config.max_search_results}")
    print(f"  Max reflection steps: {config.max_reflection_steps}")
    print(f"  LLM model: {config.llm_model}")

    # Build graph
    print("\nBuilding research graph...")
    graph = build_research_graph(config)

    # Company to research
    company_name = "Anthropic"

    print(f"\nResearching: {company_name}")
    print("-" * 80)

    # Initial state
    initial_state = {
        "company_name": company_name,
        "extraction_schema": DEFAULT_SCHEMA,
        "user_context": "",
        "research_queries": [],
        "search_results": [],
        "research_notes": "",
        "extracted_data": {},
        "reflection_count": 0,
        "missing_fields": [],
        "follow_up_queries": [],
        "is_complete": False,
        "messages": []
    }

    # Run research
    print("\n🔍 Starting hybrid search workflow...\n")
    print("   Strategy: first half of the queries → Tavily")
    print("             second half → Google search (Tavily if unavailable)\n")

    final_state = await graph.ainvoke(initial_state)

    # Display results
    print("\n" + "=" * 80)
    print("RESEARCH COMPLETE")
    print("=" * 80)

    print("\n📊 EXTRACTED DATA:")
    print("-" * 80)
    print(json.dumps(final_state["extracted_data"], indent=2))

    print("\n\n📝 RESEARCH NOTES (PREVIEW):")
    print("-" * 80)
    notes = final_state["research_notes"]
    preview = notes[:500] + "..." if len(notes) > 500 else notes
    print(preview)

    print("\n\n📈 STATISTICS:")
    print("-" * 80)
    print(f"Search queries executed: {len(final_state['research_queries'])}")
    print(f"Search results found: {len(final_state['search_results'])}")
    print(f"Reflection iterations: {final_state['reflection_count']}")
    print(f"Fields extracted: {len(final_state['extracted_data'])}")
    print(f"Missing fields: {len(final_state['missing_fields'])}")

    if final_state['missing_fields']:
        print(f"\nMissing/incomplete fields: {', '.join(final_state['missing_fields'])}")

    print("\n🔀 QUERY SPLIT (HYBRID STRATEGY):")
    print("-" * 80)
    total_queries = len(final_state['research_queries'])
    tavily_queries = total_queries // 2

    print(f"Total queries: {total_queries}")
    print(f"  ├─ Tavily: {tavily_queries} queries")
    print(f"  └─ Google search: {total_queries - tavily_queries} queries (Tavily if Google was unavailable)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment")
        print("Please set it in your .env file")
        exit(1)

    if not os.getenv("TAVILY_API_KEY"):
        print("Warning: TAVILY_API_KEY not found in environment")
        print("Hybrid mode requires Tavily for first half of queries")
        print("Get your key at: https://tavily.com/")
        exit(1)

    print("\n📌 NOTE: Hybrid mode uses:")
    print("   - Tavily API for the first half of the queries (requires TAVILY_API_KEY)")
    print("   - Google Programmable Search for the rest (GOOGLE_API_KEY + GOOGLE_CSE_ID)\n")

    # Run async main
    asyncio.run(main())
