# YOOBIC Development Tools

Development and testing tools for YOOBIC Public API.

## Overview

This repository contains the development tools needed to build, test, and debug the YOOBIC Public API.

## Project Structure

```
yoobic-utils/
├── mock_yoobic_server.py       # Mock YOOBIC API server
├── test_mission_module.py      # Comprehensive test suite
├── dev_launcher.py             # Development launcher with interactive menu
├── requirements-dev.txt        # Development dependencies
├── docker-compose.yml          # Docker setup for testing
└── README.md                   # This file
```

## Prerequisites

- Python 3.8+
- The main `viam-yoobic/` module repository in the parent directory
- Internet connection for installing dependencies

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Ensure Main Module is Available

The development tools expect the main module to be in the parent directory:

```
project-root/
├── viam-yoobic/               # Main module
│   ├── src/
│   │   └── models/
│   │       └── mission.py
│   └── ...
└── yoobic-utils/              # This directory
    ├── mock_yoobic_server.py
    └── ...
```

### 3. Run Development Environment

```bash
python dev_launcher.py
```

This will:
1. Start the mock YOOBIC server
2. Run the full test suite
3. Enter interactive development mode

## Components

### Mock YOOBIC Server (`mock_yoobic_server.py`)

A Flask-based mock server that simulates the YOOBIC API for development and testing.

**Features:**
- JWT authentication simulation
- Mission CRUD operations
- Store management
- Debug endpoints

**Endpoints:**
- `POST /public/api/auth/login` - Authentication
- `GET /public/api/missions` - Get missions
- `POST /public/api/missions` - Create mission
- `POST /public/api/missions/<id>/validate` - Validate mission
- `GET /health` - Health check
- `POST /debug/reset` - Reset mock data
- `GET /debug/missions` - View all missions

**Test Credentials:**
- Username: `test_user`
- Password: `test_password`

### Test Suite (`test_mission_module.py`)

Comprehensive test suite for the mission module.

**Test Coverage:**
- Module initialization
- Authentication
- Connection testing
- Mission creation
- Rule evaluation
- Sync operations
- Sensor readings
- Statistics

**Usage:**
```bash
python test_mission_module.py
```

### Development Launcher (`dev_launcher.py`)

Interactive development environment that coordinates the mock server and testing.

**Features:**
- Automatic mock server startup
- Full test suite execution
- Interactive development menu
- Individual test execution
- Mock data management

**Usage:**
```bash
# Full interactive mode
python dev_launcher.py

# Run tests only
python dev_launcher.py --test-only

# Start server only
python dev_launcher.py --server-only
```

**Interactive Menu:**
1. Run full test suite
2. Start mock server only
3. Test authentication
4. Test mission creation
5. View mock server logs
6. Reset mock data
7. Exit

## Testing Workflow

### 1. Start Development Environment

```bash
python dev_launcher.py
```

### 2. Run Tests

The launcher will automatically run the full test suite on startup. You can also run individual tests through the interactive menu.

### 3. Debug Issues

- Use the interactive menu to test specific functionality
- Check mock server logs for API calls
- Reset mock data between test runs
- View created missions at `http://localhost:5000/debug/missions`

### 4. Iterate on Module

After making changes to the main module:

1. Restart the development launcher
2. Run the test suite again
3. Use the interactive menu to test specific features

## Configuration Examples

### Mock Server Configuration

The test suite uses this configuration for the mock server:

```json
{
  "platform": {
    "type": "yoobic",
    "base_url": "http://localhost:5000/public/api",
    "authentication": {
      "method": "username_password",
      "username": "test_user",
      "password": "test_password"
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
        "priority": "high"
      }
    }
  ]
}
```

## Docker Setup

For containerized testing:

```bash
docker-compose up
```

This will start both the mock server and run the tests in containers.

## Development Tips

### Adding New Tests

1. Add test methods to `MissionModuleTester` class
2. Follow the naming convention: `test_<functionality>()`
3. Use `self.log_result()` to track test results
4. Handle exceptions gracefully

### Mock Server Extensions

1. Add new endpoints to `mock_yoobic_server.py`
2. Update mock data structure as needed
3. Add corresponding tests to validate new functionality

### Debugging Authentication

1. Use the interactive menu option "Test authentication"
2. Check token generation and validation
3. Verify API endpoint authentication requirements

### Performance Testing

1. Adjust `sync_interval` in test configuration
2. Monitor mock server logs for API call patterns
3. Test with multiple concurrent missions

## Troubleshooting

### Mock Server Won't Start

1. Check if port 5000 is already in use
2. Verify Flask is installed: `pip install flask`
3. Check firewall settings

### Tests Fail with Import Errors

1. Ensure main module is in correct location (`../yoobic/`)
2. Check Python path configuration
3. Verify all dependencies are installed

### Authentication Issues

1. Verify mock server is running: `curl http://localhost:5000/health`
2. Check test credentials in mock server
3. Ensure token generation is working properly

### Module Configuration Errors

1. Check JSON syntax in test configuration
2. Verify all required fields are present
3. Check field types match expectations

## Production Transition

When ready to use real YOOBIC credentials:

1. Update configuration to use real YOOBIC API URLs
2. Replace mock credentials with real ones
3. Test authentication with real API
4. Gradually migrate from mock to real data sources

## Contributing

1. Add tests for new functionality
2. Update mock server for new API endpoints
3. Document new features in README
4. Test thoroughly with both mock and real APIs

## Support

For issues with the development tools:
1. Check the troubleshooting section
2. Review test output for specific error messages
3. Verify mock server logs for API call details
4. Create an issue with detailed error information