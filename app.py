from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import json
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
from model import stroke_model
import qrcode
from io import BytesIO
import base64
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.context_processor
def inject_year():
    return {'current_year': datetime.utcnow().year}

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Float, nullable=False)
    hypertension = db.Column(db.Integer, nullable=False)
    heart_disease = db.Column(db.Integer, nullable=False)
    ever_married = db.Column(db.String(5), nullable=False)
    work_type = db.Column(db.String(20), nullable=False)
    residence_type = db.Column(db.String(10), nullable=False)
    avg_glucose_level = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    smoking_status = db.Column(db.String(20), nullable=False)
    stroke_risk = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:  # In production, use proper password hashing
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        new_user = User(name=name, email=email, password=password)  # In production, hash the password
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).all()
    return render_template('dashboard.html', assessments=assessments)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        # Get form data
        features = {
            'patient_name': request.form.get('patient_name'),
            'gender': request.form.get('gender'),
            'age': float(request.form.get('age')),
            'hypertension': int(request.form.get('hypertension')),
            'heart_disease': int(request.form.get('heart_disease')),
            'ever_married': request.form.get('ever_married'),
            'work_type': request.form.get('work_type'),
            'Residence_type': request.form.get('residence_type'),
            'avg_glucose_level': float(request.form.get('avg_glucose_level')),
            'bmi': float(request.form.get('bmi')),
            'smoking_status': request.form.get('smoking_status')
            
        }
        
        # Get prediction from model
        prediction_features = features.copy()
        del prediction_features['patient_name']  # Remove patient name as it's not needed for prediction
        
        stroke_risk = stroke_model.predict(prediction_features)
        
        # Save assessment
        assessment = Assessment(
            user_id=current_user.id,
            patient_name=features['patient_name'],
            gender=features['gender'],
            age=features['age'],
            hypertension=features['hypertension'],
            heart_disease=features['heart_disease'],
            ever_married=features['ever_married'],
            work_type=features['work_type'],
            residence_type=features['Residence_type'],
            avg_glucose_level=features['avg_glucose_level'],
            bmi=features['bmi'],
            smoking_status=features['smoking_status'],
            stroke_risk=stroke_risk
        )
        db.session.add(assessment)
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    return render_template('predict.html')

def generate_qr_code(assessment):
    # Create QR code data
    qr_data = {
        'patient_name': assessment.patient_name,
        'gender': assessment.gender,
        'age': assessment.age,
        'hypertension': assessment.hypertension,
        'heart_disease': assessment.heart_disease,
        'ever_married': assessment.ever_married,
        'work_type': assessment.work_type,
        'residence_type': assessment.residence_type,
        'avg_glucose_level': assessment.avg_glucose_level,
        'bmi': assessment.bmi,
        'smoking_status': assessment.smoking_status,
        'stroke_risk': f"{assessment.stroke_risk:.2%}",
        'date': assessment.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Convert data to JSON string
    qr_json = json.dumps(qr_data)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_json)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffered = BytesIO()
    qr_image.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return qr_base64

def generate_recommendations(assessment):
    recommendations = {
        'lifestyle': [],
        'medical': []
    }
    
    # Age-based recommendations
    if assessment.age > 60:
        recommendations['lifestyle'].append("Regular physical activity (20-30 minutes daily)")
        recommendations['medical'].append("Annual comprehensive health check-up")
    elif assessment.age > 40:
        recommendations['lifestyle'].append("Moderate exercise (30 minutes, 5 days/week)")
        recommendations['medical'].append("Biannual health check-up")
    else:
        recommendations['lifestyle'].append("Regular exercise (30 minutes daily)")
        recommendations['medical'].append("Annual health check-up")
    
    # Hypertension-based recommendations
    if assessment.hypertension:
        recommendations['lifestyle'].append("Low-sodium diet")
        recommendations['lifestyle'].append("Stress management techniques")
        recommendations['medical'].append("Daily blood pressure monitoring")
    
    # Heart disease-based recommendations
    if assessment.heart_disease:
        recommendations['lifestyle'].append("Heart-healthy diet")
        recommendations['medical'].append("Regular cardiac check-ups")
    
    # BMI-based recommendations
    if assessment.bmi > 30:
        recommendations['lifestyle'].append("Weight management program")
        recommendations['lifestyle'].append("Portion control and balanced diet")
    elif assessment.bmi < 18.5:
        recommendations['lifestyle'].append("Nutritional counseling")
        recommendations['lifestyle'].append("Healthy weight gain plan")
    
    # Glucose level-based recommendations
    if assessment.avg_glucose_level > 140:
        recommendations['lifestyle'].append("Low-glycemic diet")
        recommendations['medical'].append("Regular glucose monitoring")
    
    # Smoking status-based recommendations
    if assessment.smoking_status == 'smokes':
        recommendations['lifestyle'].append("Smoking cessation program")
        recommendations['medical'].append("Lung function assessment")
    elif assessment.smoking_status == 'formerly smoked':
        recommendations['lifestyle'].append("Avoid secondhand smoke")
        recommendations['medical'].append("Regular lung health check")
    
    # High risk specific recommendations
    if assessment.stroke_risk > 0.5:
        recommendations['lifestyle'].append("Strict adherence to prescribed medications")
        recommendations['medical'].append("Monthly follow-up with healthcare provider")
        recommendations['medical'].append("Emergency action plan for stroke symptoms")
    
    return recommendations

@app.route('/report/<int:assessment_id>')
@login_required
def report(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    
    # Generate QR code
    qr_code = generate_qr_code(assessment)
    
    # Generate personalized recommendations
    recommendations = generate_recommendations(assessment)
    
    return render_template('report.html', 
                         assessment=assessment, 
                         qr_code=qr_code,
                         recommendations=recommendations)

@app.route('/clear-assessments')
@login_required
def clear_assessments():
    # Delete all assessments for the current user
    Assessment.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('All your assessment data has been cleared.')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/sos', methods=['GET', 'POST'])
@login_required
def sos():
    if request.method == 'POST':
        # Get user's location from the request
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Location data not provided'}), 400
            
        # Use Google Places API to find nearby hospitals
        api_key = 'YOUR_GOOGLE_MAPS_API_KEY'  # You'll need to get this from Google Cloud Console
        url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=5000&type=hospital&key={api_key}'
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == 'OK':
                hospitals = []
                for place in data['results']:
                    hospital = {
                        'name': place['name'],
                        'address': place.get('vicinity', 'Address not available'),
                        'rating': place.get('rating', 'No rating'),
                        'distance': calculate_distance(float(latitude), float(longitude), 
                                                     place['geometry']['location']['lat'],
                                                     place['geometry']['location']['lng'])
                    }
                    hospitals.append(hospital)
                
                return jsonify({'hospitals': hospitals})
            else:
                return jsonify({'error': 'No hospitals found'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return render_template('sos.html')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    return round(geodesic((lat1, lon1), (lat2, lon2)).kilometers, 2)
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)


