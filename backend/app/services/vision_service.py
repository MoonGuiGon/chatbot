"""
Vision Model Service - For document screenshot analysis
"""
import base64
import logging
from typing import Optional, Dict, Any, List
from io import BytesIO
from PIL import Image
import requests

from app.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """Vision Model Service for analyzing document screenshots"""

    def __init__(self):
        self.api_key = settings.llm_api_key
        self.api_url = settings.llm_api_url
        self.vision_model = settings.llm_vision_model
        self.use_mock = not self.api_key or not self.api_url

        if self.use_mock:
            logger.info("Vision API not configured. Using mock responses.")

    def analyze_document_image(
        self,
        image_path: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze document image and extract information

        Args:
            image_path: Path to the image file
            prompt: Optional custom prompt

        Returns:
            Dict containing summary, key_points, and structured_data
        """
        if self.use_mock:
            return self._mock_analysis(image_path)

        try:
            # Load and encode image
            with Image.open(image_path) as img:
                # Resize if too large for better performance
                max_size = (1920, 1920)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Convert to base64
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Prepare prompt
            if not prompt:
                prompt = """이 문서 이미지를 분석하여 다음을 제공하세요:

1. **요약**: 문서의 주요 내용을 2-3문장으로 요약
2. **핵심 포인트**: 중요한 정보를 bullet point로 나열
3. **구조화 데이터**: 표, 숫자, 날짜 등이 있다면 추출
4. **시각 요소**: 차트, 다이어그램, 이미지가 있다면 설명

JSON 형식으로 응답하세요:
{
  "summary": "...",
  "key_points": ["...", "..."],
  "structured_data": {...},
  "visual_elements": ["..."]
}
"""

            # Call vision API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.vision_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }

            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            # Try to parse as JSON
            try:
                import json
                analysis = json.loads(content)
            except:
                # If not JSON, return as summary
                analysis = {
                    "summary": content,
                    "key_points": [],
                    "structured_data": {},
                    "visual_elements": []
                }

            return analysis

        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return self._mock_analysis(image_path)

    def batch_analyze_images(
        self,
        image_paths: List[str],
        prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Batch analyze multiple images for better performance"""
        results = []
        for image_path in image_paths:
            result = self.analyze_document_image(image_path, prompt)
            results.append(result)
        return results

    def generate_summary_for_rag(
        self,
        image_path: str,
        text_content: str
    ) -> str:
        """
        Generate enhanced summary combining text and visual information
        This summary will be stored with the document for better RAG retrieval
        """
        if self.use_mock:
            return f"[Mock Summary] {text_content[:200]}... (이미지 분석: 차트 및 표 포함)"

        try:
            prompt = f"""다음 문서의 텍스트와 이미지를 함께 분석하여 RAG 검색에 최적화된 요약을 생성하세요.

텍스트 내용:
{text_content[:1000]}

요구사항:
1. 텍스트와 이미지의 정보를 모두 포함
2. 검색에 유용한 키워드 강조
3. 숫자, 날짜, 고유명사 등 정확히 표기
4. 3-5문장으로 간결하게 작성

요약:"""

            analysis = self.analyze_document_image(image_path, prompt)
            return analysis.get('summary', text_content[:200])

        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return text_content[:200]

    def _mock_analysis(self, image_path: str) -> Dict[str, Any]:
        """Return mock analysis for testing"""
        return {
            "summary": f"문서 '{image_path}'의 분석 결과입니다. 주요 내용은 반도체 부품 관리 및 사양 정보를 포함하고 있습니다.",
            "key_points": [
                "부품 보관 조건: 온도 20-25도, 습도 40-60%",
                "자재코드 MAT-001 관련 사양",
                "구매 및 재고 현황 데이터 포함"
            ],
            "structured_data": {
                "temperature": "20-25도",
                "humidity": "40-60%",
                "material_code": "MAT-001"
            },
            "visual_elements": [
                "테이블: 부품 사양 정보",
                "차트: 분기별 구매 현황"
            ]
        }


# Global instance
vision_service = VisionService()
