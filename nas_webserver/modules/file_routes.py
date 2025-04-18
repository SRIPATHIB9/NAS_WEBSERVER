import os
import shutil
from flask import Blueprint, request, send_from_directory, jsonify, current_app
from flask import render_template  # for optional template support
from modules.auth_middleware import login_required

file_bp = Blueprint('file', __name__)

# Utility to validate safe names
def is_safe_name(name):
    return name and not any(x in name for x in ['..', '/', '\\'])

# Upload a file
@file_bp.route('/upload', methods=['POST'])
@login_required(role='write')
def upload_file():
    file = request.files.get('file')
    if not file or not is_safe_name(file.filename):
        return jsonify({'error': 'Invalid or missing file'}), 400
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    return jsonify({'message': 'File uploaded successfully'})

# Download a file
@file_bp.route('/download/<filename>', methods=['GET'])
@login_required(role='read')
def download_file(filename):
    if not is_safe_name(filename):
        return jsonify({'error': 'Invalid filename'}), 400
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

# Delete a file
@file_bp.route('/delete/<filename>', methods=['DELETE'])
@login_required(role='edit')
def delete_file(filename):
    if not is_safe_name(filename):
        return jsonify({'error': 'Invalid filename'}), 400
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(path):
        os.remove(path)
        return jsonify({'message': 'File deleted'})
    return jsonify({'error': 'File not found'}), 404

# List all files/folders with metadata
@file_bp.route('/api/files', methods=['GET'])
@login_required(role='read')
def list_files():
    files = []
    for entry in os.scandir(current_app.config['UPLOAD_FOLDER']):
        stat = entry.stat()
        files.append({
            'name': entry.name,
            'size': stat.st_size if entry.is_file() else 0,
            'modified': stat.st_mtime,
            'is_folder': entry.is_dir()
        })
    return jsonify(files)

# Create folder
@file_bp.route('/folder/create', methods=['POST'])
@login_required(role='write')
def create_folder():
    name = request.json.get('folder')
    if not is_safe_name(name):
        return jsonify({'error': 'Invalid folder name'}), 400
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], name)
    if not os.path.exists(path):
        os.makedirs(path)
        return jsonify({'message': 'Folder created'})
    return jsonify({'error': 'Folder already exists'}), 409

# Delete folder
@file_bp.route('/folder/delete', methods=['DELETE'])
@login_required(role='admin')
def delete_folder():
    folder = request.json.get('folder')
    if not is_safe_name(folder):
        return jsonify({'error': 'Invalid folder name'}), 400
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
        return jsonify({'message': 'Folder deleted'})
    return jsonify({'error': 'Folder not found'}), 404

# Rename file or folder
@file_bp.route('/rename', methods=['PUT'])
@login_required(role='edit')
def rename_item():
    data = request.get_json()
    old = data.get('old_name')
    new = data.get('new_name')
    if not is_safe_name(old) or not is_safe_name(new):
        return jsonify({'error': 'Invalid names'}), 400
    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old)
    new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new)
    if not os.path.exists(old_path):
        return jsonify({'error': 'Item not found'}), 404
    os.rename(old_path, new_path)
    return jsonify({'message': 'Renamed successfully'})

# Save file edits (inline editing)
@file_bp.route('/edit/<filename>', methods=['POST'])
@login_required(role='write')
def save_edited_file(filename):
    if not is_safe_name(filename):
        return jsonify({'error': 'Invalid filename'}), 400
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    content = request.form.get('content')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': 'File saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

