"""
MongoDB 샘플 데이터 생성 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
import random
from app.services.database_service import get_mongodb
from app.config import config

def seed_parts_data():
    """부품 데이터 생성"""
    mongodb = get_mongodb()

    # 기존 데이터 삭제
    print("기존 데이터 삭제 중...")
    mongodb.delete_many("parts", {})

    parts = []
    part_prefixes = ["ABC", "DEF", "XYZ", "QWE", "RTY"]
    categories = ["메모리", "프로세서", "센서", "기타"]
    warehouses = ["A", "B", "C"]
    defect_types = ["스크래치", "접착불량", "오염", "치수불량", "전기불량"]

    print(f"\n{len(part_prefixes)} x 4 = 20개 부품 데이터 생성 중...\n")

    for i in range(20):
        prefix = part_prefixes[i % len(part_prefixes)]
        part_number = f"{prefix}-{12345 + i}"

        # 출고 이력 생성 (최근 12개월)
        shipment_history = []
        base_date = datetime.now() - timedelta(days=365)

        for month in range(12):
            shipment_date = base_date + timedelta(days=30 * month)
            quantity = random.randint(50, 200)
            shipment_history.append({
                "date": shipment_date.strftime("%Y-%m-%d"),
                "quantity": quantity,
                "destination": f"라인 {random.randint(1, 3)}",
                "status": "completed"
            })

        # 장착 이력 생성
        mounting_history = []
        for j in range(random.randint(3, 8)):
            mount_date = datetime.now() - timedelta(days=random.randint(1, 180))
            mounting_history.append({
                "date": mount_date.strftime("%Y-%m-%d"),
                "equipment": f"장비-{random.randint(1, 10):03d}",
                "line": f"라인 {random.randint(1, 3)}",
                "quantity": random.randint(10, 50),
                "status": random.choice(["completed", "completed", "completed", "in_progress"])
            })

        # 재고 정보
        total_stock = random.randint(500, 2000)
        reserved = random.randint(0, min(300, total_stock // 2))
        available = total_stock - reserved

        part = {
            "part_number": part_number,
            "part_name": f"반도체 부품 {prefix} 시리즈",
            "category": categories[i % len(categories)],
            "manufacturer": random.choice(["삼성전자", "SK하이닉스", "인텔", "TSMC"]),
            "specifications": {
                "voltage": f"{random.choice([1.2, 1.5, 1.8, 3.3])}V",
                "temperature_range": f"-40°C ~ {random.choice([85, 105, 125])}°C",
                "package_type": random.choice(["BGA", "QFP", "DIP", "SOP"]),
                "dimensions": f"{random.randint(5, 15)}x{random.randint(5, 15)}mm"
            },
            "inventory": {
                "total_stock": total_stock,
                "available": available,
                "reserved": reserved,
                "location": f"창고 {random.choice(warehouses)}",
                "shelf": f"{random.choice(['A', 'B', 'C'])}-{random.randint(1, 20):02d}"
            },
            "shipment_history": shipment_history,
            "mounting_history": mounting_history,
            "quality_info": {
                "inspection_pass_rate": round(random.uniform(0.95, 0.995), 3),
                "defect_types": random.sample(defect_types, k=random.randint(1, 3)),
                "last_inspection": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            },
            "price_info": {
                "unit_price": round(random.uniform(10, 500), 2),
                "currency": "USD",
                "minimum_order": random.choice([10, 50, 100, 500])
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        parts.append(part)
        print(f"  [{i+1}/20] {part_number}: {part['part_name']}")

    # 데이터 삽입
    print(f"\n데이터베이스에 저장 중...")
    result = mongodb.insert_many("parts", parts)
    print(f"✓ {len(result)} 개의 부품 데이터 생성 완료!\n")

    # 통계 출력
    print("=== 생성된 데이터 통계 ===")
    print(f"총 부품 수: {len(parts)}개")
    print(f"카테고리별 분포:")
    for category in categories:
        count = sum(1 for p in parts if p["category"] == category)
        print(f"  - {category}: {count}개")

    # 샘플 데이터 상세 출력
    print("\n=== 샘플 데이터 (첫 번째 부품) ===")
    sample = parts[0]
    print(f"부품번호: {sample['part_number']}")
    print(f"부품명: {sample['part_name']}")
    print(f"카테고리: {sample['category']}")
    print(f"제조사: {sample['manufacturer']}")
    print(f"총 재고: {sample['inventory']['total_stock']}개")
    print(f"  - 가용: {sample['inventory']['available']}개")
    print(f"  - 예약: {sample['inventory']['reserved']}개")
    print(f"  - 위치: {sample['inventory']['location']}, {sample['inventory']['shelf']}")
    print(f"출고 이력: {len(sample['shipment_history'])}건")
    print(f"장착 이력: {len(sample['mounting_history'])}건")
    print(f"검사 합격률: {sample['quality_info']['inspection_pass_rate']*100:.1f}%")
    print(f"단가: ${sample['price_info']['unit_price']}")

if __name__ == "__main__":
    print("=" * 50)
    print("MongoDB 샘플 데이터 생성 스크립트")
    print("=" * 50)
    print()

    try:
        seed_parts_data()
        print("\n완료! 🎉")
        print("\n다음 명령어로 데이터를 확인할 수 있습니다:")
        print("  docker exec -it semiconductor_mongodb mongosh")
        print("  > use semiconductor_chatbot")
        print("  > db.parts.find().pretty()")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
