# 차트 및 표 시각화 가이드

## 개요

챗봇이 응답할 때 그래프, 차트, 표를 아름답게 표시하고 다운로드할 수 있는 기능이 추가되었습니다.

## 지원하는 시각화 타입

### 1. 차트 (EnhancedChart)
- **Line Chart** (선형 차트) - 시간에 따른 추세 표시
- **Bar Chart** (막대 차트) - 카테고리별 비교
- **Pie Chart** (원형 차트) - 비율 표시
- **Area Chart** (영역 차트) - 누적 데이터 표시

### 2. 표 (MaterialDataTable)
- 부품 재고 정보 테이블
- 진행률 바, 상태 인디케이터 포함
- Knowledge Graph 연관 정보 표시

## 백엔드에서 차트 데이터 보내기

### 1. 기본 구조

챗봇 응답 메시지의 `metadata`에 `chart_data`를 추가합니다:

```python
# backend/app/agents/enhanced_nodes.py

def generate_response_node_enhanced(state: GraphState) -> Dict:
    """응답 생성 노드 - 차트 데이터 포함"""

    # 기본 응답 텍스트
    response_text = "MAT-001의 최근 6개월 재고 추이입니다.\n\n"

    # 차트 데이터 준비
    chart_data = {
        "type": "line",  # 'line', 'bar', 'pie', 'area' 중 선택
        "title": "MAT-001 재고 추이",
        "xKey": "month",  # X축 데이터 키
        "yKey": "stock",  # Y축 데이터 키
        "height": 300,    # 차트 높이 (픽셀)
        "data": [
            {"month": "1월", "stock": 1500},
            {"month": "2월", "stock": 1200},
            {"month": "3월", "stock": 1800},
            {"month": "4월", "stock": 1400},
            {"month": "5월", "stock": 2000},
            {"month": "6월", "stock": 1700},
        ]
    }

    # 메시지 메타데이터에 차트 추가
    metadata = {
        "chart_data": chart_data,
        "sources": state.get("sources", []),
        "material_data": state.get("material_data", [])
    }

    return {
        "messages": [{
            "role": "assistant",
            "content": response_text,
            "metadata": metadata
        }]
    }
```

### 2. 차트 타입별 예제

#### Line Chart (추세 분석)

```python
chart_data = {
    "type": "line",
    "title": "월별 매출 추이",
    "xKey": "month",
    "yKey": "revenue",
    "height": 350,
    "data": [
        {"month": "1월", "revenue": 45000},
        {"month": "2월", "revenue": 52000},
        {"month": "3월", "revenue": 48000},
        # ...
    ]
}
```

#### Bar Chart (비교 분석)

```python
chart_data = {
    "type": "bar",
    "title": "부품 카테고리별 재고",
    "xKey": "category",
    "yKey": "count",
    "height": 400,
    "data": [
        {"category": "반도체", "count": 1200},
        {"category": "저항", "count": 3500},
        {"category": "커패시터", "count": 2800},
        {"category": "IC", "count": 950},
    ]
}
```

#### Pie Chart (비율 표시)

```python
chart_data = {
    "type": "pie",
    "title": "부품 상태 분포",
    "xKey": "status",
    "yKey": "percentage",
    "height": 350,
    "data": [
        {"status": "정상", "percentage": 75},
        {"status": "부족", "percentage": 15},
        {"status": "과잉", "percentage": 10},
    ]
}
```

#### Area Chart (누적 데이터)

```python
chart_data = {
    "type": "area",
    "title": "누적 주문량",
    "xKey": "week",
    "yKey": "orders",
    "height": 300,
    "data": [
        {"week": "1주", "orders": 120},
        {"week": "2주", "orders": 280},
        {"week": "3주", "orders": 450},
        # ...
    ]
}
```

### 3. 부품 데이터 테이블 보내기

```python
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
            "suppliers": [
                {"name": "공급업체A"},
                {"name": "공급업체B"}
            ],
            "similar_materials": [
                {"materialId": "MAT-002"}
            ]
        }
    },
    # 더 많은 부품...
]

metadata = {
    "material_data": material_data
}
```

## 완전한 예제

### 예제 1: 재고 분석 + 차트 + 테이블

```python
def analyze_inventory_node(state: GraphState) -> Dict:
    """재고 분석 노드"""

    query = state["query"]

    # MongoDB에서 부품 데이터 조회
    materials = mongodb_service.find_materials({"category": "반도체"})

    # 차트용 데이터 준비 (카테고리별 재고)
    chart_data = {
        "type": "bar",
        "title": "반도체 부품 카테고리별 재고 현황",
        "xKey": "name",
        "yKey": "stock",
        "height": 350,
        "data": [
            {"name": mat["name"], "stock": mat["inventory"]["current_stock"]}
            for mat in materials[:10]  # 상위 10개만
        ]
    }

    # 테이블용 데이터 준비
    material_data = [
        {
            "materialId": mat["materialId"],
            "name": mat["name"],
            "category": mat["category"],
            "inventory": mat["inventory"]
        }
        for mat in materials
    ]

    response_text = f"""
## 반도체 부품 재고 분석

총 {len(materials)}개의 반도체 부품을 분석했습니다.

### 주요 발견사항:
- 평균 재고량: {sum(m['inventory']['current_stock'] for m in materials) / len(materials):.0f}개
- 재고 부족 부품: {sum(1 for m in materials if m['inventory']['current_stock'] < m['inventory']['minimum_stock'])}개
- 재고 충분 부품: {sum(1 for m in materials if m['inventory']['current_stock'] >= m['inventory']['minimum_stock'] * 2)}개

아래 차트와 표에서 자세한 내용을 확인하세요.
"""

    return {
        "messages": [{
            "role": "assistant",
            "content": response_text,
            "metadata": {
                "chart_data": chart_data,
                "material_data": material_data,
                "sources": [{"type": "mongodb", "count": len(materials)}]
            }
        }]
    }
```

### 예제 2: 시계열 추세 분석

```python
def analyze_trend_node(state: GraphState) -> Dict:
    """시계열 추세 분석"""

    material_id = "MAT-001"

    # 최근 6개월 데이터 조회 (예시)
    trend_data = get_stock_history(material_id, months=6)

    # Line Chart 데이터
    chart_data = {
        "type": "line",
        "title": f"{material_id} 재고 추이 (최근 6개월)",
        "xKey": "date",
        "yKey": "quantity",
        "height": 400,
        "data": trend_data
    }

    # 추세 분석
    avg_stock = sum(d["quantity"] for d in trend_data) / len(trend_data)
    trend = "상승" if trend_data[-1]["quantity"] > avg_stock else "하락"

    response_text = f"""
## {material_id} 재고 추세 분석

### 분석 기간: 최근 6개월

- **평균 재고**: {avg_stock:.0f}개
- **추세**: {trend}
- **현재 재고**: {trend_data[-1]["quantity"]}개

아래 그래프에서 자세한 추이를 확인하세요.
"""

    return {
        "messages": [{
            "role": "assistant",
            "content": response_text,
            "metadata": {"chart_data": chart_data}
        }]
    }
```

## 다운로드 기능

### 차트 다운로드
- **PNG**: 고품질 이미지로 다운로드 (프레젠테이션용)
- **CSV**: 원본 데이터 다운로드 (Excel 분석용)

### 테이블 다운로드
- **Excel (.xlsx)**: 모든 테이블 데이터를 Excel 파일로 다운로드

## 프론트엔드 사용법

### 차트 렌더링

프론트엔드에서는 메시지 메타데이터에 `chart_data`가 있으면 자동으로 차트를 렌더링합니다:

```jsx
// EnhancedMessageBubble.jsx에서 자동 처리
{!isUser && chartData && (
  <EnhancedChart
    data={chartData.data}
    type={chartData.type}
    title={chartData.title}
    xKey={chartData.xKey}
    yKey={chartData.yKey}
    height={chartData.height}
  />
)}
```

### 사용자 경험

1. **챗봇 응답**: 텍스트 설명과 함께 차트/표 표시
2. **인터랙티브**: 마우스 호버 시 상세 정보 표시
3. **다운로드**: PNG, CSV, Excel 버튼으로 간편 다운로드
4. **애니메이션**: 부드러운 페이드인 효과

## 고급 활용

### 여러 차트 동시 표시

```python
# 여러 차트를 배열로 보낼 수도 있습니다 (필요시 구현)
metadata = {
    "charts": [
        {
            "type": "line",
            "title": "재고 추이",
            "data": [...],
            # ...
        },
        {
            "type": "pie",
            "title": "상태 분포",
            "data": [...],
            # ...
        }
    ]
}
```

### Vision 분석 + 차트 조합

```python
# 문서에서 추출한 데이터를 차트로 시각화
vision_result = vision_service.analyze_document_image(image_path)
structured_data = vision_result.get("structured_data", {})

if "table_data" in structured_data:
    chart_data = {
        "type": "bar",
        "title": "문서에서 추출한 데이터",
        "data": structured_data["table_data"]
    }
```

## 요약

✅ **완료된 기능**:
- Line, Bar, Pie, Area 차트 지원
- PNG, CSV 다운로드
- Excel 테이블 다운로드
- 아름다운 애니메이션 및 UI
- 반응형 디자인

🎯 **사용 시나리오**:
- 재고 추세 분석
- 카테고리별 비교
- 상태 분포 표시
- 부품 정보 테이블

💡 **팁**:
- 데이터는 10-20개 포인트가 가장 보기 좋음
- 차트 제목은 명확하게
- X축, Y축 키 이름을 데이터에 맞게 설정
- 색상은 자동으로 할당됨 (최대 8가지 색상)
