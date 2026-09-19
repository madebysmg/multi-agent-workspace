# Google ADK 분석 및 비교

> Google Agent Development Kit (ADK) 분석 및 LangGraph 기반 시스템과의 비교

**작성일**: 2025-10-22
**목적**: ADK 샘플 분석을 통한 개선사항 도출

---

## 📋 목차

1. [Google ADK 개요](#google-adk-개요)
2. [ADK 샘플 분석](#adk-샘플-분석)
3. [LangGraph vs ADK 비교](#langgraph-vs-adk-비교)
4. [적용 가능한 개선사항](#적용-가능한-개선사항)
5. [향후 ADK 버전 구현 계획](#향후-adk-버전-구현-계획)

---

## Google ADK 개요

### 기본 정보

| 항목 | 내용 |
|------|------|
| **Repository** | https://github.com/google/adk-python |
| **Samples** | https://github.com/google/adk-samples |
| **Documentation** | https://google.github.io/adk-docs/ |
| **License** | Apache 2.0 |
| **Language** | Python 3.10+ (86.8%), Java (1.1%) |
| **Status** | Not officially supported (demonstration) |

### 핵심 특징

1. **Code-First Development**
   - Python으로 에이전트 로직 직접 정의
   - 선언적(declarative)이 아닌 명령적(imperative) 접근

2. **Hierarchical Multi-Agent**
   - `sub_agents` 파라미터로 계층적 구조 구성
   - Parent agent가 child agents를 도구로 사용

3. **Rich Tool Ecosystem**
   - 내장 Google Search (Gemini와 통합)
   - OpenAPI 기반 커스텀 도구
   - BigQuery, Cloud Storage 등 GCP 통합

4. **Gemini 최적화**
   - Gemini 2.0/2.5 Flash 모델과 긴밀 통합
   - Google Search 무료 제공 (Gemini 2+ 전용)
   - Vertex AI Agent Engine 배포

5. **Human-in-the-Loop (HITL)**
   - 도구 실행 전 확인 플로우
   - 커스텀 입력 검증

---

## ADK 샘플 분석

### 1. Academic Research Agent

**목적**: 학술 논문 분석 및 연구 트렌드 파악

#### 아키텍처

```
academic_coordinator (Root Agent)
├── academic_websearch_agent (Sub-agent)
│   └── Google Search tool
└── academic_newresearch_agent (Sub-agent)
    └── Research synthesis
```

#### 워크플로우

1. **Paper Analysis**: 세미널 논문 핵심 기여 파악
2. **Citation Discovery**: Google Search로 최근 인용 논문 검색
3. **Future Research Synthesis**: 새로운 연구 방향 제안

#### 주요 코드 패턴

```python
# Agent definition (추정)
academic_coordinator = Agent(
    name="academic_coordinator",
    model="gemini-2.5-pro",
    description="analyzing seminal papers...",
    instructions=ACADEMIC_COORDINATOR_PROMPT,
    sub_agents=[
        academic_websearch_agent,
        academic_newresearch_agent
    ]
)
```

#### 특징

- ✅ Multi-modal: PDF 입력 지원
- ✅ Google Search 내장
- ✅ Sequential delegation (분석 → 검색 → 합성)
- ✅ Evaluation suite 포함 (`eval/`)
- ✅ Vertex AI 배포 스크립트 (`deployment/`)

---

### 2. FOMC Research Agent

**목적**: 연방공개시장위원회(FOMC) 회의 분석 및 보고서 생성

#### 아키텍처

```
root_agent (Orchestrator)
├── research_agent (Coordinator)
│   ├── retrieve_meeting_data_agent
│   ├── extract_page_data_agent
│   └── summarize_meeting_agent
└── analysis_agent (Report Generator)
```

#### 주요 도구

| 도구 | 용도 |
|------|------|
| `fetch_page_tool` | HTTP 요청으로 웹 콘텐츠 수집 |
| `store_state_tool` | ToolContext에 정보 저장 |
| `analyze_video_tool` | YouTube 비디오 처리 |
| `compute_probability_tool` | Fed Futures 가격 기반 확률 계산 |
| `compare_statements` | FOMC 성명서 비교 |
| `fetch_transcript` | 회의록 검색 |

#### 특징

- ✅ **Non-conversational workflow**: 자율 실행
- ✅ **Rate Limiting**: `rate_limit_callback`으로 429 에러 방지
- ✅ **External DB Integration**: BigQuery (Fed Futures 데이터)
- ✅ **Multi-modal**: YouTube 비디오 분석
- ✅ **CSV 지원**: 히스토리컬 데이터

#### 우리 시스템과의 유사점 ⭐

| 요소 | FOMC Research | 우리 시스템 |
|------|---------------|-------------|
| **워크플로우** | Multi-agent, non-conversational | Research-Extraction-Reflection |
| **데이터 수집** | Web scraping + API | Tavily API |
| **Rate Limiting** | ✅ `rate_limit_callback` | ✅ `InMemoryRateLimiter` |
| **외부 DB** | BigQuery | (설계됨: PostgreSQL) |
| **타겟** | 시장 이벤트 | 비상장 중소기업 |

---

### 3. 기타 Research 관련 샘플

#### Google Trends Agent

- **목적**: Google Trends 데이터 분석
- **도구**: BigQuery (Google Trends dataset)
- **특징**: 트렌드 검색어 추출

#### Brand Search Optimization

- **목적**: 이커머스 상품 데이터 강화
- **도구**: Google Search
- **특징**: 상위 검색 결과 분석 및 비교

#### Data Science Agent

- **목적**: 정교한 데이터 분석
- **특징**: Multi-agent system

---

## LangGraph vs ADK 비교

### 아키텍처 패턴

| 항목 | LangGraph (우리 시스템) | Google ADK |
|------|------------------------|------------|
| **Orchestration** | Graph-based (Explicit nodes + edges) | Hierarchical (Parent-child agents) |
| **Routing** | Conditional edges (명시적) | LLM delegation (암시적) |
| **State 관리** | `TypedDict` + `Annotated` | `ToolContext` + shared state |
| **Tool 사용** | Function tools | AgentTool (sub-agents as tools) |
| **실행 흐름** | Deterministic (predefined graph) | Dynamic (LLM decides routing) |

### 코드 예시 비교

#### LangGraph (우리 방식)

```python
# Explicit graph definition
workflow = StateGraph(ResearchState)

# Add nodes
workflow.add_node("research", research_node)
workflow.add_node("extract", extraction_node)
workflow.add_node("reflect", reflection_node)

# Explicit routing
workflow.add_edge("research", "extract")
workflow.add_edge("extract", "reflect")
workflow.add_conditional_edges(
    "reflect",
    should_continue,
    {"continue": "research", "end": END}
)
```

**특징**:
- ✅ 명확한 워크플로우 (시각화 가능)
- ✅ 예측 가능한 실행 경로
- ✅ 디버깅 용이
- ❌ 유연성 낮음 (사전 정의 필요)

#### Google ADK

```python
# Hierarchical agent definition
coordinator = Agent(
    name="coordinator",
    model="gemini-2.5-pro",
    sub_agents=[research_agent, analysis_agent]
)

# LLM이 자동으로 적절한 sub-agent 선택
```

**특징**:
- ✅ 유연한 라우팅 (LLM이 결정)
- ✅ 간결한 코드
- ❌ 실행 경로 예측 어려움
- ❌ 디버깅 복잡 (LLM 판단 추적 필요)

---

### 장단점 비교

#### LangGraph

**장점**:
- ✅ **명시적 제어**: 정확한 실행 순서 보장
- ✅ **디버깅 용이**: 각 노드 출력 추적 가능
- ✅ **예측 가능성**: Deterministic workflow
- ✅ **시각화**: 그래프 구조 명확
- ✅ **모델 중립적**: Claude, GPT, Gemini 모두 사용 가능

**단점**:
- ❌ **Boilerplate 많음**: 노드, 엣지 모두 명시
- ❌ **유연성 낮음**: 동적 변경 어려움
- ❌ **복잡한 조건부 라우팅**: 많은 조건 시 코드 복잡

#### Google ADK

**장점**:
- ✅ **간결한 코드**: Sub-agent만 정의
- ✅ **동적 라우팅**: LLM이 상황에 맞게 선택
- ✅ **Google 생태계**: Vertex AI, BigQuery 통합
- ✅ **내장 Google Search**: Gemini 2+ 무료
- ✅ **Multi-modal**: PDF, 비디오 쉽게 처리

**단점**:
- ❌ **LLM 의존성**: 라우팅 실패 가능
- ❌ **예측 불가**: 실행 경로 사전 파악 어려움
- ❌ **디버깅 어려움**: LLM 판단 추적 필요
- ❌ **Gemini 편향**: 다른 모델 사용 시 제한적
- ❌ **비공식 지원**: Production 사용 주의

---

## 적용 가능한 개선사항

### 1. Evaluation Framework ⭐⭐⭐

**ADK 접근**:
- `eval/` 폴더에 평가 스크립트 분리
- `AgentEvaluator`로 베이스라인 비교
- `uv run pytest eval` 실행

**우리 시스템에 적용**:
```
company-search-agent/
├── src/agents/company_research/
├── examples/
└── eval/                        # NEW
    ├── __init__.py
    ├── baseline_data.json       # Expected outputs
    ├── test_quality.py          # Completeness score
    ├── test_cost.py             # Token/API cost tracking
    └── test_reflection_roi.py   # Reflection 효과 측정
```

**구현 계획**:
1. Baseline dataset 생성 (10-20개 회사)
2. Quality metrics (completeness, accuracy)
3. Cost tracking (토큰, API 호출)
4. Reflection ROI 측정

---

### 2. Deployment Scripts ⭐⭐

**ADK 접근**:
- `deployment/` 폴더에 배포 스크립트 분리
- Vertex AI Agent Engine 배포
- `deploy.py --create` 간편 배포

**우리 시스템에 적용**:
```
company-search-agent/
├── src/agents/company_research/
├── examples/
└── deployment/                  # NEW
    ├── __init__.py
    ├── docker/
    │   ├── Dockerfile
    │   └── docker-compose.yml
    ├── cloud_run/
    │   └── deploy_cloud_run.sh
    └── api/
        └── fastapi_server.py
```

**구현 계획**:
1. Docker 컨테이너화
2. FastAPI REST API 래퍼
3. Cloud Run 배포 스크립트 (Google Cloud)
4. 환경 변수 관리 (Secret Manager)

---

### 3. Sub-agent Modularization ⭐

**ADK 접근**:
- `sub_agents/` 폴더에 전문화된 에이전트 분리
- 각 에이전트가 독립적 책임

**우리 시스템에 적용**:
```
src/agents/company_research/
├── phases/                      # Rename from current structure
│   ├── __init__.py
│   ├── research.py
│   ├── extraction.py
│   └── reflection.py
└── specialized_agents/          # NEW (future)
    ├── __init__.py
    ├── indirect_source_agent.py  # 공시자료 전문
    ├── social_media_agent.py     # SNS 크롤링
    └── financial_agent.py        # 재무 분석
```

**장점**:
- 책임 분리 명확
- 테스트 용이
- 재사용 가능

---

### 4. Rate Limiting Callback ⭐⭐⭐

**ADK 접근**:
```python
# FOMC Research agent
rate_limit_callback = ...  # 429 에러 방지
```

**우리 시스템 현황**:
- ✅ 이미 구현됨 (`InMemoryRateLimiter`)
- ✅ 0.8 req/sec (Anthropic Tier 1)

**개선 방향**:
```python
# llm.py 개선
class AdaptiveRateLimiter:
    """429 에러 감지 시 자동으로 속도 조절"""
    def __init__(self, initial_rate=0.8):
        self.current_rate = initial_rate
        self.error_count = 0

    def on_error(self, error):
        if "429" in str(error):
            self.current_rate *= 0.5  # 속도 절반으로
            self.error_count += 1

    def on_success(self):
        if self.error_count > 0:
            self.current_rate *= 1.1  # 점진적 회복
```

---

### 5. Multi-modal Support (향후)

**ADK 접근**:
- PDF, 비디오, 이미지 입력 지원
- Gemini 2.5 Flash의 multi-modal 능력 활용

**우리 시스템에 적용 (미래)**:
- 회사 발표 자료 (PDF) 분석
- YouTube 회사 소개 영상 분석
- 웹사이트 스크린샷 분석

**구현 시기**: v3.0 (현재 v2.0)

---

### 6. Tool Context State Management

**ADK 접근**:
- `store_state_tool`로 중간 결과 저장
- Agent 간 컨텍스트 공유

**우리 시스템 비교**:
- 현재: `ResearchState` (TypedDict)로 모든 상태 관리
- ADK: ToolContext로 도구 간 상태 공유

**개선 여부**: 현재 방식으로 충분 (명시적 상태 관리 선호)

---

## 향후 ADK 버전 구현 계획

### Phase 1: PoC (Proof of Concept)

**목표**: Google ADK 기반 간단한 company research agent 구현

**범위**:
```
company-search-agent-adk/          # 별도 디렉토리
├── adk_agent/
│   ├── agent.py                   # Root coordinator
│   ├── sub_agents/
│   │   ├── web_search_agent.py
│   │   └── extraction_agent.py
│   └── prompts.py
├── pyproject.toml                 # uv 기반
└── README_ADK.md
```

**타임라인**: 1-2주

**핵심 검증 사항**:
1. Google Search 무료 사용 (Gemini 2.5 Flash)
2. Hierarchical agent 패턴 적용
3. 비용 비교 (vs LangGraph 버전)

---

### Phase 2: Feature Parity

**목표**: LangGraph 버전과 동등한 기능 구현

**추가 기능**:
- Reflection loop (품질 평가)
- Custom schema support
- PostgreSQL 통합 (캐싱)
- CloudWatch monitoring

**타임라인**: 2-4주

---

### Phase 3: ADK 고유 기능 활용

**목표**: ADK만의 강점 활용

**신규 기능**:
1. **Multi-modal 입력**:
   - 회사 발표자료 PDF 분석
   - YouTube 기업 소개 영상 처리
   - 웹사이트 스크린샷 분석

2. **BigQuery 통합**:
   - 산업 트렌드 데이터
   - 기업 통계 (매출, 직원 수 등)

3. **Vertex AI 배포**:
   - Agent Engine으로 프로덕션 배포
   - Auto-scaling

**타임라인**: 1-2개월

---

## 비용 비교 분석

### LangGraph 버전 (현재)

| 항목 | 단가 | 사용량 (1회) | 비용 |
|------|------|-------------|------|
| Claude Sonnet 4.5 | $3/$15 per 1M | ~10K tokens | ~$0.03-0.15 |
| Tavily API | $0.005/쿼리 | 3-6 쿼리 | $0.015-0.03 |
| **총계** | | | **~$0.05-0.18** |

### ADK 버전 (예상)

| 항목 | 단가 | 사용량 (1회) | 비용 |
|------|------|-------------|------|
| Gemini 2.5 Flash | $0.30/$2.50 per 1M | ~10K tokens | ~$0.003-0.025 |
| Google Search (ADK) | **무료** | 3-6 쿼리 | **$0.00** |
| **총계** | | | **~$0.003-0.025** |

**비용 절감**: **85-95%** (검색 무료 + 저렴한 LLM)

---

## 결론 및 권장사항

### 1. 단기 개선 (현 LangGraph 버전)

우선 순위 순:

1. ✅ **Evaluation Framework** 구축 (가장 중요)
   - Baseline dataset 생성
   - Quality/cost metrics

2. ✅ **Deployment Scripts** 작성
   - Docker + FastAPI
   - Cloud Run 배포

3. ✅ **Adaptive Rate Limiting**
   - 429 에러 자동 대응

### 2. 중기 계획 (ADK PoC)

- Google ADK 기반 별도 버전 구현
- 비용 비교 실험
- Multi-modal 기능 탐색

### 3. 장기 방향

**Hybrid 전략 권장**:

| 용도 | Framework | 이유 |
|------|-----------|------|
| **프로덕션 (현재)** | LangGraph | 안정성, 예측 가능성 |
| **실험/탐색** | ADK | 비용 절감, multi-modal |
| **대량 배치** | ADK | 무료 검색, 저렴한 LLM |

**양쪽 모두 유지하는 이유**:
- LangGraph: 안정적, 디버깅 용이, 모델 중립적
- ADK: 비용 효율적, Google 생태계 통합, 실험적 기능

---

## 참고 자료

### 공식 문서

- **ADK Documentation**: https://google.github.io/adk-docs/
- **ADK Python**: https://github.com/google/adk-python
- **ADK Samples**: https://github.com/google/adk-samples

### 주요 샘플

- **Academic Research**: `python/agents/academic-research/`
- **FOMC Research**: `python/agents/fomc-research/`
- **Data Science**: `python/agents/data-science/`

### 추가 리소스

- **Awesome ADK Agents**: https://github.com/Sri-Krishna-V/awesome-adk-agents
- **ADK Made Simple**: https://github.com/chongdashu/adk-made-simple

---

**작성**: 2025-10-22
**버전**: 1.0.0
**다음 업데이트**: ADK PoC 완료 후
