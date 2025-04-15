Python Code Analysis & Bug Detection Platform

## Overview

It is a sophisticated web application that leverages machine learning to provide intelligent Python code analysis and automated bug detection. Built on the powerful PyBugHunt, it evaluates code snippets and offers insights into code quality, potential issues, and best practices with actionable fix suggestions.

## Key Features

- **AI-Powered Code Analysis**: Utilize pybughunt for intelligent Python code evaluation
- **GitHub OAuth Authentication**: Secure login with GitHub credentials
- **Real-time Code Feedback**: Instant insights and suggestions for your code
- **User-Friendly Interface**: Clean and intuitive React.js frontend with Tailwind CSS
- **Comprehensive Code Review**: Checks for syntax errors, logic issues, and coding standards
- **Fix Suggestions**: Get specific recommendations to improve your code
- **Quality Score Visualization**: Visual representation of code quality with percentage rating

## Tech Stack

- **Backend**:
  - FastAPI
  - Python
  - PyBugHunt (Custom code analysis library)
  - Motor (Async MongoDB driver)
- **Frontend**:
  - Next.js
  - React with TypeScript
  - Tailwind CSS
- **Authentication**:
  - Auth0
  - GitHub OAuth
- **Database**:
  - MongoDB

## Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB
- Auth0 Account
- GitHub Developer Account

## Installation

### Backend Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/pybughunt.git
cd pybughunt/backend
```

2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure `.env` file

```
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_CALLBACK_URL=http://localhost:8000/auth/callback
MONGO_URI=your_mongodb_connection_string
```

### Frontend Setup

1. Navigate to frontend directory

```bash
cd ../frontend
npm install
```

2. Create `.env.local` file

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Start Frontend

```bash
cd frontend
npm run dev
```

Access the application at http://localhost:3000

## How It Works

1. **Authentication**: Users log in via GitHub OAuth
2. **Code Input**: Users paste their Python code snippet into the editor
3. **Analysis**: The PyBugHunt engine analyzes the code for various issues
4. **Results Display**: Users receive detailed feedback including:
   - Overall code quality score (0-100%)
   - Syntax errors with locations and descriptions
   - Logic errors and potential bugs
   - Code quality issues and best practice violations
   - Specific fix suggestions for each category of issue

## Code Analysis Components

PyBugHunt performs analysis on three primary levels:

### Syntax Analysis

- Identifies syntax errors that would prevent code from running
- Pinpoints exact locations of syntax issues
- Provides clear explanations of errors

### Logic Analysis

- Detects potential logic errors and bugs
- Identifies inefficient algorithms
- Finds potential edge cases that might cause issues

### Quality Analysis

- Evaluates code against PEP 8 standards
- Checks for readability and maintainability issues
- Suggests improvements for code structure and organization

## Project Structure

```
/pybughunt
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── pybughunt_integration.py
│   │   │   └── test_review.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   └── review.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx
│   │   ├── utils/
│   │   │   ├── api.ts
│   │   │   └── auth.ts
│   │   └── ...
│   ├── package.json
│   └── ...
└── README.md
```

## Interface Components

### User Authentication

- GitHub OAuth integration for secure authentication
- User profile display with avatar
- Session management and secure logout

### Code Editor

- Clean, syntax-highlighted code input area
- Language selection dropdown (currently supporting Python)
- One-click analysis button

### Analysis Results

- Visual quality score with color-coded indicator
- Categorized issue display:
  - Syntax errors (red)
  - Logic errors (yellow)
  - Code quality issues (purple)
- Fix suggestions in an easy-to-read format
- Issue summary statistics

## Security Considerations

- OAuth 2.0 authentication with GitHub
- Secure token management
- Environment variable configuration for sensitive data
- HTTPS recommended for production deployment

## Error Handling

- Graceful handling of API errors
- User-friendly error messages
- Fallback options for API unavailability

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- Support for additional programming languages
- Integration with GitHub repositories for automatic code review
- Real-time collaborative code review features
- Custom rule creation for organization-specific code standards
- Integration with popular IDEs through plugins
- Historical analysis tracking to measure improvement
- Team collaboration features for educational environments

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Lead: Preksha Upadhyay
Email: prekshau03@gmail.com
