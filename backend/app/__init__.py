"""
Flask 애플리케이션 초기화
"""
from flask import Flask
from flask_cors import CORS
from app.config import config


def create_app():
    """Flask 앱 생성 및 설정"""
    app = Flask(__name__)

    # CORS 설정
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 설정
    app.config["DEBUG"] = config.flask_debug
    app.config["UPLOAD_FOLDER"] = config.upload_folder
    app.config["MAX_CONTENT_LENGTH"] = config.max_file_size

    # 업로드 폴더 생성
    import os
    os.makedirs(config.upload_folder, exist_ok=True)

    # 라우트 등록
    from app.routes import chat, document, settings, feedback, memory

    app.register_blueprint(chat.bp, url_prefix="/api")
    app.register_blueprint(document.bp, url_prefix="/api")
    app.register_blueprint(settings.bp, url_prefix="/api")
    app.register_blueprint(feedback.bp, url_prefix="/api")
    app.register_blueprint(memory.bp, url_prefix="/api")

    # 헬스 체크
    @app.route("/health")
    def health_check():
        return {"status": "ok", "test_mode": config.test_mode}

    return app
