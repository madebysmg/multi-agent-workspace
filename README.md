# Multi-Agent Workspace

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> Claude Code로 LangGraph 기반 멀티 에이전트를 개발할 때 쓰는 워크스페이스 템플릿

Claude Code에서 에이전트를 만들 때 필요한 세 가지를 한 저장소에 모았습니다.

1. **커스텀 Claude Code 스킬 8개** (`.claude/skills/`): PRD → User Story → Jira 티켓으로 이어지는 애자일 파이프라인, 딥 리서치, DB 설계, 멀티 에이전트, Next.js 프론트엔드, 워크스페이스 이식
2. **예제 에이전트** (`src/agents/`): LangGraph로 만든 Research → Extraction → Reflection 루프의 기업 리서치 에이전트와, 이를 FastAPI 서비스 3개로 나눈 A2A 버전
3. **레퍼런스와 설계 문서**: Claude가 참조할 LangGraph / Google ADK 문서 사본(`.claude/references/`)과 A2A 아키텍처·인프라·비용 설계 문서(`docs/`)

2025년 10월에 작성한 개인 프로젝트입니다. 모델명, 가격, 외부 API 정보는 그 시점 기준이라 지금과 다를 수 있습니다.

---

## 프로젝트 구조

```
multi-agent-workspace/
├── .claude/
│   ├── skills/                      # 커스텀 Claude Code 스킬 (8개)
│   │   ├── agile-product/           # PRD 작성
│   │   ├── agile-stories/           # PRD → User Story (Given-When-Then AC)
│   │   ├── agile-jira/              # Jira REST API로 Epic/Story 생성 (scripts/jira-api.js)
│   │   ├── deep-research/           # 스키마 기반 웹 리서치 에이전트 가이드, 검색 API 8종 문서
│   │   ├── database-designer/       # DB 선택(15종 비교) + 스키마 패턴 10종
│   │   ├── langgraph-multi-agent/   # Researcher → Writer → Reviewer 워크플로우
│   │   ├── fullstack-frontend/      # Next.js 14 + shadcn/ui 템플릿 (미완성, 아래 참고)
│   │   └── workspace-transplant/    # 이 저장소의 패턴을 다른 프로젝트로 옮기는 스크립트
│   ├── references/                  # LangGraph / Google ADK 문서 사본 (+ 라이선스)
│   ├── AGILE_SKILLS_V2.md           # 애자일 스킬 3종 가이드
│   └── SKILLS_COLLECTION.md         # 스킬 목록
│
├── src/
│   ├── agents/
│   │   ├── company_research/        # LangGraph 에이전트 (research / extraction / reflection / graph)
│   │   └── a2a/                     # A2A 분리 버전
│   │       ├── coordinator/         # FastAPI :8000, 워크플로우 조율 + reflection
│   │       ├── research_agent/      # FastAPI :5001
│   │       └── extraction_agent/    # FastAPI :5002
│   └── common/                      # llm.py (rate limit 적용 LLM), utils.py (중복 제거, 토큰 제한 등)
│
├── examples/                        # 실행 예제 6개
├── docs/                            # 시작 가이드, 에이전트 작성 가이드, 설계·분석 문서
├── docker-compose.yml               # 개발용 컨테이너
├── docker-compose.a2a.yml           # A2A 서비스 3개
├── requirements.txt
└── .env.example
```

---

## 빠른 시작

### 1. 설치

```bash
git clone https://github.com/madebysmg/multi-agent-workspace.git
cd multi-agent-workspace

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .env에 ANTHROPIC_API_KEY, TAVILY_API_KEY 등 입력
```

### 2. 예제 에이전트 실행

예제는 `src` 패키지를 import하므로 저장소 루트를 `PYTHONPATH`에 넣고 실행합니다.

```bash
# 기본 예제 (ANTHROPIC_API_KEY + TAVILY_API_KEY 필요)
PYTHONPATH=. python examples/basic_research.py

# DuckDuckGo 검색 예제 (검색 API 키 없이, ANTHROPIC_API_KEY만 필요)
pip install -U ddgs
PYTHONPATH=. python examples/free_research_duckduckgo.py
```

| 예제 | 내용 |
|------|------|
| `basic_research.py` | 기본 스키마로 한 회사 리서치 |
| `custom_schema.py` | 커스텀 추출 스키마 |
| `streaming_example.py` | 단계별 스트리밍 출력 |
| `free_research_duckduckgo.py` | DuckDuckGo 검색 사용 |
| `hybrid_search_example.py` | Tavily + Google Programmable Search 혼합 (`search_provider="hybrid"`) |
| `google_adk_example.py` | `google_adk` 검색 제공자(Google Programmable Search) 사용 |

### 3. A2A 서비스 실행 (선택)

```bash
docker-compose -f docker-compose.a2a.yml up --build

curl http://localhost:8000/health
curl http://localhost:5001/.well-known/agent.json   # Agent Card
```

Coordinator의 `POST /research`가 Research Agent와 Extraction Agent를 HTTP로 호출하고, reflection은 Coordinator 안에서 실행합니다. Docker 없이 실행하는 방법은 [src/agents/a2a/README.md](src/agents/a2a/README.md)에 있습니다. 이때는 `pip install fastapi "uvicorn[standard]" httpx`가 추가로 필요하고, `coordinator/app.py`의 에이전트 URL을 `localhost`로 바꿔야 합니다.

### 4. Claude Code 스킬 사용

이 디렉터리에서 Claude Code를 실행하면 `.claude/skills/`의 스킬을 쓸 수 있습니다.

```bash
/skill agile-product "OAuth 인증 추가"                     # → docs/prd/*.md
/skill agile-stories --prd=docs/prd/<파일>.md              # → docs/stories/*.md
/skill agile-jira --import docs/stories/                   # → Jira Epic/Story
/skill langgraph-multi-agent
/skill deep-research
```

`agile-jira`는 MCP 서버 없이 Jira Cloud REST API를 직접 호출합니다. `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`를 환경 변수나 `.claude/skills/agile-jira/.jira-config.json`(git에서 제외됨)에 설정하세요. 스킬별 설명은 [.claude/SKILLS_COLLECTION.md](.claude/SKILLS_COLLECTION.md)에 있습니다.

---

## 기업 리서치 에이전트

```
research ──→ extract ──→ reflect ──→ (완료) END
   ↑                         │
   └──── follow-up 쿼리 ─────┘
```

- **research**: 추출 스키마를 보고 검색 쿼리를 만들고, 웹 검색 결과를 URL 기준으로 중복 제거한 뒤 소스당 토큰을 제한해 리서치 노트를 작성
- **extract**: 리서치 노트에서 스키마에 맞는 JSON 추출
- **reflect**: 누락 필드를 찾아 follow-up 쿼리를 만들고, `max_reflection_steps` 안에서 다시 research로 보냄
- 프롬프트는 `prompts.py`, LLM 초기화와 rate limit(`InMemoryRateLimiter`)은 `src/common/llm.py`에 모았습니다.

### 스키마만 바꿔 다른 대상 리서치

`extraction_schema`를 바꾸면 회사 외에 제품, 인물, 논문 등도 같은 루프로 조사할 수 있습니다.

```python
import asyncio
from src.agents.company_research import Configuration, build_research_graph

PRODUCT_SCHEMA = {
    "title": "Product Research",
    "type": "object",
    "properties": {
        "product_name": {"type": "string"},
        "manufacturer": {"type": "string"},
        "key_features": {"type": "array", "items": {"type": "string"}},
        "pros": {"type": "array", "items": {"type": "string"}},
        "cons": {"type": "array", "items": {"type": "string"}},
    },
}

config = Configuration(search_provider="duckduckgo", max_search_queries=3, max_reflection_steps=1)
graph = build_research_graph(config)

result = asyncio.run(graph.ainvoke({
    "company_name": "Sony WH-1000XM5",   # 리서치 대상 (필드명은 company_name)
    "extraction_schema": PRODUCT_SCHEMA,
    "user_context": "Focus on noise cancelling and battery life",
    "research_queries": [], "search_results": [], "research_notes": "",
    "extracted_data": {}, "reflection_count": 0, "missing_fields": [],
    "follow_up_queries": [], "is_complete": False, "messages": [],
}))
print(result["extracted_data"])
```

### 검색 제공자

`Configuration.search_provider`로 고릅니다. 코드에 구현된 값은 다음과 같습니다.

| 값 | 필요한 것 |
|----|-----------|
| `tavily` (기본값) | `TAVILY_API_KEY` |
| `duckduckgo` | `pip install -U ddgs` (API 키 불필요) |
| `google_adk` | Google Programmable Search(Custom Search JSON API). `pip install langchain-google-community`, `GOOGLE_API_KEY`, `GOOGLE_CSE_ID` 필요. 이름과 달리 Google ADK나 Gemini는 쓰지 않으며, 래퍼를 만들 수 없으면 Tavily로 대체 |
| `hybrid` | 쿼리 앞 절반은 Tavily, 나머지는 `google_adk`와 같은 Google 검색 (`TAVILY_API_KEY` 필요, Google을 쓸 수 없으면 전부 Tavily) |
| `serpapi` | `pip install google-search-results`, SerpAPI 키 |
| `bing` | Bing Search API 키 (`BING_SUBSCRIPTION_KEY`) |
| `brave` | Brave Search API 키 (`BRAVE_API_KEY`) |

Serper, Exa, Jina를 포함한 검색 API 8종의 가격·무료 한도·연동 코드 비교는 [deep-research 스킬 문서](.claude/skills/deep-research/references/WEB_SEARCH_APIS.md)에 정리했습니다. Serper, Exa, Jina는 문서에만 있고 에이전트 코드에는 구현되어 있지 않습니다.

---

## 문서

| 문서 | 내용 |
|------|------|
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | 워크스페이스 사용 가이드 |
| [docs/CREATE_AGENT.md](docs/CREATE_AGENT.md) | 새 에이전트 만들기 |
| [docs/README_DEEP_RESEARCH.md](docs/README_DEEP_RESEARCH.md) | 리서치 에이전트 상세 |
| [docs/COMPARISON_ANALYSIS.md](docs/COMPARISON_ANALYSIS.md) | [langchain-ai/company-researcher](https://github.com/langchain-ai/company-researcher)와 비교 |
| [docs/A2A_ARCHITECTURE.md](docs/A2A_ARCHITECTURE.md) | A2A 분산 구조 설계 |
| [docs/INFRASTRUCTURE_DESIGN.md](docs/INFRASTRUCTURE_DESIGN.md), [docs/COST_OPTIMIZATION.md](docs/COST_OPTIMIZATION.md) | AWS 인프라·비용 설계 (Terraform은 문서 안의 예시 코드) |
| [docs/LLM_CLOUD_PRICING_2025.md](docs/LLM_CLOUD_PRICING_2025.md) | LLM 가격 비교 (2025-10 기준) |
| [CLAUDE.md](CLAUDE.md) | Claude Code용 프로젝트 기술 문서 |
| [.claude/references/README.md](.claude/references/README.md) | 레퍼런스 사용법 |

---

## 현재 상태와 한계

- 자동화된 테스트가 없습니다. 예제와 A2A 서비스의 동작을 검증한 기록도 저장소에 없습니다.
- LLM 호출은 `ChatAnthropic`으로 고정되어 있습니다(`src/common/llm.py`). `Configuration.llm_model` 설명에 나오는 DeepSeek, Qwen, Gemini 모델명을 넣어도 그대로는 동작하지 않습니다.
- `duckduckgo`, `google_adk`, `serpapi` 등 일부 검색 제공자는 `requirements.txt`에 없는 패키지가 필요합니다(`requirements.txt` 하단 주석 참고). `serpapi`, `bing`, `brave`는 패키지를 불러오지 못하면 DuckDuckGo로 바꾼다는 메시지만 출력하고, 실제 대체 검색은 하지 않습니다.
- `requirements.txt`는 대부분 하한 버전만 지정합니다. `langchain-community`만 `<1.0`으로 막았는데, 코드가 쓰는 `TavilySearchResults`가 upstream에서 deprecated 상태이고 1.0에서 제거될 예정이기 때문입니다. 최신 LangChain/LangGraph에서 동작하는지는 확인하지 않았습니다.
- `fullstack-frontend` 템플릿에는 `lib/`(`api.ts`, `types.ts`, `utils.ts`), PostCSS 설정, 일부 컴포넌트가 빠져 있어 그대로는 빌드되지 않습니다.
- `CLAUDE.md`와 `docs/`의 성능·비용 수치(예: 1,000개 회사 90초, 월 비용 91% 절감)는 설계 단계의 추정치이며 측정값이 아닙니다.
- `docs/`의 AWS·Terraform 내용은 설계 문서이고, 인프라 코드는 저장소에 없습니다.

---

## 서드파티 콘텐츠

- `.claude/references/`의 LangGraph 문서(MIT)와 Google ADK `llms.txt`(Apache-2.0)는 원본 저장소의 사본입니다. 출처와 라이선스 전문은 [.claude/references/README.md](.claude/references/README.md)와 `.claude/references/licenses/`에 있습니다. ADK 전체본(`llms-full.txt`, 약 3MB)은 포함하지 않았습니다.
- Anthropic의 문서 스킬(`docx`, `pdf`, `pptx`, `xlsx`)과 `skill-creator`는 포함하지 않습니다. 필요하면 [anthropics/skills](https://github.com/anthropics/skills)에서 받으세요.
- 브라우저 자동화 스킬 `playwright-skill`도 포함하지 않습니다: [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill)

## 라이선스

이 저장소의 코드와 문서는 [MIT License](LICENSE)입니다. 위 서드파티 파일은 각 원본의 라이선스를 따릅니다.
