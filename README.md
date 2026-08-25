# ToolContract

AI Agent의 Tool 정의 품질을 검사하고,
실제 LLM이 올바른 Tool을 선택하는지 테스트하는 오픈소스 도구입니다.

## Why ToolContract?

AI Agent의 함수 자체가 정상적으로 동작하더라도,
Tool description이나 parameter 정의가 모호하면 LLM이 잘못된 Tool을 선택할 수 있습니다.

ToolContract는 이를 두 단계로 검사합니다.

### 1. Static Analysis

API 호출 없이 Tool 명세 자체를 검사합니다.

- 누락된 description
- 지나치게 짧은 description
- 모호한 표현
- parameter description 누락
- 잘못된 input schema
- 서로 지나치게 유사한 Tool

### 2. Behavior Test

실제 LLM에게 Prompt를 전달하고
예상한 Tool과 arguments를 선택하는지 반복 테스트합니다.

Supported Providers:

- OpenAI
- Gemini
- Groq

---

# Installation

```bash
git clone https://github.com/heosm/ToolContract.git
cd ToolContract

python -m pip install -e .