#!/usr/bin/env python3
"""
Development Launcher for Mission Module
Runs mock server and module tests in a coordinated fashion
"""

import asyncio
import subprocess
import sys
import time
import requests
import signal
import os
from pathlib import Path

class DevLauncher:
    def __init__(self):
        self.mock_server_process = None
        self.running = True
        
    def start_mock_server(self):
        """Start the mock YOOBIC server."""
        print("🚀 Starting mock YOOBIC server...")
        
        try:
            # Start the mock server process
            self.mock_server_process = subprocess.Popen([
                sys.executable, "mock_yoobic_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for server to start
            for attempt in range(20):  # Wait up to 20 seconds
                try:
                    response = requests.get("http://localhost:5000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Mock server is running on http://localhost:5000")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Mock server failed to start within 20 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error starting mock server: {e}")
            return False
    
    def stop_mock_server(self):
        """Stop the mock server."""
        if self.mock_server_process:
            print("🛑 Stopping mock server...")
            self.mock_server_process.terminate()
            try:
                self.mock_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️  Mock server didn't stop gracefully, killing process...")
                self.mock_server_process.kill()
                self.mock_server_process.wait()
            print("✅ Mock server stopped")
    
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        print("🔍 Checking dependencies...")
        
        required_packages = ["flask", "requests"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install them with: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ All dependencies available")
        return True
    
    def check_main_module(self):
        """Check if the main module is available."""
        print("🔍 Checking main module...")
        
        yoobic_path = Path("../yoobic")
        if not yoobic_path.exists():
            print("❌ Main module not found at ../yoobic")
            print("Please ensure the yoobic module is in the parent directory")
            return False
        
        mission_file = yoobic_path / "src" / "models" / "mission.py"
        if not mission_file.exists():
            print("❌ Mission module not found at ../yoobic/src/models/mission.py")
            return False
        
        print("✅ Main module found")
        return True
    
    async def run_tests(self):
        """Run the test suite."""
        print("🧪 Running mission module tests...")
        
        try:
            # Import and run tests
            from test_mission_module import MissionModuleTester
            tester = MissionModuleTester()
            await tester.run_all_tests()
            
            return True
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            print(f"\n🛑 Received signal {sig}, shutting down...")
            self.running = False
            self.stop_mock_server()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def show_interactive_menu(self):
        """Show interactive menu for development actions."""
        print("\n🔧 Development Menu")
        print("=" * 30)
        print("1. Run full test suite")
        print("2. Start mock server only")
        print("3. Test authentication")
        print("4. Test mission creation")
        print("5. View mock server logs")
        print("6. Reset mock data")
        print("7. Exit")
        print("=" * 30)
        
        choice = input("Enter your choice (1-7): ").strip()
        return choice
    
    async def handle_menu_choice(self, choice):
        """Handle user menu choice."""
        if choice == "1":
            await self.run_tests()
        elif choice == "2":
            print("Mock server is already running at http://localhost:5000")
            print("Visit http://localhost:5000/health to check status")
        elif choice == "3":
            await self.test_authentication()
        elif choice == "4":
            await self.test_mission_creation()
        elif choice == "5":
            self.show_server_logs()
        elif choice == "6":
            self.reset_mock_data()
        elif choice == "7":
            self.running = False
        else:
            print("Invalid choice, please try again")
    
    async def test_authentication(self):
        """Test authentication with mock server."""
        print("🔐 Testing authentication...")
        
        try:
            import requests
            response = requests.post("http://localhost:5000/public/api/auth/login", 
                                   json={"username": "test_user", "password": "test_password"})
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Authentication successful")
                print(f"Token: {data.get('token')[:20]}...")
                print(f"Expires: {data.get('expires')}")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing authentication: {e}")
    
    async def test_mission_creation(self):
        """Test mission creation with mock server."""
        print("🎯 Testing mission creation...")
        
        try:
            import requests
            
            # First authenticate
            auth_response = requests.post("http://localhost:5000/public/api/auth/login", 
                                        json={"username": "test_user", "password": "test_password"})
            
            if auth_response.status_code != 200:
                print("❌ Authentication failed")
                return
            
            token = auth_response.json().get("token")
            
            # Create mission
            mission_data = {
                "title": "Test Mission from Dev Launcher",
                "type": "test",
                "store_id": "store_001",
                "priority": "medium"
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post("http://localhost:5000/public/api/missions", 
                                   json=mission_data, headers=headers)
            
            if response.status_code == 201:
                mission = response.json()
                print("✅ Mission created successfully")
                print(f"Mission ID: {mission.get('mission_id')}")
                print(f"Title: {mission.get('title')}")
                print(f"Status: {mission.get('status')}")
            else:
                print(f"❌ Mission creation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing mission creation: {e}")
    
    def show_server_logs(self):
        """Show recent server logs."""
        print("📋 Mock Server Logs")
        print("=" * 30)
        
        if self.mock_server_process:
            try:
                # This is a simplified log viewer
                print("Mock server is running. Check terminal where it was started for logs.")
                print("Or visit http://localhost:5000/debug/missions to see created missions.")
            except Exception as e:
                print(f"Error accessing logs: {e}")
        else:
            print("Mock server is not running")
    
    def reset_mock_data(self):
        """Reset mock server data."""
        print("🔄 Resetting mock data...")
        
        try:
            import requests
            response = requests.post("http://localhost:5000/debug/reset")
            
            if response.status_code == 200:
                print("✅ Mock data reset successfully")
            else:
                print(f"❌ Failed to reset mock data: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error resetting mock data: {e}")
    
    async def interactive_mode(self):
        """Run in interactive mode."""
        print("🎮 Interactive Development Mode")
        print("Mock server is running in background...")
        
        while self.running:
            try:
                choice = self.show_interactive_menu()
                await self.handle_menu_choice(choice)
                
                if self.running:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n🛑 Exiting interactive mode...")
                break
            except Exception as e:
                print(f"❌ Error in interactive mode: {e}")
                time.sleep(1)
    
    async def main(self):
        """Main development launcher."""
        print("🔧 Mission Module Development Launcher")
        print("=" * 50)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Check dependencies
        if not self.check_dependencies():
            return
        
        # Check main module
        if not self.check_main_module():
            return
        
        try:
            # Start mock server
            if not self.start_mock_server():
                return
            
            # Check command line arguments
            if len(sys.argv) > 1:
                if sys.argv[1] == "--test-only":
                    # Run tests and exit
                    await self.run_tests()
                    return
                elif sys.argv[1] == "--server-only":
                    # Keep server running
                    print("🖥️  Mock server running. Press Ctrl+C to stop.")
                    try:
                        while self.running:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        pass
                    return
            
            # Default: Run tests first, then interactive mode
            print("🚀 Running initial test suite...")
            await self.run_tests()
            
            print("\n🎮 Entering interactive mode...")
            await self.interactive_mode()
            
        finally:
            # Clean up
            self.stop_mock_server()

if __name__ == "__main__":
    launcher = DevLauncher()
    asyncio.run(launcher.main())