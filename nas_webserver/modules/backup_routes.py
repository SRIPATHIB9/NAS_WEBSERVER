import os
import shutil
import datetime
from flask import Blueprint, request, jsonify
from modules.auth_middleware import login_required

backup_bp = Blueprint('backup', __name__)

BACKUP_FOLDER = 'backups'
UPLOAD_FOLDER = 'uploads'

# Ensure backup folder exists
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# 🔄 Create a new backup
@backup_bp.route('/backup/run', methods=['GET'])
@login_required(role='admin')
def run_backup():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    backup_name = f'backup_{timestamp}'
    archive_path = shutil.make_archive(os.path.join(BACKUP_FOLDER, backup_name), 'zip', UPLOAD_FOLDER)
    return jsonify({
        'message': 'Backup created successfully',
        'file': os.path.basename(archive_path)
    })

# ♻️ Restore a backup from uploaded zip
@backup_bp.route('/backup/restore', methods=['POST'])
@login_required(role='admin')
def restore_backup():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.zip'):
        return jsonify({'error': 'Invalid or missing .zip file'}), 400

    path = os.path.join(BACKUP_FOLDER, file.filename)
    file.save(path)

    try:
        shutil.unpack_archive(path, UPLOAD_FOLDER, 'zip')
        return jsonify({'message': 'Backup restored successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to restore: {str(e)}'}), 500

