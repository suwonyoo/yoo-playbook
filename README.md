# Codex Hackathon Playbook

**과제 파악 → 구현 → 직접 확인 → 판단·검증 기록 → 제출 점검**을 돕는 한국어 사전 준비 도구입니다. 새 Codex 세션도 [START_HERE.md](START_HERE.md)부터 필요한 절차만 선택할 수 있습니다.

SK하이닉스 AI 해커톤 2026 준비를 위해 만들었습니다. 공식 제공·승인 자료가 아니며, 실제 문제의 정답·완성 서비스·제출물을 포함하지 않습니다. 규정 해석과 준비 가정은 [근거와 적용 범위](docs/rules-and-assumptions.md)에 구분했습니다. 검토 기준일: **2026-10-31**.

## 바로 읽기

- [스킬 선택표](START_HERE.md) · [명령과 도구 사용법](docs/harness.md) · [공개 자료 선별 결과](docs/source-selection.md)
- [웹 과제](docs/web-playbook.md) · [데이터 과제](docs/data-playbook.md) · [장애 대응](docs/troubleshooting.md) · [프롬프트 모음](docs/prompts.md)

## 제공 환경에서 가져오기

실제 응시 안내에서 공개 자료 다운로드가 허용될 때, 제공된 터미널과 Codex를 사용합니다. 개인 PC의 파일을 업로드하는 방식이 아닙니다. 실행 위치는 실제 과제 폴더로 바꾸세요.

```bash
git clone https://github.com/suwonyoo/codex-hackathon-playbook.git /tmp/codex-hackathon-playbook
python3 /tmp/codex-hackathon-playbook/scripts/playbook.py doctor --workspace .
python3 /tmp/codex-hackathon-playbook/scripts/playbook.py init --workspace .
```

그다음 Codex에 다음과 같이 지시합니다.

> 과제 README와 현재 AGENTS.md를 먼저 읽고, .playbook/START.md를 참고해 필요한 스킬만 사용해줘. 필수 기능·제출물·검증 기준을 정리하고, 가장 중요한 사용자 흐름 하나부터 구현해줘. 확인된 사실과 가정을 구분하고 검증 결과를 남겨줘.

`init`은 `.playbook/`에 기록 양식과 참고 문서를 만듭니다. 과제의 `README.md`와 `AGENTS.md`는 변경하지 않습니다. 자동 스킬 탐색이 필요하면 선택한 것만 추가합니다.

```bash
python3 /tmp/codex-hackathon-playbook/scripts/playbook.py init --workspace . --skills task-intake verify-behavior debug-root-cause
```

자동 탐색이 안 되면 `.playbook/skills/<name>/SKILL.md`를 직접 읽도록 요청하세요. 제공 환경의 Codex 버전·메뉴·설정 권한은 이 준비 환경과 다를 수 있습니다.

## 들어 있는 것

| 구성 | 역할 |
|---|---|
| `.agents/skills/` | 상황별로 선택하는 12개 독립 스킬 |
| `templates/` | 요구사항·의사결정·협업·검증·한계·인수인계 기록 |
| `scripts/playbook.py` | 초기화, 환경 확인, 명령 결과 저장, 필수 파일·증거 점검 |
| `docs/` | 과제 유형별 가이드와 프롬프트, 규정 근거 |
| `sources/catalog.json` | 검토한 공개 저장소의 고정 커밋과 사용 방식 |
| `examples/` | 실제 시험과 무관한 연습용 예시·평가 시나리오 |

실행 하네스는 자체적으로 네트워크 요청을 하지 않습니다. `run`은 사용자가 지정한 명령을 실행하므로 그 명령의 외부 접속까지 차단하는 샌드박스는 아닙니다. 로그는 지정 작업 공간에만 저장됩니다.

## 검증

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repo.py
```

기본 도구는 Python 3.10+만 필요합니다. 테스트 범위·한계는 [검증 기록](docs/validation.md)에 남깁니다.

## 공개 상태 유지

제공받은 추가 공지에 따라 이 준비 저장소는 **2차 예선 결과 통지 전까지 공개 상태를 유지**합니다. 시험 중 생성한 문제·데이터·코드·협업 기록을 이 저장소로 push하지 않습니다. 실제 후속 서술형 단계에는 AI 사용과 복사·붙여넣기가 금지되므로, 설명 연습 스킬은 사전 준비에만 사용합니다.
