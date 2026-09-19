# 새 에이전트 만들기

> Step-by-step 가이드 - LangGraph 멀티 에이전트 시스템 개발

---

## 🎯 개요

이 가이드는 Multi-Agent Workspace에서 새로운 에이전트를 만드는 방법을 설명합니다.

---

## 📋 전제 조건

- Multi-Agent Workspace 환경 설정 완료
- [Getting Started](GETTING_STARTED.md) 읽음
- 기본 Python 지식
- LangGraph 기본 개념 이해 (선택)

---

## 🚀 방법 1: Claude Code 활용 (추천)

### 단계 1: 레퍼런스 확인

```bash
# 멀티 에이전트 아키텍처 학습
cat .claude/references/langgraph-multi-agent.md

# 5가지 아키텍처:
# 1. Network - 에이전트 간 자유로운 통신
# 2. Supervisor - 중앙 관리자가 작업 분배
# 3. Supervisor (Tool-Calling) - 에이전트를 Tool로 노출
# 4. Hierarchical - 팀별 관리자 + 최상위 관리자
# 5. Custom Workflow - 사전 정의된 순서
```

### 단계 2: Claude에게 명확히 요청

```
"langgraph-multi-agent.md의 Supervisor 패턴을 참고해서
 다음 에이전트 시스템을 만들어줘:

 목적: 고객 지원 자동화
 에이전트:
 - TriageAgent: 문의 분류
 - TechnicalAgent: 기술 문의 처리
 - BillingAgent: 결제 문의 처리
 - EscalationAgent: 에스컬레이션 처리

 디렉토리: src/agents/customer_support/
 파일 구조: company_research 예제 참고"
```

### 단계 3: 생성된 코드 검토

```bash
tree src/agents/customer_support/

# 예상 구조:
# src/agents/customer_support/
# ├── __init__.py
# ├── configuration.py
# ├── state.py
# ├── graph.py
# ├── agents/
# │   ├── triage.py
# │   ├── technical.py
# │   ├── billing.py
# │   └── escalation.py
# └── prompts.py
```

### 단계 4: 테스트 및 개선

```python
# examples/customer_support_example.py 생성
from src.agents.customer_support import Configuration, build_support_graph

async def main():
    config = Configuration()
    graph = build_support_graph(config)

    result = await graph.ainvoke({
        "customer_query": "결제가 안 돼요",
        "messages": []
    })

    print(result)
```

---

## 🛠️ 방법 2: 수동 구현

### 단계 1: 디렉토리 구조 생성

```bash
mkdir -p src/agents/my_agent
cd src/agents/my_agent

# 필수 파일들
touch __init__.py
touch configuration.py
touch state.py
touch graph.py
touch prompts.py
```

### 단계 2: State 정의 (`state.py`)

```python
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage

class MyAgentState(MessagesState):
    """에이전트 상태 정의"""

    # 입력
    user_input: str

    # 중간 상태
    processed_data: dict
    current_step: str

    # 출력
    final_result: str
    is_complete: bool

# 기본 스키마 (필요시)
DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        "result": {"type": "string"},
        "confidence": {"type": "number"}
    }
}
```

### 단계 3: Configuration (`configuration.py`)

```python
from dataclasses import dataclass

@dataclass
class Configuration:
    """에이전트 설정"""

    # LLM 설정
    llm_model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.7

    # 에이전트 설정
    max_iterations: int = 5
    timeout_seconds: int = 60

    # API 설정
    api_key: str = None  # 환경 변수에서 로드
```

### 단계 3: Graph 구축 (`graph.py`)

```python
from langgraph.graph import StateGraph, END
from .state import MyAgentState
from .configuration import Configuration

def build_my_agent_graph(config: Configuration):
    """에이전트 그래프 생성"""

    # 그래프 초기화
    workflow = StateGraph(MyAgentState)

    # 노드 추가
    workflow.add_node("process", process_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("finalize", finalize_node)

    # 엣지 추가
    workflow.set_entry_point("process")
    workflow.add_edge("process", "validate")
    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {
            "continue": "process",  # 재시도
            "finalize": "finalize"
        }
    )
    workflow.add_edge("finalize", END)

    # 컴파일
    return workflow.compile()


def process_node(state: MyAgentState) -> MyAgentState:
    """처리 노드"""
    # TODO: 구현
    return state


def validate_node(state: MyAgentState) -> MyAgentState:
    """검증 노드"""
    # TODO: 구현
    return state


def finalize_node(state: MyAgentState) -> MyAgentState:
    """완료 노드"""
    state["is_complete"] = True
    return state


def should_continue(state: MyAgentState) -> str:
    """계속할지 결정"""
    if state.get("is_valid"):
        return "finalize"
    elif state["iteration_count"] < 3:
        return "continue"
    else:
        return "finalize"
```

### 단계 4: Prompts (`prompts.py`)

```python
SYSTEM_PROMPT = """You are a helpful AI assistant for {task}.

Your goals:
- {goal_1}
- {goal_2}

Guidelines:
- {guideline_1}
- {guideline_2}
"""

PROCESS_PROMPT = """Process the following input:

Input: {user_input}

Output format: {output_format}
"""

VALIDATE_PROMPT = """Validate the following result:

Result: {result}

Is this valid? Respond with YES or NO and explain.
"""
```

### 단계 5: Init 파일 (`__init__.py`)

```python
"""
My Custom Agent
"""
from .configuration import Configuration
from .state import MyAgentState, DEFAULT_SCHEMA
from .graph import build_my_agent_graph

__all__ = [
    "Configuration",
    "MyAgentState",
    "DEFAULT_SCHEMA",
    "build_my_agent_graph",
]
```

### 단계 6: 예제 작성 (`examples/my_agent_example.py`)

```python
import asyncio
from src.agents.my_agent import Configuration, build_my_agent_graph

async def main():
    # 설정
    config = Configuration(
        max_iterations=3
    )

    # 그래프 생성
    graph = build_my_agent_graph(config)

    # 실행
    result = await graph.ainvoke({
        "user_input": "test input",
        "processed_data": {},
        "current_step": "start",
        "final_result": "",
        "is_complete": False,
        "messages": []
    })

    print("Result:", result["final_result"])
    print("Complete:", result["is_complete"])

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 멀티 에이전트 패턴 선택 가이드

### Supervisor 패턴 (가장 일반적)

**언제 사용**:
- 중앙 조정이 필요한 경우
- 에이전트 간 명확한 역할 분담
- 작업 우선순위 관리 필요

**예제**: Customer Support, Task Management

```python
# Supervisor가 작업 분배
supervisor -> triage_agent
supervisor -> technical_agent
supervisor -> billing_agent
```

### Network 패턴

**언제 사용**:
- 에이전트 간 자유로운 협업
- 동적인 워크플로우
- Peer-to-peer 통신

**예제**: Research Team, Creative Brainstorming

```python
# 에이전트들이 서로 직접 통신
researcher <-> analyst <-> writer
```

### Hierarchical 패턴

**언제 사용**:
- 대규모 조직 구조
- 여러 팀 관리
- 복잡한 계층 구조

**예제**: Enterprise System, Department Management

```python
# 계층적 구조
ceo_agent
  -> sales_supervisor -> [sales_agent_1, sales_agent_2]
  -> tech_supervisor -> [dev_agent_1, qa_agent]
```

### Custom Workflow 패턴

**언제 사용**:
- 사전 정의된 순서가 명확
- 파이프라인 처리
- 단계별 검증 필요

**예제**: Data Pipeline, Document Processing

```python
# 순차적 워크플로우
ingestion -> validation -> transformation -> output
```

---

## 💡 베스트 프랙티스

### 1. 명확한 State 정의

```python
# ✅ 좋은 예
class MyState(MessagesState):
    input_text: str  # 명확한 타입
    processing_step: str  # 현재 단계 추적
    result: dict  # 결과 저장
    error: str | None  # 에러 처리

# ❌ 나쁜 예
class MyState(MessagesState):
    data: dict  # 너무 모호함
    stuff: any  # 타입 불명확
```

### 2. 작은 노드로 분리

```python
# ✅ 좋은 예
workflow.add_node("fetch_data", fetch_data_node)
workflow.add_node("process_data", process_data_node)
workflow.add_node("validate_data", validate_data_node)

# ❌ 나쁜 예
workflow.add_node("do_everything", do_everything_node)
```

### 3. 에러 처리

```python
def my_node(state: MyState) -> MyState:
    try:
        # 작업 수행
        result = perform_task(state)
        state["result"] = result
    except Exception as e:
        state["error"] = str(e)
        state["is_complete"] = True  # 에러 시 중단

    return state
```

### 4. 프롬프트 중앙화

```python
# prompts.py에 모든 프롬프트 정리
from .prompts import SYSTEM_PROMPT, TASK_PROMPT

# graph.py에서 사용
def my_node(state):
    prompt = TASK_PROMPT.format(
        input=state["input"],
        context=state["context"]
    )
    # ...
```

---

## 📚 참고 자료

### 공식 레퍼런스

- [LangGraph Multi-Agent](../.claude/references/langgraph-multi-agent.md)
- [Google ADK Patterns](../.claude/references/google-adk-llms.txt)
- [LangGraph Low-Level API](../.claude/references/langgraph-concepts-low-level.md)

### 예제 코드

- [Company Research Agent](../src/agents/company_research/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)

### 스킬 활용

```bash
/skill langgraph-multi-agent  # 대화형 에이전트 생성
# 새 스킬 만들기: https://github.com/anthropics/skills 의 skill-creator 참고 (이 저장소에는 미포함)
```

---

## 🎓 다음 단계

에이전트를 만들었다면:

1. **문서화**
   ```bash
   mkdir -p docs/agents/my_agent
   # docs/agents/my_agent/README.md 작성
   ```

2. **테스트**
   ```bash
   PYTHONPATH=. python examples/my_agent_example.py
   ```

3. **Git 커밋**
   ```bash
   git add src/agents/my_agent/
   git commit -m "Add: My custom agent"
   ```

4. **공유**
   - PR 생성
   - 팀에 공유
   - 문서 업데이트

---

**Happy building! 🚀**

[← Getting Started](GETTING_STARTED.md) | [스킬 활용](../.claude/SKILLS_COLLECTION.md)
