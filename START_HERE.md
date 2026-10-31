# 새 세션의 시작점

먼저 현재가 **사전 준비 / 과제 수행 / 실제 후속 서술형** 중 어디인지 확인한다. 실제 후속 서술형이면 AI 사용을 중단하고 본인이 답한다. 작업이 이미 진행 중이면 인수인계 기록과 실제 파일·테스트 결과를 비교한다.

## 최소 로드 순서

1. 과제 README, 기존 AGENTS.md, 제출 요구사항을 읽는다.
2. `task-intake`로 반드시 충족할 조건·미확인 사항을 추린다.
3. 아래에서 필요한 스킬 하나를 고른다. 구현 후 `verify-behavior`, 제출 전 `submission-audit`를 사용한다.
4. 기능·판단이 바뀔 때만 기록을 갱신한다. 출력마다 모든 양식을 다시 만들지 않는다.

| 상황 / 사용자 표현 | 읽을 스킬 | 기대 결과 |
|---|---|---|
| "뭘 만들라는 건지 정리해줘" | [task-intake](.agents/skills/task-intake/SKILL.md) | 필수조건과 검증 기준 |
| "핵심 흐름부터 구현해줘" | [web-mvp](.agents/skills/web-mvp/SKILL.md) | 실제 입력→처리→출력 경로 |
| "CSV·집계 결과가 맞는지 봐줘" | [data-audit](.agents/skills/data-audit/SKILL.md) | 데이터 품질·단위·기준 검증 |
| "오류가 반복돼" | [debug-root-cause](.agents/skills/debug-root-cause/SKILL.md) | 재현과 원인을 연결한 수정 |
| "제대로 동작하는지 확인해줘" | [verify-behavior](.agents/skills/verify-behavior/SKILL.md) | 요구사항별 관찰 결과 |
| "변경을 리뷰해줘" | [code-review](.agents/skills/code-review/SKILL.md) | 영향 있는 결함과 재현 조건 |
| "결정과 AI 활용 기록을 남겨줘" | [evidence-log](.agents/skills/evidence-log/SKILL.md) | 실제 근거를 연결한 기록 |
| "병렬로 나눠 작업해줘" | [parallel-work](.agents/skills/parallel-work/SKILL.md) | 파일 소유권·검증·통합 계획 |
| "표·보고서·PDF로 정리해줘" | [artifact-authoring](.agents/skills/artifact-authoring/SKILL.md) | 형식 요구에 맞는 문서 |
| "이 세션 이어받게 정리해줘" | [session-handoff](.agents/skills/session-handoff/SKILL.md) | 현재 상태와 바로 할 다음 행동 |
| "제출 직전 점검해줘" | [submission-audit](.agents/skills/submission-audit/SKILL.md) | 누락·오류·미확인 항목 |
| "시험 전에 설명 연습하자" | [explanation-rehearsal](.agents/skills/explanation-rehearsal/SKILL.md) | 사실에 근거한 자기 설명 연습 |

## 읽기를 멈추고 구현할 때

필수 기능 하나의 입력·출력·검증 방법을 말할 수 있으면 그 경로를 먼저 만든다. 참고 문서 수집을 계속할 필요는 없다. 아직 기술 선택이 불확실하면 제공 프로젝트의 기존 스택을 우선 활용한다. 제출 직전에는 새 프레임워크 도입보다 핵심 흐름·저장·재현 가능성을 점검한다.

## 상황별 문서

- 웹 UI·API: [웹 플레이북](docs/web-playbook.md)
- CSV·분석·추천·모델: [데이터 플레이북](docs/data-playbook.md)
- 서버·권한·시간 부족: [장애 대응](docs/troubleshooting.md)
- 바로 사용할 요청문: [프롬프트](docs/prompts.md)
- 규정과 추정 구분: [근거](docs/rules-and-assumptions.md)
- 도구 실행: [하네스](docs/harness.md)
