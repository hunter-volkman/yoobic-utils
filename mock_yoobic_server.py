#!/usr/bin/env python3
"""
Mock YOOBIC Server for Development & Testing
Simulates YOOBIC API endpoints to enable development without real credentials
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
import uuid
import threading

app = Flask(__name__)

# Mock data storage
mock_data = {
    "users": {
        "test_user": {
            "username": "test_user",
            "password": "test_password",
            "org_id": "test_org_123",
            "token": None,
            "token_expires": None
        }
    },
    "missions": [],
    "stores": [
        {"id": "store_001", "name": "Test Store 1", "location": "New York"},
        {"id": "store_002", "name": "Test Store 2", "location": "Boston"},
        {"id": "store_003", "name": "Test Store 3", "location": "Chicago"}
    ],
    "mission_templates": {
        "temperature_check": {
            "title": "Temperature Compliance Check",
            "description": "Monitor refrigeration unit temperatures",
            "required_fields": ["temperature", "unit_id", "status"]
        }
    }
}

def generate_jwt_token(username: str) -> str:
    """Generate a mock JWT token"""
    return f"mock_jwt_token_{username}_{int(time.time())}"

def is_token_valid(token: str) -> bool:
    """Check if token is valid"""
    if not token:
        return False
    
    for user_data in mock_data["users"].values():
        if (user_data.get("token") == token and 
            user_data.get("token_expires") and 
            datetime.now() < user_data["token_expires"]):
            return True
    return False

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        if not is_token_valid(token):
            return jsonify({"error": "Invalid or expired token"}), 401
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/public/api/auth/login', methods=['POST'])
def login():
    """Mock login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Check credentials
    user = mock_data["users"].get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Generate token
    token = generate_jwt_token(username)
    expires = datetime.now() + timedelta(hours=1)
    
    # Store token
    user["token"] = token
    user["token_expires"] = expires
    
    return jsonify({
        "token": token,
        "expires": expires.isoformat(),
        "user": {
            "username": username,
            "org_id": user["org_id"]
        }
    })

@app.route('/public/api/missions', methods=['GET'])
@require_auth
def get_missions():
    """Get missions with optional filtering"""
    store_id = request.args.get('store_id')
    limit = int(request.args.get('limit', 10))
    
    missions = mock_data["missions"]
    
    if store_id:
        missions = [m for m in missions if m.get("store_id") == store_id]
    
    # Apply limit
    missions = missions[:limit]
    
    return jsonify({
        "data": missions,
        "count": len(missions),
        "total": len(mock_data["missions"])
    })

@app.route('/public/api/missions', methods=['POST'])
@require_auth
def create_mission():
    """Create a new mission"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["title", "type", "store_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create mission
    mission = {
        "mission_id": str(uuid.uuid4()),
        "title": data["title"],
        "type": data["type"],
        "store_id": data["store_id"],
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "due_date": data.get("due_date"),
        "custom_fields": data.get("custom_fields", {}),
        "priority": data.get("priority", "medium"),
        "created_by": "viam_mission_module"
    }
    
    mock_data["missions"].append(mission)
    
    print(f"🎯 Created mission: {mission['title']} for {mission['store_id']}")
    
    return jsonify(mission), 201

@app.route('/public/api/missions/<mission_id>/validate', methods=['POST'])
@require_auth
def validate_mission(mission_id: str):
    """Validate a mission"""
    data = request.get_json()
    
    # Find mission
    mission = None
    for m in mock_data["missions"]:
        if m["mission_id"] == mission_id:
            mission = m
            break
    
    if not mission:
        return jsonify({"error": "Mission not found"}), 404
    
    # Update mission
    mission["status"] = "completed" if data.get("compliant", True) else "non_compliant"
    mission["validated_at"] = datetime.now().isoformat()
    mission["validation_data"] = data
    
    print(f"✅ Validated mission: {mission['title']} - {mission['status']}")
    
    return jsonify(mission)

@app.route('/public/api/tenants', methods=['GET'])
@require_auth
def get_tenants():
    """Get tenant information"""
    return jsonify({
        "tenants": [
            {
                "id": "test_tenant",
                "name": "Test Organization",
                "stores": len(mock_data["stores"])
            }
        ]
    })

@app.route('/public/api/stores', methods=['GET'])
@require_auth
def get_stores():
    """Get store information"""
    return jsonify({
        "data": mock_data["stores"],
        "count": len(mock_data["stores"])
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "missions_count": len(mock_data["missions"]),
        "stores_count": len(mock_data["stores"])
    })

@app.route('/debug/reset', methods=['POST'])
def reset_data():
    """Reset all mock data (for testing)"""
    mock_data["missions"] = []
    for user in mock_data["users"].values():
        user["token"] = None
        user["token_expires"] = None
    
    return jsonify({"message": "Mock data reset"})

@app.route('/debug/missions', methods=['GET'])
def debug_missions():
    """Debug endpoint to view all missions"""
    return jsonify({
        "missions": mock_data["missions"],
        "count": len(mock_data["missions"])
    })

if __name__ == '__main__':
    print("🚀 Starting Mock YOOBIC Server")
    print("📋 Available endpoints:")
    print("  POST /public/api/auth/login")
    print("  GET  /public/api/missions")
    print("  POST /public/api/missions")
    print("  POST /public/api/missions/<id>/validate")
    print("  GET  /public/api/tenants")
    print("  GET  /public/api/stores")
    print("  GET  /health")
    print("  POST /debug/reset")
    print("  GET  /debug/missions")
    print()
    print("💡 Test credentials:")
    print("  Username: test_user")
    print("  Password: test_password")
    print()
    print("🌐 Server starting on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)