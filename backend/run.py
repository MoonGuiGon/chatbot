"""
Flask 서버 실행
"""
from app import create_app
from app.config import config

if __name__ == "__main__":
    app = create_app()

    print(f"""
    ========================================
    반도체 부품 챗봇 서버 시작
    ========================================
    모드: {'테스트 모드 (Mock DB/LLM)' if config.test_mode else '운영 모드'}
    포트: {config.flask_port}
    ========================================
    """)

    app.run(
        host="0.0.0.0",
        port=config.flask_port,
        debug=config.flask_debug
    )
