# Company Deep Research Agent

LangGraph를 활용한 웹 검색 기반 기업 딥리서치 에이전트입니다. LangChain의 company-researcher 아키텍처를 참고하여 구현되었으며, Research → Extraction → Reflection의 3단계 반복 워크플로우로 구성되어 있습니다.

## 특징

- **웹 검색 기반 리서치**: Tavily API를 활용한 실시간 웹 검색
- **구조화된 데이터 추출**: 사용자 정의 JSON 스키마로 데이터 추출
- **품질 반성 루프**: 자동으로 누락된 정보를 감지하고 추가 검색 수행
- **반복적 개선**: 최대 reflection 횟수까지 자동으로 품질 향상
- **커스텀 스키마 지원**: 비즈니스 요구에 맞는 스키마 정의 가능
- **비동기 실행**: 효율적인 동시 웹 검색

## 🎯 타겟 기업

본 에이전트는 **중소·중견 비상장 기업** 리서치에 특화되어 있습니다:

### 타겟 특성
- **기업 규모**: 중소기업(직원 10~300명) ~ 중견기업(직원 300~1,000명)
- **상장 여부**: 비상장사 (상장사의 경우 공시자료가 더 효과적)
- **업종**: B2B 제조, IT, 서비스업 등
- **정보 접근성**: 제한적 정보 공개, 웹사이트/뉴스 중심

### 검색 전략

**직접 정보 소스:**
- ✅ 회사 웹사이트, 블로그, 보도자료
- ✅ 산업 뉴스, 기술 매체
- ✅ 채용 공고 (조직 규모, 기술 스택 파악)
- ✅ 고객 사례, 파트너십 정보

**간접 정보 소스 (매우 중요!):**
- ✅ **상장사 공시에서 거래처/관계사로 언급**
  - 주요 거래처 명단 (매출/매입 상위)
  - 계열사/자회사 목록
  - 특수관계자 거래 내역
  - 협력업체 리스트
- ✅ **투자사/VC의 포트폴리오** (투자 유치 비상장사)
- ✅ **정부/공공기관 발주 정보** (나라장터, 사업 수행 실적)

**검색 쿼리 예시:**
```
"[회사명] 거래처"
"[회사명] 협력사"
"[회사명] 공급업체"
"[회사명] site:dart.fss.or.kr"  (전자공시)
"[회사명] 투자 유치"
"[회사명] 납품"
```

> 💡 **왜 간접 소스가 중요한가?** 비상장사 자체는 공시 의무가 없지만, 그들과 거래하는 상장사는 주요 거래처를 공시해야 합니다. 이를 통해 거래 규모, 관계의 성격, 사업 내용 등을 파악할 수 있습니다.

## 아키텍처

```
┌─────────────────────────────────────────────────────┐
│  1. RESEARCH PHASE (리서치)                          │
│  - 타겟 검색 쿼리 생성 (스키마 기반)                    │
│  - Tavily API로 동시 웹 검색 실행                      │
│  - 구조화된 리서치 노트 작성                           │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│  2. EXTRACTION PHASE (추출)                         │
│  - 리서치 노트 통합                                   │
│  - JSON 스키마에 맞춰 데이터 추출                      │
│  - 구조화된 출력 생성                                 │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│  3. REFLECTION PHASE (반성)                         │
│  - 추출 품질 평가                                     │
│  - 누락/불완전 필드 식별                              │
│  - 후속 검색 쿼리 생성                                │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
          [완료 OR 다시 Research]
```

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
cp .env.example .env
```

`.env` 파일 편집:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # https://tavily.com/
```

## 사용 방법

### 기본 예제

```python
import asyncio
from src.agents.company_research import Configuration, DEFAULT_SCHEMA, build_research_graph

async def main():
    # 설정
    config = Configuration(
        max_search_queries=3,
        max_search_results=3,
        max_reflection_steps=1,
        llm_model="claude-sonnet-4-5-20250929"
    )

    # 그래프 빌드
    graph = build_research_graph(config)

    # 초기 상태
    initial_state = {
        "company_name": "Anthropic",
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

    # 실행
    result = await graph.ainvoke(initial_state)

    print(result["extracted_data"])

asyncio.run(main())
```

### 예제 실행

예제는 `src` 패키지를 import하므로 저장소 루트에서 `PYTHONPATH=.`로 실행합니다.

```bash
# 기본 리서치
PYTHONPATH=. python examples/basic_research.py

# 커스텀 스키마 (스타트업 분석)
PYTHONPATH=. python examples/custom_schema.py

# 스트리밍 실행
PYTHONPATH=. python examples/streaming_example.py
```

## 프로젝트 구조

```
multi-agent-workspace/
│
├── src/
│   ├── agents/
│   │   ├── company_research/
│   │   │   ├── __init__.py
│   │   │   ├── configuration.py    # 에이전트 설정
│   │   │   ├── state.py           # 상태 정의
│   │   │   ├── prompts.py         # 프롬프트 템플릿
│   │   │   ├── graph.py           # 메인 워크플로우
│   │   │   ├── research.py        # Research phase
│   │   │   ├── extraction.py      # Extraction phase
│   │   │   └── reflection.py      # Reflection phase
│   │   └── a2a/                   # FastAPI 서비스로 나눈 A2A 버전
│   └── common/
│       ├── llm.py                 # rate limit 적용 LLM 초기화
│       └── utils.py               # 중복 제거, 소스 포맷팅 등
│
├── examples/
│   ├── basic_research.py      # 기본 예제
│   ├── custom_schema.py       # 커스텀 스키마
│   ├── streaming_example.py   # 스트리밍
│   └── ...                    # 검색 제공자별 예제 3개
│
├── .claude/
│   └── skills/
│       ├── langgraph-multi-agent/    # 기본 멀티에이전트 스킬
│       └── deep-research/            # 딥리서치 스킬
│
└── requirements.txt
```

## Configuration 옵션

```python
class Configuration:
    max_search_queries: int = 3       # 검색 쿼리 수 (1-10)
    max_search_results: int = 3       # 쿼리당 결과 수 (1-10)
    max_reflection_steps: int = 1     # 반복 횟수 (0-5)
    llm_model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.7
```

## 커스텀 스키마 정의

스타트업 분석용 커스텀 스키마 예시:

```python
CUSTOM_SCHEMA = {
    "title": "Startup Analysis",
    "type": "object",
    "properties": {
        "company_name": {
            "type": "string",
            "description": "Company name"
        },
        "funding_rounds": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "round": {"type": "string"},
                    "amount": {"type": "string"},
                    "date": {"type": "string"}
                }
            },
            "description": "Funding history"
        },
        "competitors": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Main competitors"
        }
    },
    "required": ["company_name"]
}
```

### 스키마 설계 Best Practices

1. **Flat 구조 선호**: 깊은 중첩보다 평평한 구조 사용
2. **명확한 설명**: 각 필드에 상세한 description 포함
3. **필수 필드 최소화**: truly required 필드만 지정
4. **배열 사용**: 중첩 객체 대신 배열 of simple objects

## 워크플로우 상세

### 1. Research Phase

**입력:**
- company_name: 조사할 회사명
- extraction_schema: 추출할 데이터 스키마
- user_context: 추가 컨텍스트 (optional)

**처리:**
1. 스키마 필드 분석
2. 타겟 검색 쿼리 생성 (LLM)
3. Tavily API로 웹 검색 실행
4. 검색 결과를 구조화된 노트로 정리 (LLM)

**출력:**
- research_queries: 생성된 검색 쿼리 목록
- search_results: 웹 검색 결과
- research_notes: 구조화된 리서치 노트

### 2. Extraction Phase

**입력:**
- research_notes: 리서치 노트
- extraction_schema: JSON 스키마

**처리:**
1. 노트에서 관련 정보 식별
2. 스키마에 맞춰 데이터 추출 (LLM)
3. JSON 포맷으로 변환

**출력:**
- extracted_data: 스키마에 맞는 JSON 데이터

### 3. Reflection Phase

**입력:**
- extracted_data: 추출된 데이터
- extraction_schema: 원본 스키마
- reflection_count: 현재 반복 횟수

**처리:**
1. 필드 완성도 평가
2. 누락/불완전 필드 식별
3. 후속 검색 쿼리 생성 (LLM)
4. 완료 여부 결정

**출력:**
- missing_fields: 누락된 필드 목록
- follow_up_queries: 추가 검색 쿼리
- is_complete: 완료 여부 (bool)

## 스트리밍 실행

실시간 업데이트를 받으려면:

```python
async for event in graph.astream(initial_state):
    if "research" in event:
        print(f"Research: {len(event['research']['search_results'])} results")
    elif "extract" in event:
        print(f"Extracted: {len(event['extract']['extracted_data'])} fields")
    elif "reflect" in event:
        print(f"Complete: {event['reflect']['is_complete']}")
```

## Claude Code 스킬

이 프로젝트는 Claude Code 스킬로 제공됩니다:

### 1. 기본 멀티에이전트 스킬
`.claude/skills/langgraph-multi-agent/`

기본적인 멀티에이전트 시스템 구축 방법을 제공합니다.

### 2. 딥리서치 스킬
`.claude/skills/deep-research/`

웹 검색 기반 자동 리서치 시스템 구축 방법을 제공합니다.

### 스킬 사용 방법

Claude Code에서 자동으로 인식합니다. 다음과 같이 요청하면:

- "LangGraph로 멀티에이전트 시스템 만들어줘" → 기본 스킬 활성화
- "웹에서 자동으로 정보를 조사하는 에이전트 만들어줘" → 딥리서치 스킬 활성화

## 비용 최적화

1. **쿼리 수 조절**: `max_search_queries`를 3-5로 제한
2. **Reflection 제한**: `max_reflection_steps`를 1-2로 설정
3. **모델 선택**:
   - 쿼리 생성: 저렴한 모델 사용 가능
   - 추출: 고급 모델 권장
4. **결과 캐싱**: 같은 회사 재조사 시 캐시 활용

## 문제 해결

### 빈 추출 결과

- 검색 결과에 관련 정보가 없는지 확인
- 스키마 필드 description을 더 명확하게 수정
- `max_search_queries` 증가

### 무한 Reflection 루프

- `max_reflection_steps` 확인 (권장: 1-2)
- required 필드가 실제로 찾을 수 있는지 검토
- follow-up 쿼리 품질 확인

### API Rate Limit

- 재시도 로직에 exponential backoff 추가
- `max_search_queries` 감소
- 요청 간 지연 추가

## 예제 출력

```json
{
  "company_name": "Anthropic",
  "founded": "2021",
  "headquarters": "San Francisco, CA, USA",
  "industry": "Artificial Intelligence",
  "description": "Anthropic is an AI safety company focused on building reliable, interpretable, and steerable AI systems.",
  "products": [
    "Claude (AI assistant)",
    "Constitutional AI",
    "Claude API"
  ],
  "key_people": [
    {
      "name": "Dario Amodei",
      "role": "CEO"
    },
    {
      "name": "Daniela Amodei",
      "role": "President"
    }
  ],
  "revenue": "Not publicly disclosed",
  "employee_count": "~150-200",
  "website": "https://www.anthropic.com"
}
```

## 참고 자료

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangChain Company Researcher](https://github.com/langchain-ai/company-researcher)
- [Tavily API](https://tavily.com/)
- [LangSmith](https://smith.langchain.com/)

## 라이선스

MIT License
