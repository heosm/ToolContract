# ToolContract

AI Agent의 Tool 정의 품질을 검사하고,  
실제 LLM이 올바른 Tool을 선택하는지 테스트하는 오픈소스 도구입니다.

## Why ToolContract?

AI Agent의 함수 자체가 정상적으로 동작하더라도,  
Tool description이나 parameter 정의가 모호하면 LLM이 잘못된 Tool을 선택할 수 있습니다.

ToolContract는 이를 두 단계로 검사합니다.

## Quick Start

Install directly from GitHub:

```bash
python -m pip install "git+https://github.com/heosm/ToolContract.git"

Static analysis:

python -m toolcontract.cli check examples/tools.json

Behavior testing:

python -m toolcontract.cli test examples/tools.json --provider groq --model openai/gpt-oss-20b --prompt "사용자 ID 12345의 정보를 찾아줘." --expected-tool search_user --expected-args user_id=12345 --repeats 3

Behavior suite:

python -m toolcontract.cli suite examples/tools.json examples/behavior_tests.json --provider groq --model openai/gpt-oss-20b

3. **그 다음 GitHub Actions**
   
이걸 붙이면 GitHub에 push할 때마다 ToolContract가 깨졌는지 자동 검사할 수 있어.

4. **그 다음 `v0.1.0` GitHub Release 만들기**

그러면 GitHub 들어온 사람이:

```text
ToolContract v0.1.0

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

개발 및 테스트까지 사용하려면:

python -m pip install -e ".[dev]"
Static Analysis

Static Analysis는 API Key가 필요하지 않습니다.

python -m toolcontract.cli check examples/tools.json

Example:

===== ToolContract Static Analysis =====

검사한 Tool 수: 3
발견된 문제 수: 5

TC003 search_order
TC101 search_order
TC003 cancel_order
TC101 cancel_order
TC301 search_order ↔ cancel_order
Behavior Test

Behavior Test는 사용자가 실제 Agent에서 사용하는
LLM Provider의 API Key를 사용합니다.

프로젝트 루트에 .env 파일을 생성합니다.

OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=

사용하는 Provider의 API Key만 입력하면 됩니다.

Groq
python -m toolcontract.cli test examples/tools.json \
  --provider groq \
  --model openai/gpt-oss-20b \
  --prompt "사용자 ID 12345의 정보를 찾아줘." \
  --expected-tool search_user \
  --expected-args user_id=12345 \
  --repeats 3

PowerShell에서는 한 줄로 실행할 수 있습니다.

python -m toolcontract.cli test examples/tools.json --provider groq --model openai/gpt-oss-20b --prompt "사용자 ID 12345의 정보를 찾아줘." --expected-tool search_user --expected-args user_id=12345 --repeats 3
OpenAI
python -m toolcontract.cli test examples/tools.json \
  --provider openai \
  --model YOUR_MODEL \
  --prompt "사용자 ID 12345의 정보를 찾아줘." \
  --expected-tool search_user \
  --expected-args user_id=12345 \
  --repeats 3
Gemini
python -m toolcontract.cli test examples/tools.json \
  --provider gemini \
  --model YOUR_MODEL \
  --prompt "사용자 ID 12345의 정보를 찾아줘." \
  --expected-tool search_user \
  --expected-args user_id=12345 \
  --repeats 3
Static + Behavior Test

두 검사를 한 번에 실행할 수도 있습니다.

python -m toolcontract.cli run examples/tools.json \
  --provider groq \
  --model openai/gpt-oss-20b \
  --prompt "사용자 ID 12345의 정보를 찾아줘." \
  --expected-tool search_user \
  --expected-args user_id=12345 \
  --repeats 3
Supported Tool Formats

ToolContract는 현재 MCP-style과 OpenAI Function Calling-style Tool 정의를 지원합니다.

파일 이름은 tools.json일 필요가 없습니다.

MCP-style
[
  {
    "name": "cancel_order",
    "description": "주문을 취소합니다.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "order_id": {
          "type": "string",
          "description": "취소할 주문 ID"
        }
      }
    }
  }
]
OpenAI Function Calling-style
[
  {
    "type": "function",
    "function": {
      "name": "cancel_order",
      "description": "주문을 취소합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "order_id": {
            "type": "string",
            "description": "취소할 주문 ID"
          }
        }
      }
    }
  }
]
Static Analysis Rules
Rule	Description
TC001	Tool description 없음
TC002	Tool description이 지나치게 짧음
TC003	모호한 표현 포함
TC101	Parameter description 없음
TC201	inputSchema 없음
TC202	Schema type이 object가 아님
TC203	properties 없음
TC301	Tool description 간 유사도가 지나치게 높음
Development

테스트 실행:

python -m pytest
Roadmap
Multiple behavior test cases
Tool confusion report
MCP Server direct import
Python / LangChain adapter
CI Quality Gate
Web interface
License

MIT


붙여넣고 `Ctrl + S` 한 다음 터미널에서:

```powershell
git add README.md
git commit -m "Update README for public usage"
git push

# Behavior Suite

여러 Prompt를 한 번에 테스트할 수 있습니다.

예제:

```bash
python -m toolcontract.cli suite \
  examples/tools.json \
  examples/behavior_tests.json \
  --provider groq \
  --model openai/gpt-oss-20b