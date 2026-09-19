# Claude Code Skills Collection

Custom Claude Code skills bundled in `.claude/skills/`. Each skill follows the progressive-disclosure layout (a lean `SKILL.md`, with details in `references/`, helper code in `scripts/` and templates in `assets/`).

**Total Skills**: 8

| Skill | Area | Main files | External requirements |
|-------|------|------------|-----------------------|
| **agile-product** | PRD writing | `SKILL.md` | - |
| **agile-stories** | User stories | `SKILL.md` | - |
| **agile-jira** | Jira tickets | `SKILL.md`, `scripts/jira-api.js`, `references/` | Node.js, Jira Cloud API token |
| **deep-research** | Web research agent | `SKILL.md`, `references/` (search APIs, LLM selection) | Anthropic API key, a search API key (optional) |
| **database-designer** | Database selection and schema | `SKILL.md`, `references/` | - |
| **langgraph-multi-agent** | Multi-agent workflows | `SKILL.md`, `references/` | LLM API key |
| **fullstack-frontend** | Next.js frontend template | `SKILL.md`, `assets/nextjs-template/`, `scripts/` | Node.js |
| **workspace-transplant** | Reusing this workspace's patterns elsewhere | `SKILL.md`, `scripts/*.py`, `references/` | Python 3 |

Not bundled: third-party skills such as Anthropic's `docx`, `pdf`, `pptx`, `xlsx` and `skill-creator` (see https://github.com/anthropics/skills) and the community `playwright-skill` (see https://github.com/lackeyjb/playwright-skill). Install them separately if you want them.

---

## Agile workflow (3 skills)

The three agile skills form one pipeline: PRD → user stories → Jira tickets. Every intermediate document is plain Markdown, so it can be reviewed in git before the next step. See [AGILE_SKILLS_V2.md](AGILE_SKILLS_V2.md) for the full guide.

### 1. agile-product
**Path**: `.claude/skills/agile-product/`

Interactive, question-driven PRD writing (problem, users, goals and metrics, scope). Output: `docs/prd/<feature>-<date>.md`.

```bash
/skill agile-product "Add OAuth authentication"
```

### 2. agile-stories
**Path**: `.claude/skills/agile-stories/`

Reads a PRD, proposes an Epic structure and writes user stories with Given-When-Then acceptance criteria and story-point estimates. Output: one Markdown file per story in `docs/stories/`.

```bash
/skill agile-stories --prd=docs/prd/oauth-authentication-2024-10-23.md
```

### 3. agile-jira
**Path**: `.claude/skills/agile-jira/`

Creates Jira Epics and Stories from the story files through the Jira Cloud REST API v3. No MCP server is needed: `scripts/jira-api.js` (plain Node.js, no npm dependencies) supports `import`, `create-epic`, `create-story`, `search` and `track`.

Configuration comes from environment variables (`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`) or from `.jira-config.json` (copy `.jira-config.example.json`; the real file is git-ignored).

```bash
/skill agile-jira --import docs/stories/
```

---

## Research and data (2 skills)

### 4. deep-research
**Path**: `.claude/skills/deep-research/`

Guide for building the schema-driven Research → Extraction → Reflection agent that lives in `src/agents/company_research/`. Changing the JSON extraction schema retargets the agent to companies, products, people or papers.

```
Research → Extraction → Reflection
   ↑                         ↓
   └──── loop if incomplete ─┘
```

References:
- `WEB_SEARCH_APIS.md`, `SEARCH_PROVIDERS.md`, `references/api/*.md`: notes on 8 search APIs (Tavily, Serper, Exa, Jina, Brave, DuckDuckGo, SerpAPI, Bing)
- `LLM_SELECTION.md`: model and cost comparison
- `PRIVATE_SME_RESEARCH.md`: strategies for researching private small and mid-sized companies
- `IMPLEMENTATION_GUIDE.md`, `PRODUCTION_CHECKLIST.md`, `TROUBLESHOOTING.md`

Note: the reference docs cover 8 APIs, while the agent code in `src/agents/company_research/research.py` implements `tavily`, `google_adk`, `hybrid`, `serpapi`, `bing`, `duckduckgo` and `brave`.

### 5. database-designer
**Path**: `.claude/skills/database-designer/`

Goes from requirements to a database choice and a schema.

- `DATABASE_OPTIONS.md`: 15 options (Supabase, PlanetScale, Neon, Firebase, MongoDB Atlas, AWS RDS/Aurora, Cloud SQL, Azure Database, PostgreSQL, MySQL, SQLite, MongoDB, Redis, ClickHouse) with a decision framework and migration paths
- `SCHEMA_DESIGN_PATTERNS.md`: 10 schema patterns with SQL (auth, e-commerce, blog/CMS, multi-tenancy, audit logging, media metadata, social, analytics events, notifications, tags)
- `API_REFERENCE.md`, `references/api/*.md`: per-database guides (connection, CRUD, examples)

---

## Agent development (2 skills)

### 6. langgraph-multi-agent
**Path**: `.claude/skills/langgraph-multi-agent/`

A Researcher → Writer → Reviewer LangGraph workflow with conditional routing on a quality score, plus reference notes on agent patterns, architecture, implementation and examples.

```
Researcher → Writer → Reviewer
                ↑        ↓
                └─ needs revision
```

### 7. workspace-transplant
**Path**: `.claude/skills/workspace-transplant/`

Carries this workspace's patterns (centralized prompts, rate-limited LLM setup, TypedDict state, Pydantic configuration, the A2A split) into another project.

Scripts (standard library only):
- `analyze_workspace.py`: scans a workspace and reports structure, patterns and reusable components
- `extract_component.py`: copies a component (`prompts`, `utils`, `llm`, `state`, `configuration`) to a target project and rewrites imports
- `scaffold_agent.py`: generates a new LangGraph, A2A or hybrid agent skeleton

---

## Frontend (1 skill)

### 8. fullstack-frontend
**Path**: `.claude/skills/fullstack-frontend/`

A Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui + React Query template for putting a web UI in front of a backend API such as the A2A coordinator. It includes dashboard and "new research" pages, `scripts/setup-frontend.sh` and `scripts/add-component.sh`, plus notes on API integration and deployment.

The template is incomplete: `lib/` (`api.ts`, `types.ts`, `utils.ts`), a PostCSS config and some components described in `SKILL.md` are missing, so it does not build as-is.

```bash
cp -r .claude/skills/fullstack-frontend/assets/nextjs-template ./frontend
cd frontend && bash ../.claude/skills/fullstack-frontend/scripts/setup-frontend.sh
```

---

## Adding or changing skills

1. Create a directory in `.claude/skills/<name>/` with a `SKILL.md` (YAML front matter with `name` and `description`).
2. Put long material in `references/`, runnable helpers in `scripts/` and templates in `assets/`.
3. Add the skill to the table at the top of this file.

## Resources

- Claude Code skills docs: https://docs.claude.com/en/docs/claude-code/skills
- Anthropic skills repository: https://github.com/anthropics/skills
