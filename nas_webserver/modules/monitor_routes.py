import psutil
from flask import Blueprint, jsonify
from modules.auth_middleware import login_required

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/monitor/system', methods=['GET'])
@login_required()
def get_system_status():
    return jsonify({
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    })

@monitor_bp.route('/monitor/logs', methods=['GET'])
@login_required(role='admin')
def get_logs():
    try:
        with open('/var/log/syslog', 'r') as f:
            lines = f.readlines()[-20:]
        return jsonify({'logs': lines})
    except FileNotFoundError:
        return jsonify({'message': 'Log file not found'}), 404
