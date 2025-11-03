"""
Export and download API routes
"""
from flask import Blueprint, request, jsonify, send_file
import logging
import io
import os
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__, url_prefix='/api/export')


@export_bp.route('/material', methods=['POST'])
def export_material_data():
    """Export material data to Excel"""
    try:
        data = request.json
        materials = data.get('materials', [])

        if not materials:
            return jsonify({"error": "No data to export"}), 400

        # Create DataFrame
        df_data = []
        for material in materials:
            row = {
                '자재코드': material.get('materialId', ''),
                '부품명': material.get('name', ''),
                '카테고리': material.get('category', ''),
                '공급업체': material.get('supplier', ''),
            }

            # Add inventory info
            if material.get('inventory'):
                inv = material['inventory']
                row['현재재고'] = inv.get('current_stock', 0)
                row['최소재고'] = inv.get('minimum_stock', 0)
                row['보관위치'] = inv.get('location', '')

            # Add specifications
            if material.get('specifications'):
                specs = material['specifications']
                for key, value in specs.items():
                    row[key] = value

            df_data.append(row)

        df = pd.DataFrame(df_data)

        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='부품정보')

            # Auto-adjust column width
            worksheet = writer.sheets['부품정보']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

        output.seek(0)

        filename = f"material_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error exporting material data: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@export_bp.route('/conversation/<int:conversation_id>', methods=['GET'])
def export_conversation(conversation_id):
    """Export conversation to text file"""
    try:
        from app.services.database_service import db_service
        from app.models.database import Conversation, Message

        with db_service.get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404

            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).all()

            # Create text content
            lines = [
                f"대화 제목: {conversation.title}",
                f"생성일: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 80,
                ""
            ]

            for msg in messages:
                role_label = "사용자" if msg.role == "user" else "어시스턴트"
                lines.append(f"[{role_label}] ({msg.created_at.strftime('%Y-%m-%d %H:%M:%S')})")
                lines.append(msg.content)
                lines.append("-" * 80)
                lines.append("")

            content = "\n".join(lines)

            # Create file in memory
            output = io.BytesIO()
            output.write(content.encode('utf-8'))
            output.seek(0)

            filename = f"conversation_{conversation_id}_{datetime.now().strftime('%Y%m%d')}.txt"

            return send_file(
                output,
                mimetype='text/plain; charset=utf-8',
                as_attachment=True,
                download_name=filename
            )

    except Exception as e:
        logger.error(f"Error exporting conversation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@export_bp.route('/document', methods=['POST'])
def download_document():
    """
    Download a source document
    (In real scenario, this would fetch from file storage)
    """
    try:
        data = request.json
        source = data.get('source')
        doc_type = data.get('type', 'pdf')

        if not source:
            return jsonify({"error": "Source is required"}), 400

        # In real scenario, fetch the actual file from storage
        # For now, return a mock message
        return jsonify({
            "message": f"Document download: {source}",
            "note": "In production, this would return the actual file from storage"
        })

    except Exception as e:
        logger.error(f"Error downloading document: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
