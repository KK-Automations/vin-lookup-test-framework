# vin-lookup-test-framework
Auto VIN Search

# VIN Lookup Test Automation Framework

## Project Overview
This test automation framework provides a comprehensive solution for decoding Vehicle Identification Numbers (VINs) using multiple open-source and API-based services.

## Features
- Multi-API VIN Decoding Support
- Supports NHTSA, MarketCheck, and CarMD APIs
- Comprehensive Test Coverage
- Logging and Error Handling
- Allure Reporting Integration

## Prerequisites
- Python 3.8+
- pip
- Virtual Environment (recommended)

## Getting Started

### Installation

1. Clone the Repository
```bash
git clone https://github.com/yourusername/vin-lookup-test-framework.git
cd vin-lookup-test-framework
```

2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Set Up Environment Variables
Create a `.env` file in the project root with:
```
MARKETCHECK_API_KEY=your_marketcheck_api_key
CARMD_API_KEY=your_carmd_api_key
CARMD_PARTNER_TOKEN=your_carmd_partner_token
```

### Running the Application

1. Start the Flask Application
```bash
python -m app
```

2. Access the Application
Open your browser and navigate to `http://127.0.0.1:5000`.

## Running Tests
```bash
# Run all tests
pytest tests/

# Run with Allure reporting
pytest --alluredir=allure-results
allure serve allure-results
```

## Project Structure
The project is organized as follows:

```
vin-lookup-test-framework/
├── .env                     # Environment variables file (not committed to version control)
├── .gitignore               # Specifies files and directories to ignore in version control
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies for the project
├── setup.py                 # Setup script for packaging and installation
├── .github/
│   └── workflows/
│       └── python-tests.yml # GitHub Actions workflow for running tests
├── config/                  # Placeholder for configuration files (e.g., settings, API configs)
├── src/
│   └── vin_lookup/
│       ├── __init__.py      # Marks the directory as a Python package
│       ├── carapi_auth.py   # Handles authentication with CarAPI
│       └── vin_decoder.py   # Contains the VIN decoding logic for multiple APIs
├── testenv/                 # Virtual environment directory (excluded from version control)
└── tests/
    ├── __init__.py          # Marks the directory as a Python package
    ├── test_carapi_integration.py # Integration tests for CarAPI
    └── __pycache__/         # Compiled Python files (ignored in version control)
```

## Collaboration

### Contributing
We welcome contributions! To contribute:
1. Fork the Repository
2. Create a Feature Branch
3. Commit Your Changes
4. Push to Your Branch
5. Create a Pull Request

### Reporting Issues
If you encounter any issues, please open an issue in the GitHub repository with detailed information.

### Code of Conduct
Please adhere to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact
For questions or collaboration, please contact:
- **Author**: krishnaharshap
- **Email**: krishnaharshap11@gmail.com
- **GitHub**: [krishnaharshap](https://github.com/krishnaharshap)
