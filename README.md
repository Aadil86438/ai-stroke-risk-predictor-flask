# Stroke Risk Prediction System

An AI-powered web application that predicts stroke risk based on user health metrics. Built with Flask, TensorFlow, and modern web technologies.

## Features

- **User Authentication**: Secure login and registration system
- **AI Risk Assessment**: Deep Neural Network model for stroke risk prediction
- **Interactive Dashboard**: Real-time visualization of health metrics and risk trends
- **Health Reports**: Downloadable PDF reports with personalized recommendations
- **Modern UI**: Clean and responsive design using Tailwind CSS

## Technologies Used

- **Backend**: Flask, SQLite
- **AI/ML**: TensorFlow, NumPy, Scikit-learn
- **Frontend**: HTML, Tailwind CSS, Chart.js
- **Data Analysis**: SHAP (for AI explainability)
- **Documentation**: PDF generation with ReportLab

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stroke-risk-prediction.git
cd stroke-risk-prediction
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py
```

5. Access the application:
Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
stroke-risk-prediction/
├── app.py              # Main Flask application
├── model.py            # AI model implementation
├── requirements.txt    # Project dependencies
├── static/            
│   ├── css/           # Custom CSS files
│   ├── js/            # JavaScript files
│   └── models/        # Saved AI models
└── templates/         
    ├── base.html      # Base template
    ├── index.html     # Home page
    ├── login.html     # Login page
    ├── register.html  # Registration page
    ├── dashboard.html # User dashboard
    ├── predict.html   # Risk assessment form
    └── report.html    # Health report page
```

## Usage

1. Register a new account or login with existing credentials
2. Navigate to "New Assessment" to input your health metrics
3. View your risk assessment and recommendations on the dashboard
4. Generate and download detailed health reports
5. Track your health progress over time with interactive charts

## AI Model

The stroke risk prediction model is a Deep Neural Network built with TensorFlow. It:

- Takes 4 input features: age, weight, blood sugar, and glucose level
- Uses multiple dense layers with dropout for regularization
- Achieves >90% accuracy on the test set
- Provides explainable predictions using SHAP values

## Security Note

This is a demonstration project. In a production environment, you should:

- Use proper password hashing
- Implement CSRF protection
- Use environment variables for sensitive data
- Add input validation and sanitization
- Implement rate limiting
- Use HTTPS

## License

MIT License - feel free to use this project for learning and development. 