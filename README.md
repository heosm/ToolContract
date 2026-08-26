# ToolContract

> **AI Agent의 Tool Calling을 자동으로 테스트하는 오픈소스 프레임워크**

ToolContract는 AI Agent에 등록된 **Tool / Function Calling 명세의 품질을 분석하고**, 실제 LLM이 올바른 Tool과 Arguments를 선택하는지 자동으로 테스트합니다.

단순히 JSON Schema가 유효한지만 검사하는 것이 아니라,
**“이 Tool 정의를 실제 AI가 헷갈리지 않고 사용할 수 있는가?”**를 검증하는 것이 목표입니다.

---

## Problem

AI Agent는 외부 API나 기능을 사용하기 위해 Tool Calling(Function Calling)을 활용합니다.

하지만 Tool의 `name`, `description`, `parameters`가 조금만 모호해도 LLM은 다음과 같은 실수를 할 수 있습니다.

* 비슷한 Tool 중 잘못된 Tool 선택
* 필요한 Parameter 누락
* 잘못된 Argument 생성
* Tool 설명이 서로 유사해 호출 결과가 불안정해짐
* 명세 자체는 정상인데 실제 LLM 호출에서는 실패

예를 들어 다음 두 Tool이 있다고 가정합니다.

```text
order_tool_a
- 주문 정보를 처리합니다.

order_tool_b
- 주문 관련 요청을 처리합니다.
```

두 Tool 모두 Schema 자체에는 문제가 없을 수 있습니다.

하지만 사용자가

```text
주문번호 123번을 취소해줘
```

라고 요청했을 때 LLM이 어떤 Tool을 선택할지는 불안정할 수 있습니다.

기존 Schema Validator만으로는 이러한 문제를 발견하기 어렵습니다.

---

## Solution

ToolContract는 Tool Calling 명세를 두 단계로 검사합니다.

### 1. Static Analysis

LLM을 호출하기 전에 Tool 정의 자체의 문제를 검사합니다.

현재 다음과 같은 규칙을 지원합니다.

| Code    | 검사 내용                         |
| ------- | ----------------------------- |
| `TC001` | Tool description 누락           |
| `TC002` | Tool description이 지나치게 짧음     |
| `TC003` | 모호한 표현 사용                     |
| `TC101` | Parameter description 누락      |
| `TC301` | 여러 Tool의 description이 지나치게 유사 |

예:

```bash
toolcontract check examples/tools.json
```

```text
TC002 search_user: description is too short
TC101 search_user.user_id: parameter description is missing
TC301 order_tool_a <-> order_tool_b: descriptions are too similar
```

---

### 2. Behavior Test

Static Analysis에서 발견하기 어려운 문제는 실제 LLM을 호출해 테스트합니다.

ToolContract는 다음 과정을 자동으로 수행합니다.

```text
User Prompt
    ↓
LLM + Tool Definitions
    ↓
Tool Selection
    ↓
Arguments Generation
    ↓
Expected Result Comparison
    ↓
PASS / FAIL
```

예를 들어 기대 결과를 다음과 같이 정의할 수 있습니다.

```text
Prompt:
"사용자 ID 12345를 검색해줘"

Expected Tool:
search_user

Expected Arguments:
{"user_id": "12345"}
```

ToolContract는 실제 모델 호출 결과와 기대값을 비교합니다.

---

## Demo

비슷한 역할을 가진 두 Tool을 테스트한 예시입니다.

```text
Prompt
"주문번호 123번 취소"

Expected
order_tool_b
```

3회 반복 테스트 결과:

```text
Run 1  order_tool_a  FAIL
Run 2  order_tool_b  PASS
Run 3  order_tool_b  PASS

Result: 2 / 3 PASS
```

Schema 자체에는 오류가 없지만, 실제 LLM은 **3번 중 1번 잘못된 Tool을 선택했습니다.**

ToolContract는 이런 **Tool 간 의미적 충돌과 호출 불안정성**을 실제 행동 테스트를 통해 발견합니다.

---

## Architecture

```text
Tool Definitions
      │
      ├───────────────┐
      │               │
      ▼               ▼
Static Analyzer    Behavior Runner
      │               │
      ▼               ▼
 Rule Checks        LLM API
      │               │
      │               ▼
      │            Tool Call
      │               │
      └───────┬───────┘
              ▼
          Evaluator
              │
              ▼
        PASS / FAIL Report
```

프로젝트 구조:

```text
ToolContract/
├── examples/
│   └── tools.json
│
├── src/
│   └── toolcontract/
│       ├── analyzer.py
│       ├── cli.py
│       ├── loader.py
│       │
│       ├── checks/
│       │   ├── description.py
│       │   ├── parameters.py
│       │   ├── schema.py
│       │   └── similarity.py
│       │
│       └── behavior/
│           ├── runner.py
│           └── evaluator.py
│
└── tests/
```

### Core Components

**Analyzer**

Tool Definition을 읽고 정적 분석 규칙을 실행합니다.

**Checks**

Description, Parameter, Schema, Tool 간 유사도 등을 검사합니다.

**Runner**

LLM에 User Prompt와 Tool Definition을 전달하고 실제 Tool Call을 실행합니다.

**Evaluator**

선택된 Tool과 Arguments를 Expected Result와 비교합니다.

---

## Quick Start

### Installation

```bash
git clone https://github.com/heosm/ToolContract.git
cd ToolContract
pip install -e .
```

### Static Analysis

```bash
toolcontract check examples/tools.json
```

또는

```bash
python -m toolcontract.cli check examples/tools.json
```

### Behavior Test

환경 변수에 API Key를 설정합니다.

```env
GROQ_API_KEY=your_api_key
```

Behavior Test를 실행합니다.

```bash
toolcontract test ...
```

ToolContract는 실제 Tool Calling 결과를 실행하고 예상한 Tool 및 Arguments와 비교하여 `PASS / FAIL`을 출력합니다.

---

## Why ToolContract?

기존 Validator가 묻는 질문은 주로 다음과 같습니다.

> **“이 Tool Schema가 올바른가?”**

ToolContract는 한 단계 더 나아가 묻습니다.

> **“AI가 이 Tool을 실제로 올바르게 사용할 수 있는가?”**

ToolContract는 **정적 분석 + 실제 LLM 행동 테스트**를 결합해 AI Agent의 Tool Calling 품질을 개발 단계에서 검증할 수 있도록 합니다.
