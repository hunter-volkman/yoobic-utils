#!/usr/bin/env python3
"""
Mission Module Test Suite
Tests the mission module with mock YOOBIC server
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the main module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'yoobic', 'src'))

# Mock Viam imports for testing
class MockComponentConfig:
    def __init__(self, name: str, attributes: Dict):
        self.name = name
        self.attributes = MockStruct(attributes)

class MockStruct:
    def __init__(self, data: Dict):
        self._data = data

def struct_to_dict(struct):
    if hasattr(struct, '_data'):
        return struct._data
    return struct

# Monkey patch for testing
import models.mission
models.mission.struct_to_dict = struct_to_dict

from models.mission import MissionManager

class MissionModuleTester:
    def __init__(self):
        self.mission_manager = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        
    def create_test_config(self) -> Dict[str, Any]:
        """Create test configuration."""
        return {
            "platform": {
                "type": "yoobic",
                "base_url": "http://localhost:5000/public/api",
                "authentication": {
                    "method": "username_password",
                    "username": "test_user",
                    "password": "test_password",
                    "endpoint": "/auth/login",
                    "token_expires_minutes": 60
                },
                "endpoints": {
                    "create_mission": "/missions",
                    "get_missions": "/missions",
                    "validate_mission": "/missions/{mission_id}/validate",
                    "health": "/health"
                }
            },
            "mission_rules": [
                {
                    "name": "temperature_violation",
                    "trigger": {
                        "type": "threshold",
                        "field": "temperature",
                        "operator": "gt",
                        "threshold": 4.0
                    },
                    "action": {
                        "title": "Temperature Alert - {unit_name}",
                        "type": "temperature_check",
                        "priority": "high",
                        "due_hours": 1,
                        "custom_fields": {
                            "temperature": "{temperature}",
                            "threshold": "4.0",
                            "unit_name": "{unit_name}",
                            "sensor_id": "{sensor_id}"
                        }
                    }
                },
                {
                    "name": "critical_temperature",
                    "trigger": {
                        "type": "threshold",
                        "field": "temperature",
                        "operator": "gt",
                        "threshold": 8.0
                    },
                    "action": {
                        "title": "CRITICAL: Equipment Failure - {unit_name}",
                        "type": "equipment_failure",
                        "priority": "critical",
                        "due_hours": 0.5,
                        "custom_fields": {
                            "temperature": "{temperature}",
                            "critical_threshold": "8.0",
                            "unit_name": "{unit_name}",
                            "requires_immediate_attention": True
                        }
                    }
                }
            ],
            "data_sources": [
                {
                    "name": "mock_temperature_sensors",
                    "type": "mock",
                    "stores": ["store_001", "store_002", "store_003"],
                    "base_temperature": 2.5
                }
            ],
            "sync_interval": 5,  # 5 seconds for testing
            "batch_size": 10,
            "retry_attempts": 2,
            "timeout": 10,
            "auto_sync": False  # Disable auto sync for testing
        }

    async def test_module_initialization(self):
        """Test module initialization."""
        try:
            config = MockComponentConfig("test-mission-manager", self.create_test_config())
            self.mission_manager = MissionManager.new(config, {})
            
            if self.mission_manager._configured:
                self.log_result("Module Initialization", True, "Module configured successfully")
            else:
                self.log_result("Module Initialization", False, "Module not configured")
                
        except Exception as e:
            self.log_result("Module Initialization", False, f"Error: {str(e)}")

    async def test_authentication(self):
        """Test authentication with mock server."""
        try:
            result = await self.mission_manager.do_command({"command": "check_auth"})
            
            if result.get("authenticated"):
                self.log_result("Authentication", True, "Authentication successful")
            else:
                self.log_result("Authentication", False, f"Auth failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("Authentication", False, f"Error: {str(e)}")

    async def test_connection(self):
        """Test connection to mock server."""
        try:
            result = await self.mission_manager.do_command({"command": "test_connection"})
            
            if result.get("success"):
                self.log_result("Connection Test", True, f"Response time: {result.get('response_time', 0):.3f}s")
            else:
                self.log_result("Connection Test", False, f"Connection failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("Connection Test", False, f"Error: {str(e)}")

    async def test_manual_mission_creation(self):
        """Test manual mission creation."""
        try:
            mission_data = {
                "command": "create_mission",
                "title": "Test Mission",
                "type": "test",
                "store_id": "store_001",
                "priority": "medium",
                "custom_fields": {
                    "test_field": "test_value"
                }
            }
            
            result = await self.mission_manager.do_command(mission_data)
            
            if result.get("success"):
                self.log_result("Manual Mission Creation", True, f"Mission created successfully")
            else:
                self.log_result("Manual Mission Creation", False, f"Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("Manual Mission Creation", False, f"Error: {str(e)}")

    async def test_rule_evaluation(self):
        """Test mission rule evaluation."""
        try:
            # Test data that should trigger temperature violation rule
            test_data = {
                "command": "evaluate_rules",
                "data": {
                    "temperature": 6.0,
                    "store_id": "store_001",
                    "unit_name": "Walk in Fridge",
                    "sensor_id": "temp_sensor_001"
                }
            }
            
            result = await self.mission_manager.do_command(test_data)
            
            if result.get("success") and result.get("count", 0) > 0:
                self.log_result("Rule Evaluation", True, f"Generated {result.get('count')} missions")
            else:
                self.log_result("Rule Evaluation", False, f"No missions generated or error: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            self.log_result("Rule Evaluation", False, f"Error: {str(e)}")

    async def test_sync_operation(self):
        """Test sync operation."""
        try:
            result = await self.mission_manager.do_command({"command": "sync_now"})
            
            if result.get("success"):
                self.log_result("Sync Operation", True, "Sync completed successfully")
            else:
                self.log_result("Sync Operation", False, f"Sync failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("Sync Operation", False, f"Error: {str(e)}")

    async def test_get_missions(self):
        """Test getting missions."""
        try:
            result = await self.mission_manager.do_command({
                "command": "get_missions",
                "limit": 10
            })
            
            if result.get("success"):
                mission_count = result.get("count", 0)
                self.log_result("Get Missions", True, f"Retrieved {mission_count} missions")
            else:
                self.log_result("Get Missions", False, f"Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log_result("Get Missions", False, f"Error: {str(e)}")

    async def test_sensor_readings(self):
        """Test sensor readings."""
        try:
            readings = await self.mission_manager.get_readings()
            
            if readings.get("configured"):
                self.log_result("Sensor Readings", True, f"Retrieved {len(readings)} readings")
            else:
                self.log_result("Sensor Readings", False, f"Not configured or error: {readings.get('error', 'Unknown')}")
                
        except Exception as e:
            self.log_result("Sensor Readings", False, f"Error: {str(e)}")

    async def test_stats(self):
        """Test statistics."""
        try:
            result = await self.mission_manager.do_command({"command": "get_stats"})
            
            if result.get("success"):
                stats = result.get("stats", {})
                self.log_result("Statistics", True, f"Missions created: {stats.get('missions_created', 0)}")
            else:
                self.log_result("Statistics", False, "Failed to get statistics")
                
        except Exception as e:
            self.log_result("Statistics", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting Mission Module Tests")
        print("=" * 50)
        
        # Wait a moment for mock server to be ready
        await asyncio.sleep(2)
        
        # Run tests in order
        await self.test_module_initialization()
        
        if self.mission_manager:
            await self.test_authentication()
            await self.test_connection()
            await self.test_manual_mission_creation()
            await self.test_rule_evaluation()
            await self.test_sync_operation()
            await self.test_get_missions()
            await self.test_sensor_readings()
            await self.test_stats()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r["success"])
        failed = sum(1 for r in self.test_results if not r["success"])
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / len(self.test_results)) * 100:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")

        # Clean up
        if self.mission_manager:
            await self.mission_manager.close()

def check_mock_server():
    """Check if mock server is running."""
    import requests
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

async def main():
    """Main test function."""
    print("🚀 Mission Module Testing Suite")
    print("=" * 50)
    
    # Check if mock server is running
    if not check_mock_server():
        print("❌ Mock server not running!")
        print("Please start the mock server first:")
        print("  python mock_yoobic_server.py")
        return
    
    print("✅ Mock server is running")
    
    # Run tests
    tester = MissionModuleTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())