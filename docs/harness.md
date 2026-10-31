# 로컬 도구 사용법

Python 3.10+ 표준 라이브러리만 필요하다. 명령은 실제 과제 작업 폴더에서 실행한다. 아래 `/tmp/codex-hackathon-playbook`은 공개 저장소를 clone한 위치다.

## 초기화와 환경 확인

```bash
python3 /tmp/codex-hackathon-playbook/scripts/playbook.py doctor --workspace .
python3 /tmp/codex-hackathon-playbook/scripts/playbook.py init --workspace .
```

`doctor`는 도구 존재 여부와 프로젝트 파일명만 출력한다. 인증 파일·환경 변수·토큰·다른 사용자의 프로세스를 읽지 않는다. `init`은 `.playbook/`에 양식과 참고 자료를 복사한다. 기존 내용은 그대로 둔다. 새 버전을 가져와도 기존 복사본은 자동 갱신되지 않으므로 필요하면 차이를 검토해 수동 반영한다.

선택 스킬을 자동 탐색 위치에도 복사하려면 `init --skills task-intake verify-behavior`를 사용한다. `.playbook/skills/`의 직접 읽기 방식은 설정 변경 없이 가능하다. `AGENTS.md`를 자동 병합하거나 홈 디렉터리 설정을 바꾸지 않는다.

## 실행 결과 기록

```bash
python3 /tmp/codex-hackathon-playbook/scripts/playbook.py run \
  --workspace . --id V-001 --requirement R-001 --timeout 90 \
  --track src/calculate.py --track tests/test_calculate.py \
  -- python3 -m unittest discover -s tests -v
```

예시 파일명이므로 실제 프로젝트에 맞게 바꾼다. `--` 뒤 명령을 셸 해석 없이 실행한다. `&&`, 파이프, 리다이렉션이 필요하면 명령을 나누거나 검토된 스크립트를 실행한다. 이미 사용한 검증 ID는 덮어쓰지 않는다. 재검증은 V-002처럼 새 ID로 남긴다.

결과는 `.playbook/runs/V-001/result.json`과 `output.log`에 남는다. 명령·시각·종료 코드·시간 초과 여부·추적 파일 및 로그 SHA-256을 기록한다. 시간 초과는 124, 실행 실패는 125, 중단은 130으로 보고한다. POSIX에서는 이 도구가 시작한 프로세스 그룹만 종료한다. 제한 시간 안에 끝나는 테스트·빌드 명령에 사용하며 개발 서버는 별도 터미널에 유지한다.

`--track`은 검증 결과에 영향을 주는 소스·테스트·설정·입력 파일을 반복 지정한다. 목록 밖의 변경은 탐지하지 못한다. 출력과 명령 인자는 그대로 저장하므로 비밀번호·토큰을 인자로 넘기거나 출력하지 않는다. 로그를 자동 비식별화한다고 보장하지 않는다. 도구는 지정 명령의 네트워크 동작을 막는 샌드박스가 아니다.

## 필수 파일과 증거 대조

`.playbook/manifest.json`을 실제 과제에 맞게 작성한다.

```json
{
  "required_files": ["README.md", "src/calculate.py"],
  "checks": [
    {
      "requirement": "R-001",
      "run_id": "V-001",
      "assertion": "계산의 정상·0분모 사례가 기대값과 일치한다"
    }
  ]
}
```

```bash
python3 /tmp/codex-hackathon-playbook/scripts/playbook.py audit --workspace .
```

빈 필수 목록, 없는 파일, 실패한 명령, 시간 초과, 바뀐 추적 파일·로그는 통과하지 않는다. `RECORDED_CHECKS_OK`는 등록한 기록의 정합성을 뜻한다. 단순 `print` 명령도 종료 0이 될 수 있으므로 assertion을 증명하는 테스트인지 사람이 읽어야 한다. 전체 요구사항 충족, 보안 검증, 데이터 정확성, 공식 제출 완료를 자동 인증하지 않는다. 수동 화면 확인은 `verification.md`에 별도로 기록한다.
