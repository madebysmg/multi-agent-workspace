# Claude Code References

> 공식 레퍼런스 문서들 - Claude Code vibe coding을 위한 컨텍스트

이 디렉토리는 **멀티 에이전트 개발에 필요한 공식 레퍼런스 문서들**의 사본을 포함합니다.
Claude Code가 프로젝트 컨텍스트로 참조하여 정확한 코드를 생성할 수 있도록 최적화되었습니다.

> 이 디렉토리의 레퍼런스 파일은 제3자 문서의 사본이며 각 원본 저장소의 라이선스를 따릅니다. 아래 [출처 및 라이선스](#-출처-및-라이선스)를 참고하세요.

---

## 📚 포함된 레퍼런스

### Google Agent Development Kit (ADK)

| 파일 | 크기 | 용도 | 언제 읽을까? |
|------|------|------|------------|
| `google-adk-llms.txt` | 40KB | 요약본 (토큰 효율적) | ⭐ **기본 참조** - 빠른 조회, 개념 확인 |
| `llms-full.txt` (미포함) | 약 3MB | 전체 레퍼런스 | 상세 구현, 고급 기능, 전체 API — 용량 때문에 포함하지 않음. [google/adk-docs](https://github.com/google/adk-docs/blob/main/llms-full.txt)에서 받아 사용 |

**포함 내용:**
- ADK 핵심 개념 (Agent, Tool, Session)
- Agent 아키텍처 (LLM-driven, Workflow-based)
- Multi-agent 시스템 패턴 (Coordinator/Dispatcher)
- Tool 생태계 (Built-in, Third-party, Custom)
- Context & State 관리
- Streaming 처리
- Deployment 전략
- Evaluation & Safety

**추천 시나리오:**
```
Q: "Google ADK로 에이전트 만들 때 Tool 어떻게 정의하지?"
→ google-adk-llms.txt 참조 (빠른 답변)

Q: "Multi-agent coordinator 패턴 전체 구현 예제는?"
→ adk-docs의 llms-full.txt 참조 (상세 가이드, 별도 다운로드)
```

---

### LangGraph (LangChain)

| 파일 | 크기 | 용도 | 언제 읽을까? |
|------|------|------|------------|
| `langgraph-README.md` | 6KB | 빠른 시작 가이드 | ⭐ **첫 시작** - 설치, 기본 예제 |
| `langgraph-agentic-concepts.md` | 9KB | Agent 핵심 개념 | Agent 패턴, Reasoning, Memory |
| `langgraph-multi-agent.md` | 35KB | Multi-agent 시스템 | ⭐ **필수** - 멀티 에이전트 아키텍처 |
| `langgraph-concepts-low-level.md` | 45KB | 저수준 API 상세 | 고급 커스터마이징, 그래프 제어 |
| `langgraph-CONTRIBUTING.md` | 15KB | 기여 가이드 | LangGraph 내부 구조 이해 |

**포함 내용:**
- StateGraph, MessageGraph
- Multi-agent 아키텍처 (Network, Supervisor, Hierarchical)
- Agent 커뮤니케이션 (Handoffs, Command)
- Checkpointing & Persistence
- Human-in-the-loop
- Streaming

**추천 시나리오:**
```
Q: "LangGraph로 간단한 ReAct 에이전트 만들려면?"
→ langgraph-README.md 참조 (Quick start)

Q: "여러 에이전트가 협업하는 시스템 구조는?"
→ langgraph-multi-agent.md 참조 (5가지 아키텍처)

Q: "StateGraph에서 conditional edge 어떻게?"
→ langgraph-concepts-low-level.md 참조 (API 상세)
```

---

## 🎯 빠른 참조 가이드

### 상황별 추천 문서

#### 🚀 "처음 시작할 때"
1. `langgraph-README.md` - LangGraph 기본 개념
2. `google-adk-llms.txt` - ADK 개요

#### 🤖 "단일 에이전트 만들 때"
1. `langgraph-README.md` - ReAct agent 예제
2. `langgraph-agentic-concepts.md` - Agent 패턴
3. `google-adk-llms.txt` - Tool 정의 방법

#### 👥 "멀티 에이전트 시스템 만들 때" ⭐
1. **`langgraph-multi-agent.md`** - 5가지 아키텍처 (필수!)
2. `google-adk-llms.txt` - Coordinator/Dispatcher 패턴
3. `langgraph-concepts-low-level.md` - State 공유, Handoff

#### 🔧 "고급 기능/커스터마이징"
1. `langgraph-concepts-low-level.md` - 저수준 API
2. adk-docs `llms-full.txt` - 전체 레퍼런스 (별도 다운로드)
3. `langgraph-CONTRIBUTING.md` - 내부 구조

#### 🐛 "디버깅/문제 해결"
1. `langgraph-CONTRIBUTING.md` - 아키텍처 이해
2. adk-docs `llms-full.txt` - 전체 API 검색 (별도 다운로드)

---

## 💡 사용 팁

### 1. **Claude Code에게 명시적으로 요청**
```
"langgraph-multi-agent.md 참고해서 Supervisor 패턴으로 구현해줘"
"google-adk-llms.txt에서 Tool 정의 방법 찾아서 적용해줘"
```

### 2. **컨텍스트 크기 고려**
- 빠른 조회: 요약본 우선 (`google-adk-llms.txt`, `langgraph-README.md`)
- 상세 구현: 전체본 (`langgraph-multi-agent.md`, 필요 시 adk-docs `llms-full.txt`)

### 3. **검색 활용**
```bash
# 특정 개념 빠르게 찾기
grep -r "StateGraph" .claude/references/
grep -r "multi-agent" .claude/references/
```

---

## 📦 파일 관리

### 업데이트 정책
- **수동 업데이트**: 필요시 최신 버전 다운로드
- **버전 고정**: 프로젝트 안정성 우선
- **주기**: 분기별 또는 major release 시

### 용량 관리
- 포함된 파일 전체 크기: 약 160KB
- Google ADK 전체본(`llms-full.txt`, 약 3MB)은 저장소에 포함하지 않음

---

## 🔗 출처 및 라이선스

| 파일 | 원본 | 라이선스 |
|------|------|----------|
| `google-adk-llms.txt` | [google/adk-docs](https://github.com/google/adk-docs) `llms.txt` | Apache License 2.0 — [licenses/google-adk-docs-Apache-2.0.txt](licenses/google-adk-docs-Apache-2.0.txt) |
| `langgraph-*.md` | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) (README, CONTRIBUTING, 개념 문서) | MIT License, Copyright (c) 2024 LangChain, Inc. — [licenses/langgraph-MIT.txt](licenses/langgraph-MIT.txt) |

사본은 2025-10 시점에 가져온 것이므로 최신 내용은 원본 저장소에서 확인하세요.

**최종 업데이트**: 2025-10-23
**대상**: Claude Code vibe coding 개발자

---

## 📖 다음 단계

1. **Workspace 가이드**: `../../README.md` - 프로젝트 전체 구조
2. **스킬 활용**: `../skills/` - Claude Code 스킬 컬렉션
3. **에이전트 구현**: `../../src/agents/` - 실제 구현 예제
4. **사용 예제**: `../../examples/` - 실행 가능한 샘플

**Happy vibe coding! 🚀**
