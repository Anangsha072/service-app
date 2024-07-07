import os
from flask import Flask, request, jsonify, render_template
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import requests

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    
# Define Hospital model
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    services_offered = db.Column(db.String(200), nullable=True)
    insurance_coverage = db.Column(db.String(200), nullable=True)
    cost_details = db.Column(db.String(200), nullable=True)
    
# Define Doctor model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    hospital = db.relationship('Hospital', backref=db.backref('doctors', lazy=True))
    contact_info = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    availability = db.Column(db.String(100), nullable=True)
    cost_details = db.Column(db.String(200), nullable=True)

# Initialize Bcrypt, Migrate, and CORS
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
CORS(app)

# Sample data creation
def create_sample_data():
    if not Hospital.query.first() and not Doctor.query.first():
        # Create hospitals
        hospital1 = Hospital(name='Apollo Hospital', address='Chennai, Tamil Nadu', phone='1800-123-1010', rating=4.5, services_offered='Emergency Care, Surgery, Pediatrics', insurance_coverage='Government Insurance Schemes, Private Insurance', cost_details='Varies by service')
        hospital2 = Hospital(name='AIIMS', address='New Delhi', phone='1800-123-4567', rating=4.7, services_offered='Emergency Care, Cardiology, Oncology', insurance_coverage='Government Insurance Schemes', cost_details='Varies by service')
        hospital3 = Hospital(name='Fortis Hospital', address='Mumbai, Maharashtra', phone='1800-123-7890', rating=4.2, services_offered='Primary Care, Dermatology, Orthopedics', insurance_coverage='Private Insurance', cost_details='Varies by service')

        # Create doctors
        doctor1 = Doctor(name='Dr. Rajesh Sharma', specialization='Cardiologist', hospital=hospital1, contact_info='rajesh.sharma@example.com', rating=4.8, availability='Mon-Fri, 9am-5pm', cost_details='₹500 for consultation')
        doctor2 = Doctor(name='Dr. Priya Singh', specialization='Pediatrician', hospital=hospital2, contact_info='priya.singh@example.com', rating=4.6, availability='Mon-Sat, 8am-6pm', cost_details='₹400 for consultation')
        doctor3 = Doctor(name='Dr. Anil Kumar', specialization='Orthopedic Surgeon', hospital=hospital3, contact_info='anil.kumar@example.com', rating=4.9, availability='Tue-Thu, 10am-4pm', cost_details='₹600 for consultation')

        # Add data to session
        db.session.add_all([hospital1, hospital2, hospital3, doctor1, doctor2, doctor3])

        # Commit changes
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    if not email or not password or not role:
        return jsonify({'error': 'Email, password, and role are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful', 'user': {'email': user.email, 'role': user.role}}), 200
    return jsonify({'error': 'Invalid email or password'}), 401
@app.route('/hospital/<int:hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    # Example: Fetch hospital details from Google Maps Places API
    api_key = 'your_api_key_here'  # Replace with your actual API key
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={hospital_id}&fields=name,formatted_address,international_phone_number,rating,reviews,photos&type=hospital&key={api_key}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('result', {})
            hospital_name = data.get('name', 'Unknown')
            hospital_address = data.get('formatted_address', 'Unknown')
            hospital_phone = data.get('international_phone_number', 'Unknown')
            hospital_rating = data.get('rating', 0.0)
            hospital_reviews = data.get('reviews', [])
            hospital_photos = [photo['photo_reference'] for photo in data.get('photos', [])]
            insurance_coverage = 'Government and Private Insurance'  # Assuming hardcoded for example
            cost_details = 'Varies by service'  # Assuming hardcoded for example
            
            return jsonify({
                'id': hospital_id,
                'name': hospital_name,
                'address': hospital_address,
                'phone': hospital_phone,
                'rating': hospital_rating,
                'reviews': hospital_reviews,
                'photos': hospital_photos,
                'insurance_coverage': insurance_coverage,
                'cost_details': cost_details
            })
        else:
            return jsonify({'error': 'Failed to fetch hospital details'}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching hospital details: {e}'}), 500

@app.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_doctor_details(doctor_id):
    # Example: Fetch doctor details from an internal database or another API if applicable
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        return jsonify({
            'id': doctor.id,
            'name': doctor.name,
            'specialization': doctor.specialization,
            'hospital': doctor.hospital.name,
            'contact_info': doctor.contact_info,
            'rating': doctor.rating,
            'availability': doctor.availability,
            'cost_details': doctor.cost_details
        })
    else:
        return jsonify({'error': 'Doctor not found'}), 404

@app.route('/search', methods=['GET'])
def search():
    service_type = request.args.get('type')
    location = request.args.get('location')
    radius = request.args.get('radius', 5000)  # Default radius in meters

    if location:
        try:
            latitude, longitude = map(float, location.split(','))
        except ValueError:
            return jsonify({'error': 'Invalid location format. Use latitude,longitude'}), 400

    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    categories = {
        'hospital': 'hospital',
        'doctor': 'doctor',
        'elder_care': 'nursing_home',
        'nurse_service': 'nursing_home',  # Adjust as per Overpass API categories
        'diagnostic_center': 'clinic',  # Adjust as per Overpass API categories
        'emergency': 'hospital_emergency_room'  # Adjust as per Overpass API categories
    }

    if service_type not in categories:
        return jsonify({'error': 'Invalid service type'}), 400

    overpass_url = f"http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="{categories[service_type]}"](around:{radius},{latitude},{longitude});
      way["amenity"="{categories[service_type]}"](around:{radius},{latitude},{longitude});
      relation["amenity"="{categories[service_type]}"](around:{radius},{latitude},{longitude});
    );
    out body;
    >;
    out skel qt;
    """

    print("Overpass Query:", overpass_query)  # Debug statement

    response = requests.get(overpass_url, params={'data': overpass_query})
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from Overpass API'}), 500

    places = response.json().get('elements', [])

    results = []
    for place in places:
        results.append({
            'id': place.get('id'),
            'lat': place.get('lat'),
            'lon': place.get('lon'),
            'tags': place.get('tags', {})
        })

    return jsonify(results)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_sample_data()  # Optional: Populate with sample data
    app.run(debug=True)