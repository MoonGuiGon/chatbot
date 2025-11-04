"""
Chart Visualization Example Node
차트 시각화 예제 노드
"""

from typing import Dict, List
from datetime import datetime, timedelta
import random


def create_stock_trend_chart(material_id: str, months: int = 6) -> Dict:
    """
    재고 추이 차트 데이터 생성 (Line Chart)

    Args:
        material_id: 자재 코드
        months: 조회할 개월 수

    Returns:
        차트 데이터 딕셔너리
    """
    # 샘플 데이터 생성 (실제로는 DB에서 조회)
    base_stock = 1500
    data = []

    for i in range(months):
        month_name = f"{i+1}월"
        # 랜덤 변동 추가
        stock = base_stock + random.randint(-300, 300)
        data.append({
            "month": month_name,
            "stock": stock
        })

    return {
        "type": "line",
        "title": f"{material_id} 재고 추이",
        "xKey": "month",
        "yKey": "stock",
        "height": 350,
        "data": data
    }


def create_category_comparison_chart(categories: List[str]) -> Dict:
    """
    카테고리별 재고 비교 차트 (Bar Chart)

    Args:
        categories: 카테고리 리스트

    Returns:
        차트 데이터 딕셔너리
    """
    data = []
    for category in categories:
        count = random.randint(500, 3000)
        data.append({
            "category": category,
            "count": count
        })

    return {
        "type": "bar",
        "title": "부품 카테고리별 재고 현황",
        "xKey": "category",
        "yKey": "count",
        "height": 400,
        "data": data
    }


def create_status_distribution_chart() -> Dict:
    """
    재고 상태 분포 차트 (Pie Chart)

    Returns:
        차트 데이터 딕셔너리
    """
    return {
        "type": "pie",
        "title": "재고 상태 분포",
        "xKey": "status",
        "yKey": "percentage",
        "height": 350,
        "data": [
            {"status": "충분", "percentage": 60},
            {"status": "적정", "percentage": 25},
            {"status": "부족", "percentage": 15},
        ]
    }


def create_cumulative_orders_chart(weeks: int = 8) -> Dict:
    """
    누적 주문량 차트 (Area Chart)

    Args:
        weeks: 조회할 주 수

    Returns:
        차트 데이터 딕셔너리
    """
    cumulative = 0
    data = []

    for week in range(1, weeks + 1):
        weekly_orders = random.randint(100, 250)
        cumulative += weekly_orders
        data.append({
            "week": f"{week}주",
            "orders": cumulative
        })

    return {
        "type": "area",
        "title": "누적 주문량",
        "xKey": "week",
        "yKey": "orders",
        "height": 300,
        "data": data
    }


def example_chart_response_node(state: Dict) -> Dict:
    """
    예제: 차트가 포함된 응답 생성

    이 함수는 LangGraph 노드에서 사용할 수 있는 예제입니다.

    Args:
        state: GraphState

    Returns:
        업데이트된 state
    """
    query = state.get("query", "").lower()

    # 쿼리에 따라 적절한 차트 선택
    if "추이" in query or "트렌드" in query:
        chart_data = create_stock_trend_chart("MAT-001", months=6)
        response_text = """
## MAT-001 재고 추이 분석

최근 6개월간의 재고 변화를 분석했습니다.

### 주요 분석:
- 평균 재고량: 약 1,500개
- 최고점: 3월 (1,800개)
- 최저점: 2월 (1,200개)
- 변동폭: 약 600개

아래 차트에서 자세한 추이를 확인하세요.
"""

    elif "카테고리" in query or "비교" in query:
        categories = ["반도체", "저항", "커패시터", "IC", "트랜지스터"]
        chart_data = create_category_comparison_chart(categories)
        response_text = """
## 부품 카테고리별 재고 현황

5개 주요 카테고리의 재고를 비교 분석했습니다.

### 카테고리별 특징:
- **반도체**: 고가 부품으로 적정 재고 유지 중
- **저항**: 소모품으로 대량 재고 보유
- **커패시터**: 다양한 용량으로 중간 재고
- **IC**: 특수 부품으로 관리 필요
- **트랜지스터**: 범용 부품으로 안정적 재고

아래 차트에서 각 카테고리의 재고량을 확인하세요.
"""

    elif "상태" in query or "분포" in query:
        chart_data = create_status_distribution_chart()
        response_text = """
## 재고 상태 분포

전체 부품의 재고 상태를 분석했습니다.

### 상태 요약:
- 🟢 **충분** (60%): 최소 재고의 2배 이상
- 🟡 **적정** (25%): 최소 재고 ~ 2배 사이
- 🔴 **부족** (15%): 최소 재고 미만 (주문 필요)

아래 차트에서 비율을 확인하세요.
"""

    elif "주문" in query or "누적" in query:
        chart_data = create_cumulative_orders_chart(weeks=8)
        response_text = """
## 누적 주문량 분석

최근 8주간의 주문량 누적 추이입니다.

### 주문 패턴:
- 주간 평균 주문량: 약 150-200개
- 총 누적 주문량: 증가 추세
- 성수기 예상: 4-5주차 증가 패턴

아래 차트에서 누적 추이를 확인하세요.
"""

    else:
        # 기본 응답 (차트 없음)
        return {
            "messages": [{
                "role": "assistant",
                "content": "죄송합니다. 차트를 생성할 수 없는 질문입니다. '추이', '비교', '상태', '주문' 등의 키워드를 포함해주세요."
            }]
        }

    # 차트 데이터를 포함한 응답 반환
    return {
        "messages": [{
            "role": "assistant",
            "content": response_text,
            "metadata": {
                "chart_data": chart_data,
                "sources": [{"type": "analysis", "timestamp": datetime.now().isoformat()}]
            }
        }]
    }


def example_combined_response_node(state: Dict) -> Dict:
    """
    예제: 차트 + 테이블이 함께 포함된 응답

    Args:
        state: GraphState

    Returns:
        업데이트된 state
    """
    # 차트 데이터
    chart_data = create_stock_trend_chart("MAT-001", months=6)

    # 테이블 데이터
    material_data = [
        {
            "materialId": "MAT-001",
            "name": "반도체 A",
            "category": "반도체",
            "inventory": {
                "current_stock": 1500,
                "minimum_stock": 1000
            },
            "kg_context": {
                "suppliers": [{"name": "공급업체A"}, {"name": "공급업체B"}],
                "similar_materials": [{"materialId": "MAT-002"}]
            }
        },
        {
            "materialId": "MAT-002",
            "name": "저항 100Ω",
            "category": "저항",
            "inventory": {
                "current_stock": 3500,
                "minimum_stock": 2000
            }
        },
        {
            "materialId": "MAT-003",
            "name": "커패시터 10μF",
            "category": "커패시터",
            "inventory": {
                "current_stock": 800,
                "minimum_stock": 1000
            }
        }
    ]

    response_text = """
## 종합 재고 분석 보고서

### 📊 재고 추이 (MAT-001)
최근 6개월간의 재고 변화를 그래프로 표시했습니다.

### 📋 상세 재고 현황
아래 표에서 각 부품의 상세 정보를 확인하세요.

#### 주요 발견사항:
- MAT-001: 재고 충분 ✅
- MAT-002: 재고 충분 ✅
- MAT-003: 재고 부족 ⚠️ (주문 필요)

💡 **추천 조치**: MAT-003의 재고를 200개 이상 추가 주문하는 것을 권장합니다.
"""

    return {
        "messages": [{
            "role": "assistant",
            "content": response_text,
            "metadata": {
                "chart_data": chart_data,
                "material_data": material_data,
                "sources": [
                    {"type": "mongodb", "count": 3},
                    {"type": "analysis", "timestamp": datetime.now().isoformat()}
                ]
            }
        }]
    }
