# AI Code Review Platform 

## Overview
AI Code Review Platform is a sophisticated web application that leverages machine learning to provide intelligent code analysis and feedback. The platform uses CodeBERT, a pre-trained language model, to evaluate code snippets and offer insights into code quality, potential issues, and best practices.

## Features
- **AI-Powered Code Analysis**: Utilize CodeBERT for intelligent code evaluation
- **GitHub OAuth Authentication**: Secure login with GitHub
- **Real-time Code Feedback**: Instant insights and suggestions
- **User-Friendly Interface**: Clean and intuitive React.js frontend
- **Comprehensive Code Review**: Checks for coding standards, potential issues, and best practices

##  Tech Stack
- **Backend**: 
  - FastAPI
  - Python
  - CodeBERT (Hugging Face Transformers)
  - Motor (Async MongoDB driver)
- **Frontend**: 
  - Next.js
  - React
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
git clone https://github.com/yourusername/ai-code-review-platform.git
cd ai-code-review-platform/backend
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

## 🖥 Running the Application

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

## How It Works
1. Users log in via GitHub OAuth
2. Upload a code snippet
3. CodeBERT analyzes the code
4. Receive instant feedback on:
   - Code quality score
   - Potential issues
   - Best practice suggestions

## Security
- OAuth 2.0 authentication
- Secure token management
- Environment variable configuration

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact
prekshau03@gmail.com
Preksha Upadhyay 


