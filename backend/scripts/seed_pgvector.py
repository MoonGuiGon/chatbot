"""
pgvector 샘플 문서 생성 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from app.services.database_service import get_pgvector
from app.services.llm_service import get_embedding_llm
from app.config import config

def seed_documents():
    """샘플 문서 생성 및 임베딩"""
    pgvector = get_pgvector()
    embedding_llm = get_embedding_llm()

    # 샘플 문서
    documents = [
        {
            "content": """ABC-12345 부품 상세 사양
            - 제품명: DDR4 메모리 모듈
            - 규격: DDR4-3200
            - 용량: 8GB
            - 동작 전압: 1.2V
            - 동작 온도: -40°C ~ 85°C
            - 패키지: BGA-256
            - 제조사: 삼성전자
            - 보증기간: 5년""",
            "metadata": {
                "part_number": "ABC-12345",
                "type": "specification",
                "category": "메모리",
                "language": "ko"
            }
        },
        {
            "content": """부품 출고 절차
            1. 출고 요청서 작성
               - 부품번호, 수량, 목적지 명시
               - 담당자 승인 필요

            2. 재고 확인
               - 가용 재고 확인
               - 예약 재고와 구분

            3. 품질 검사
               - 육안 검사 (스크래치, 오염)
               - 전기적 특성 검사
               - 합격 기준: 검사 기준서 참조

            4. 포장
               - 정전기 방지 포장
               - 습기 방지 밀봉

            5. 출하
               - 출고 기록 생성
               - 재고 자동 차감""",
            "metadata": {
                "type": "procedure",
                "category": "출고",
                "language": "ko"
            }
        },
        {
            "content": """품질 검사 기준

            외관 검사:
            - 스크래치: 0.5mm 이하 허용
            - 변색: 육안으로 식별 가능한 변색 불허
            - 오염: 먼지, 이물질 부착 불허

            치수 검사:
            - 허용 오차: ±0.1mm
            - 측정 장비: 디지털 마이크로미터

            전기적 특성:
            - 접착 강도: 10N 이상
            - 절연 저항: 100MΩ 이상
            - 정전기 감도: Class 1A

            환경 시험:
            - 온도 사이클: -40°C ~ 85°C, 100회
            - 습도 시험: 85°C, 85%RH, 1000시간

            합격 기준: 모든 항목 통과 시 합격""",
            "metadata": {
                "type": "quality_standard",
                "category": "검사",
                "language": "ko"
            }
        },
        {
            "content": """DEF-12346 부품 보관 조건

            환경 조건:
            - 온도: 15-25°C (권장: 20°C)
            - 습도: 40-60% RH
            - 조도: 직사광선 차단

            포장 요구사항:
            - 정전기 방지 포장 필수 (ESD bag)
            - 습기 방지제 동봉
            - 밀봉 후 보관

            보관 위치:
            - 창고 A, 선반 B-05
            - 선입선출(FIFO) 원칙
            - 최대 적재 높이: 5단

            유효기간:
            - 제조일로부터 2년
            - 개봉 후 6개월 이내 사용 권장

            주의사항:
            - 충격 방지
            - 중량물 상부 적재 금지
            - 정기 재고 확인 (월 1회)""",
            "metadata": {
                "part_number": "DEF-12346",
                "type": "storage",
                "category": "보관",
                "language": "ko"
            }
        },
        {
            "content": """불량 처리 프로세스

            1. 불량 발견
               - 검사 중 발견
               - 사용 중 발견
               - 고객 반품

            2. 불량 분류
               - A등급: 재작업 가능
               - B등급: 일부 재사용 가능
               - C등급: 폐기 대상

            3. 원인 분석
               - 육안 검사
               - 현미경 검사
               - 전기적 분석
               - 근본 원인 파악 (Root Cause Analysis)

            4. 처리 결정
               - 재작업: 공정 재투입
               - 재선별: 등급 하향 후 재사용
               - 폐기: 환경 규정에 따라 처리

            5. 이력 기록
               - 불량 코드 부여
               - 데이터베이스 등록
               - 월간 보고서 작성
               - 재발 방지 대책 수립

            6. 재발 방지
               - 공정 개선
               - 검사 기준 강화
               - 교육 실시""",
            "metadata": {
                "type": "procedure",
                "category": "품질관리",
                "language": "ko"
            }
        },
        {
            "content": """부품 장착 절차

            사전 준비:
            - 작업장 청결 상태 확인
            - ESD 매트 및 손목띠 착용
            - 필요 공구 준비 (핀셋, 현미경)

            장착 단계:
            1. 기판 위치 확인
            2. 부품 방향 확인 (1번 핀 위치)
            3. 부품 배치
            4. 리플로우(Reflow) 또는 솔더링
            5. 육안 검사
            6. X-ray 검사 (필요 시)

            후처리:
            - 플럭스 제거
            - 세척
            - 최종 검사

            기록:
            - 작업자, 일시, 장비 번호 기록
            - 불량 발생 시 즉시 보고""",
            "metadata": {
                "type": "procedure",
                "category": "장착",
                "language": "ko"
            }
        },
        {
            "content": """재고 관리 정책

            최소 재고 수준:
            - A등급 부품(고회전율): 1000개
            - B등급 부품(중회전율): 500개
            - C등급 부품(저회전율): 200개

            재주문 시점:
            - 재고가 안전 재고 이하로 떨어질 시
            - 리드타임 고려 (평균 2주)

            재고 조사:
            - 월간: 전체 재고 실사
            - 주간: A등급 부품 재고 확인

            폐기 기준:
            - 유효기간 경과 부품
            - 3년 이상 미사용 부품
            - 단종 부품 (수요 없음)""",
            "metadata": {
                "type": "policy",
                "category": "재고",
                "language": "ko"
            }
        },
    ]

    print(f"\n총 {len(documents)}개 문서 임베딩 생성 중...\n")
    print("⚠️  OpenAI API를 사용하여 임베딩을 생성합니다.")
    print(f"예상 비용: 약 $0.01 미만\n")

    successful = 0
    failed = 0

    for i, doc in enumerate(documents, 1):
        try:
            # 임베딩 생성 (OpenAI API 호출)
            print(f"[{i}/{len(documents)}] 임베딩 생성 중...")
            print(f"  내용: {doc['content'][:60].strip()}...")

            # OpenAI API 호출
            embedding = embedding_llm.embed_query(doc["content"])
            print(f"  ✓ 임베딩 생성 완료 (차원: {len(embedding)})")

            # pgvector에 저장
            pgvector.insert(
                content=doc["content"],
                embedding=embedding,
                metadata=doc["metadata"]
            )
            print(f"  ✓ 데이터베이스 저장 완료")
            successful += 1

            # Rate Limit 방지를 위한 지연
            if i < len(documents):
                time.sleep(1)
                print()

        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")
            failed += 1
            continue

    print("=" * 60)
    print(f"✓ 완료: {successful}개 성공, {failed}개 실패")
    print("=" * 60)

    # 테스트 검색
    print("\n=== 검색 테스트 ===")
    test_queries = [
        "부품 출고는 어떻게 하나요?",
        "ABC-12345 부품의 사양은?",
        "불량이 발생하면 어떻게 처리하나요?"
    ]

    for query in test_queries:
        print(f"\n질문: {query}")

        try:
            query_embedding = embedding_llm.embed_query(query)
            results = pgvector.similarity_search(query_embedding, k=2)

            print(f"검색 결과 ({len(results)}건):")
            for i, result in enumerate(results, 1):
                similarity = result.get('similarity_score', 0)
                print(f"\n  {i}. 유사도: {similarity:.3f} ({similarity*100:.1f}%)")
                print(f"     내용: {result['content'][:100].strip()}...")
                print(f"     메타데이터: {result['metadata']}")

            time.sleep(1)  # Rate limit 방지

        except Exception as e:
            print(f"  ❌ 검색 오류: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("pgvector 샘플 문서 생성 스크립트")
    print("=" * 60)

    # 경고 메시지
    print("\n⚠️  주의사항:")
    print("  - 이 스크립트는 OpenAI API를 사용합니다")
    print("  - API Key가 .env 파일에 설정되어 있어야 합니다")
    print("  - 약간의 비용이 발생할 수 있습니다 (약 $0.01)")
    print()

    response = input("계속하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        sys.exit(0)

    try:
        seed_documents()
        print("\n완료! 🎉")
        print("\n다음 명령어로 데이터를 확인할 수 있습니다:")
        print("  docker exec -it semiconductor_postgres psql -U postgres -d vectordb")
        print("  > SELECT id, metadata, LEFT(content, 50) FROM documents;")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
