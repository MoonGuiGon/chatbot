# 테스트 모드 사용 가이드

## 개요
실제 DB(MongoDB, pgvector)와 사내 LLM에 연결하지 않고도 개발 및 테스트를 할 수 있는 Mock 시스템입니다.

## 테스트 모드 활성화

### 1. `.env` 파일 설정
```bash
# 테스트 모드 활성화
TEST_MODE=True
```

### 2. 자동 Mock 적용
테스트 모드가 활성화되면:
- ✅ MongoDB → Mock MongoDB (메모리 내 데이터)
- ✅ pgvector → Mock pgvector (메모리 내 벡터 검색)
- ✅ 사내 LLM → Mock LLM (시뮬레이션 응답)

## Mock 데이터

### Mock MongoDB 초기 데이터
```python
# 부품 정보 (parts collection)
- ABC-12345: 반도체 칩 A (재고 1000개)
- ABC-12346: 반도체 칩 B (재고 500개)
- ABC-12347: 반도체 칩 C (재고 200개)

# 각 부품은 다음 정보 포함:
- 재고 현황 (총 재고, 가용, 예약)
- 출고 이력
- 장착 정보
- 검사 데이터
```

### Mock pgvector 초기 데이터
```python
# 문서 청크 (document_chunks table)
1. 부품_매뉴얼_ABC12345.pdf (2개 청크)
   - 기본 사양
   - 전기적 특성

2. 재고_관리_지침.docx (1개 청크)
   - 재고 관리 규정

3. 검사_절차.pdf (1개 청크)
   - 입고 검사 절차
```

### Mock LLM 응답
```python
# Chat LLM
- 쿼리 분류: JSON 형식 응답
- 부품 관련 질문: 재고/출고 정보 답변
- 표/그래프 요청: 구조화된 데이터 + 그래프 JSON

# Embedding LLM
- 텍스트 → 1536차원 벡터 (일관된 해시 기반)

# Vision LLM
- 이미지 → 표/그래프/다이어그램 분석 결과
```

## 테스트 모드 해제

### 실제 환경으로 전환
```bash
# .env 파일
TEST_MODE=False

# 실제 DB/LLM 설정 입력
LLM_API_KEY=your-real-api-key
MONGODB_URI=mongodb://real-server:27017/
POSTGRES_HOST=real-postgres-server
```

## Mock 시스템 제거 방법

테스트가 끝나면 `tests/` 폴더 전체를 삭제하면 됩니다:

```bash
# Mock 시스템 완전 제거
rm -rf backend/tests/
```

그리고 코드에서 Mock import 부분만 제거:
```python
# backend/app/services/llm_service.py
# backend/app/services/database_service.py

# 다음 부분 삭제:
if config.test_mode:
    from tests.mocks import ...
    return Mock...
```

## 주의사항

1. **테스트 모드는 개발/테스트 용도만 사용**
   - 실제 운영 환경에서는 반드시 `TEST_MODE=False`

2. **Mock 데이터는 메모리에만 저장**
   - 서버 재시작 시 초기 데이터로 리셋됨

3. **Mock LLM 응답은 제한적**
   - 기본적인 시나리오만 커버
   - 복잡한 질문은 단순 응답 반환

## 테스트 실행 예제

```bash
# 1. 테스트 모드 활성화
echo "TEST_MODE=True" > .env

# 2. 서버 실행
python backend/run.py

# 3. API 테스트
curl http://localhost:5000/api/chat \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "부품 ABC-12345의 재고는?"}'

# 예상 응답: Mock 데이터 기반 답변
```

## FAQ

**Q: Mock과 실제 코드가 호환되나요?**
A: 네, 인터페이스가 동일하므로 코드 변경 없이 전환 가능합니다.

**Q: Mock 데이터를 커스터마이징할 수 있나요?**
A: `tests/mocks/mock_db.py`의 `_init_parts_data()` 함수를 수정하면 됩니다.

**Q: 실제 환경 테스트 전 확인사항은?**
A: `.env`에서 `TEST_MODE=False` 설정 후, DB/LLM 연결 정보가 올바른지 확인하세요.
