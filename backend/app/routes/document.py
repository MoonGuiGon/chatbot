"""
문서 관리 API 라우트
"""
from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from app.services.document_processor import DocumentProcessor
from app.services.database_service import get_mongodb, get_pgvector
from app.config import config

bp = Blueprint("document", __name__)

# 문서 처리기
doc_processor = DocumentProcessor()

# 검수 대기 문서 임시 저장 (실제로는 MongoDB에 저장)
pending_documents = {}


def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in config.allowed_extensions


@bp.route("/documents/upload", methods=["POST"])
def upload_document():
    """
    문서 업로드 및 검수용 파싱

    Returns:
        검수용 청크 데이터
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "파일이 없습니다."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "파일명이 없습니다."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": f"허용되지 않는 파일 형식입니다. 허용: {config.allowed_extensions}"
        }), 400

    # 파일 저장
    filename = secure_filename(file.filename)
    file_path = os.path.join(config.upload_folder, filename)
    file.save(file_path)

    try:
        # 검수용 처리 (임베딩 제외)
        review_data = doc_processor.process_for_review(file_path)

        # 임시 저장 (검수 완료 후 사용)
        document_id = review_data["document_id"]
        pending_documents[document_id] = {
            "file_path": file_path,
            "review_data": review_data
        }

        return jsonify({
            "success": True,
            "document_id": document_id,
            "review_data": review_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"문서 처리 실패: {str(e)}"
        }), 500


@bp.route("/documents/<document_id>/approve", methods=["POST"])
def approve_document(document_id):
    """
    문서 검수 승인 및 VectorDB 저장

    Request:
        {
            "chunks": [
                {
                    "chunk_index": 0,
                    "content": "...",
                    "approved": true,
                    "metadata": {...}
                },
                ...
            ]
        }
    """
    data = request.get_json()
    approved_chunks = data.get("chunks", [])

    # 임시 저장된 문서 확인
    if document_id not in pending_documents:
        return jsonify({
            "success": False,
            "error": "문서를 찾을 수 없습니다."
        }), 404

    try:
        # 최종 처리 (임베딩)
        parsed_doc = doc_processor.finalize_document(document_id, approved_chunks)

        # pgvector에 저장
        pgvector = get_pgvector()
        chunk_records = [
            {
                "document_id": parsed_doc.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "chunk_type": chunk.chunk_type,
                "embedding": chunk.embedding,
                "metadata": chunk.metadata
            }
            for chunk in parsed_doc.chunks
        ]

        ids = pgvector.add_documents(chunk_records)

        # MongoDB에 문서 메타데이터 저장
        mongodb = get_mongodb()
        mongodb.insert_one("document_metadata", {
            "document_id": parsed_doc.document_id,
            "file_name": parsed_doc.file_name,
            "file_type": parsed_doc.file_type,
            "total_chunks": len(parsed_doc.chunks),
            "status": "approved",
            "pgvector_ids": ids
        })

        # 임시 저장소에서 제거
        del pending_documents[document_id]

        return jsonify({
            "success": True,
            "document_id": document_id,
            "chunks_saved": len(ids)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"문서 저장 실패: {str(e)}"
        }), 500


@bp.route("/documents/<document_id>/reject", methods=["DELETE"])
def reject_document(document_id):
    """문서 검수 거부"""
    if document_id not in pending_documents:
        return jsonify({
            "success": False,
            "error": "문서를 찾을 수 없습니다."
        }), 404

    # 파일 삭제
    file_path = pending_documents[document_id]["file_path"]
    if os.path.exists(file_path):
        os.remove(file_path)

    # 임시 저장소에서 제거
    del pending_documents[document_id]

    return jsonify({
        "success": True,
        "message": "문서가 거부되었습니다."
    })


@bp.route("/documents", methods=["GET"])
def list_documents():
    """저장된 문서 목록 조회"""
    mongodb = get_mongodb()
    documents = mongodb.find("document_metadata", {}, limit=100)

    return jsonify({
        "success": True,
        "documents": documents
    })


@bp.route("/documents/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    """문서 삭제"""
    try:
        # pgvector에서 삭제
        pgvector = get_pgvector()
        pgvector.delete_document(document_id)

        # MongoDB에서 삭제
        mongodb = get_mongodb()
        mongodb.delete_one("document_metadata", {"document_id": document_id})

        return jsonify({
            "success": True,
            "message": "문서가 삭제되었습니다."
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"문서 삭제 실패: {str(e)}"
        }), 500
