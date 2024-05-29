from flask import Flask, render_template, redirect, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.distance import geodesic

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample user data (replace with database)
users = {
    'user1': {
        'username': 'user1',
        'email': 'user1@example.com',
        'password_hash': generate_password_hash('password')
    }
}

# Sample hospital data for each state
hospital_data = {
    "Delhi": [
        {"name": "City Hospital", "latitude": 28.7041, "longitude": 77.1025},
        {"name": "Delhi Hospital", "latitude": 28.6139, "longitude": 77.2090},
    ],
    "Mumbai": [
        {"name": "Mumbai General Hospital", "latitude": 19.0760, "longitude": 72.8777},
        {"name": "Mumbai Medical Center", "latitude": 19.0765, "longitude": 72.8758},
    ],
    "Kolkata": [
        {"name": "Apollo Gleneagles Hospital", "latitude": 22.5382, "longitude": 88.3685},
        {"name": "Medica Superspecialty Hospital", "latitude": 22.5524, "longitude": 88.4072}
    ],
    "Chennai": [
        {"name": "Apollo Hospital", "latitude": 13.0317, "longitude": 80.2518},
        {"name": "Fortis Malar Hospital", "latitude": 13.0506, "longitude": 80.2148}
    ],
    "Hyderabad": [
        {"name": "Apollo Hospital", "latitude": 17.4159, "longitude": 78.4405},
        {"name": "Care Hospitals", "latitude": 17.4435, "longitude": 78.4011}
    ],
    "Pune": [
        {"name": "Deenanath Mangeshkar Hospital", "latitude": 18.5096, "longitude": 73.8245},
        {"name": "Ruby Hall Clinic", "latitude": 18.5214, "longitude": 73.8745}
    ]
}

# Sample education data for each city
education_data = {
    "Delhi": {
        "schools": [
            {"name": "Delhi Public School", "admission_window": "Jan-Mar", "fee_structure": "INR 100,000 per year"},
            {"name": "Modern School", "admission_window": "Feb-Apr", "fee_structure": "INR 120,000 per year"},
        ],
        "second_hand_materials": [
            {"item": "Laptop", "price": "INR 20,000"},
            {"item": "Textbooks", "price": "INR 500"},
        ],
        "tuition_centers": [
            {"subject": "Mathematics", "center_name": "Maths Academy", "teacher": "Mr. Sharma"},
            {"subject": "Science", "center_name": "Science Hub", "teacher": "Ms. Verma"},
        ],
        "activity_centers": [
            {"type": "Arts", "center_name": "Art Studio"},
            {"type": "Music", "center_name": "Music Academy"},
            {"type": "Sports", "center_name": "Sports Complex"},
        ],
        "training_centers": [
            {"name": "Tech Training Institute"},
            {"name": "Job Aid Center"}
        ]
    },
     "Kolkata": {
        "schools": [
            {"name": "La Martiniere", "admission_window": "Jan-Mar", "fees": "₹55,000/year"},
            {"name": "Don Bosco", "admission_window": "Feb-Apr", "fees": "₹65,000/year"}
        ],
        "learning_materials": [
            {"item": "Used Textbooks", "price": "₹400"},
            {"item": "Second-hand Laptops", "price": "₹18,000"}
        ],
        "tuition_centers": [
            {"name": "Bright Tuition", "subject": "Math", "teacher": "Mr. Das", "location": "Park Street"},
            {"name": "LearnFast Tuition", "subject": "Science", "teacher": "Ms. Sen", "location": "Salt Lake"}
        ],
        "activity_centers": [
            {"name": "Kolkata Dance Academy", "type": "Dance", "location": "Gariahat"},
            {"name": "Artistic Minds", "type": "Art", "location": "New Town"}
        ],
        "training_centers": [
            {"name": "SkillEdge", "type": "IT", "location": "Sector V"},
            {"name": "ProBusiness", "type": "Business" }
        ]
    },
    "Pune": {
        "schools": [
            {"name": "The Bishop's School", "admission_window": "Feb-Mar", "fees": "₹70,000/year"},
            {"name": "Vibgyor High", "admission_window": "Jan-Feb", "fees": "₹80,000/year"}
        ],
        "learning_materials": [
            {"item": "Used Textbooks", "price": "₹600"},
            {"item": "Second-hand Laptops", "price": "₹25,000"}
        ],
        "tuition_centers": [
            {"name": "MathGenius Tuition", "subject": "Math", "teacher": "Mr. Patel", "location": "Kothrud"},
            {"name": "ScienceWiz Tuition", "subject": "Science", "teacher": "Ms. Deshmukh", "location": "Aundh"}
        ],
        "activity_centers": [
            {"name": "Pune Music Academy", "type": "Music", "location": "Kalyani Nagar"},
            {"name": "Creative Arts Studio", "type": "Art", "location": "Wakad"}
        ],
        "training_centers": [
            {"name": "TechBoost", "type": "IT", "location": "Hinjewadi"},
            {"name": "BizPro", "type": "Business", "location": "Magarpatta"}
        ]
    },
    # Add education data for other cities similarly
}
transportation_data = {
    "Delhi": {
        "ola_uber": {
            "auto": {"min_fare": "₹30", "per_km_charge": "₹8", "waiting_charge": "₹1/minute"},
            "two_wheeler": {"min_fare": "₹25", "per_km_charge": "₹6", "waiting_charge": "₹1/minute"},
            "car": {"min_fare": "₹50", "per_km_charge": "₹10", "waiting_charge": "₹2/minute"}
        },
        "vehicle_service_centers": [
            {"name": "Car Care Center", "location": "Connaught Place"},
            {"name": "Bike Zone", "location": "Karol Bagh"}
        ],
        "bus_stations": [
            {"name": "ISBT Kashmere Gate", "arrival_timings": "Every 15 minutes"},
            {"name": "Sarai Kale Khan", "arrival_timings": "Every 20 minutes"}
        ],
        "vehicle_service_contacts": [
            {"service": "Car Repair", "contact": "9876543210"},
            {"service": "Bike Repair", "contact": "9876543211"}
        ],
        "buy_sell_vehicles": [
            {"type": "Cars", "website": "www.delhicars.com"},
            {"type": "Bikes", "website": "www.delhibikes.com"}
        ]
    },
    "Kolkata": {
        "ride_sharing": [
            {"service": "Ola", "cost": "₹130 for 10km"},
            {"service": "Uber", "cost": "₹120 for 10km"}
        ],
        "service_centers": [
            {"name": "Kolkata Auto Repair", "location": "Park Street"},
            {"name": "Vehicle Care", "location": "Salt Lake"}
        ],
        "bus_stations": [
            {"station": "Esplanade", "arrival_timings": "Every 10 mins"},
            {"station": "Howrah", "arrival_timings": "Every 20 mins"}
        ],
        "vehicle_services": [
            {"provider": "Speedy Service", "contact": "2233445566"},
            {"provider": "OnRoad Help", "contact": "1122334455"}
        ],
        "buy_sell_vehicles": [
            {"type": "Used Cars", "link": "https://example.com/kolkata/used-cars"},
            {"type": "Second-hand Bikes", "link": "https://example.com/kolkata/used-bikes"}
        ]
    },
}
finance_data = {
    "Delhi": {
        "banks": [
            {"bank": "SBI", "interest_rate": "7.5% for housing loans"},
            {"bank": "HDFC", "interest_rate": "8.0% for housing loans"}
        ],
        "tax_saving_plans": [
            {"plan": "ELSS", "recommendation": "Invest in ELSS for tax saving"},
            {"plan": "PPF", "recommendation": "Open a PPF account"}
        ]
    },
    "Kolkata": {
        "banks": [
            {"bank": "ICICI", "interest_rate": "7.8% for housing loans"},
            {"bank": "Axis Bank", "interest_rate": "7.9% for housing loans"}
        ],
        "tax_saving_plans": [
            {"plan": "NPS", "recommendation": "Invest in NPS for retirement"},
            {"plan": "FD", "recommendation": "5-year FD for tax saving"}
        ]
    },
    # Add similar data for other cities
}
gov_services_data = {
    "Delhi": {
        "nearest_govt_offices": [
            {"service": "Aadhar", "location": "Connaught Place"},
            {"service": "Land Registration", "location": "Patel Nagar"}
        ],
        "passport_centers": [
            {"center_name": "PSK Connaught Place", "visa_consultant": "VisaEasy", "contact": "9876543210"},
            {"center_name": "PSK Janakpuri", "visa_consultant": "VisaAssist", "contact": "9876543211"}
        ],
        "housing_plan_approvals": [
            {"center_name": "DDA Office", "services": "Plan Approval, Borewell Approval", "contact": "1234567890"}
        ],
        "ration_card_centers": [
            {"center_name": "Ration Card Office", "location": "Rajouri Garden", "contact": "1122334455"}
        ],
        "govt_schemes": [
            {"scheme_name": "PM-KISAN", "beneficiaries": "Farmers", "details": "Income support of ₹6,000/year"},
            {"scheme_name": "Beti Bachao Beti Padhao", "beneficiaries": "Women", "details": "Support for girl education"}
        ],
        "pension_pf_gratuity_consultants": [
            {"name": "Retirement Solutions", "contact": "9876543220"},
            {"name": "PF Assist", "contact": "9876543221"}
        ]
    },
    "Kolkata": {
        "nearest_govt_offices": [
            {"service": "Aadhar", "location": "Salt Lake"},
            {"service": "Land Registration", "location": "Alipore"}
        ],
        "passport_centers": [
            {"center_name": "PSK Salt Lake", "visa_consultant": "Global Visa", "contact": "9830012345"},
            {"center_name": "PSK Park Street", "visa_consultant": "Visa Pros", "contact": "9830012346"}
        ],
        "housing_plan_approvals": [
            {"center_name": "KMC Office", "services": "Plan Approval, Water Supply Approval", "contact": "9000000000"}
        ],
        "ration_card_centers": [
            {"center_name": "Ration Card Office", "location": "Gariahat", "contact": "9000000001"}
        ],
        "govt_schemes": [
            {"scheme_name": "Kanyashree", "beneficiaries": "Women", "details": "Financial aid for girl students"},
            {"scheme_name": "Krishak Bandhu", "beneficiaries": "Farmers", "details": "Income support for farmers"}
        ],
        "pension_pf_gratuity_consultants": [
            {"name": "Retirement Advisory", "contact": "9830012347"},
            {"name": "Pension Planner", "contact": "9830012348"}
        ]
    },
    "Pune": {
        "nearest_govt_offices": [
            {"service": "Aadhar", "location": "Shivaji Nagar"},
            {"service": "Land Registration", "location": "Kothrud"}
        ],
        "passport_centers": [
            {"center_name": "PSK Pune", "visa_consultant": "Visa Consultants", "contact": "9922445566"},
            {"center_name": "PSK Pimpri", "visa_consultant": "Travel Visa", "contact": "9922445567"}
        ],
        "housing_plan_approvals": [
            {"center_name": "PMC Office", "services": "Plan Approval, Borewell Approval", "contact": "9922445568"}
        ],
        "ration_card_centers": [
            {"center_name": "Ration Card Office", "location": "Koregaon Park", "contact": "9922445569"}
        ],
        "govt_schemes": [
            {"scheme_name": "Balika Samridhi Yojana", "beneficiaries": "Women", "details": "Scholarship for girl child"},
            {"scheme_name": "Pradhan Mantri Fasal Bima Yojana", "beneficiaries": "Farmers", "details": "Crop insurance"}
        ],
        "pension_pf_gratuity_consultants": [
            {"name": "Pension Services", "contact": "9922445570"},
            {"name": "Gratuity Assist", "contact": "9922445571"}
        ]
    },
    # Add government services data for other cities similarly
}
housing_data = {
    "Delhi": {
        "services": [
            {"service": "Electrician", "contact": "Rahul - 9876543210"},
            {"service": "Plumber", "contact": "Amit - 9876543211"},
            {"service": "Carpenter", "contact": "Vijay - 9876543212"},
            {"service": "Painter", "contact": "Ravi - 9876543213"}
        ],
        "community_helpers": [
            {"name": "Local Police", "contact": "100"},
            {"name": "Fire Brigade", "contact": "101"},
            {"name": "Ambulance", "contact": "102"}
        ],
        "suppliers": [
            {"item": "Food", "contact": "FreshMart - 9876543214"},
            {"item": "Water", "contact": "AquaPure - 9876543215"}
        ],
        "maids": [
            {"name": "Sita", "contact": "9876543216"},
            {"name": "Gita", "contact": "9876543217"}
        ],
        "packers_movers": [
            {"name": "SafeMove Packers", "contact": "9876543218"},
            {"name": "QuickShift Movers", "contact": "9876543219"}
        ],
        "real_estate": [
            {"type": "Rent", "contact": "HouseRentals - 9876543220"},
            {"type": "Purchase", "contact": "BuyHomes - 9876543221"}
        ]
    },
    "Kolkata": {
        "housing_services": [
            {"service": "Electrician", "contact": "Mr. Dutta - 9090909090"},
            {"service": "Plumber", "contact": "Mr. Roy - 8080808080"},
            {"service": "Carpenter", "contact": "Mr. Sen - 7070707070"},
            {"service": "Painter", "contact": "Mr. Ghosh - 6060606060"}
        ],
        "community_helpers": [
            {"service": "Local Police", "contact": "100"},
            {"service": "Fire Brigade", "contact": "101"},
            {"service": "Ambulance", "contact": "102"}
        ],
        "suppliers": [
            {"item": "Food", "contact": "FoodSupplier1 - 1234567890"},
            {"item": "Water", "contact": "WaterSupplier1 - 0987654321"}
        ],
        "maids": [
            {"name": "Kamala", "contact": "1122334455"},
            {"name": "Saraswati", "contact": "5566778899"}
        ],
        "packers_movers": [
            {"name": "Kolkata Packers", "contact": "9988776655"},
            {"name": "Movers & Shakers", "contact": "7766554433"}
        ],
        "real_estate": [
            {"type": "Rent", "contact": "RentalsKolkata - 8899001122"},
            {"type": "Purchase", "contact": "BuyKolkata - 6677889900"}
        ]
    },
    "Pune": {
        "housing_services": [
            {"service": "Electrician", "contact": "Mr. Joshi - 9876543210"},
            {"service": "Plumber", "contact": "Mr. Kale - 9876543211"},
            {"service": "Carpenter", "contact": "Mr. Desai - 9876543212"},
            {"service": "Painter", "contact": "Mr. Patil - 9876543213"}
        ],
        "community_helpers": [
            {"service": "Local Police", "contact": "100"},
            {"service": "Fire Brigade", "contact": "101"},
            {"service": "Ambulance", "contact": "102"}
        ],
        "suppliers": [
            {"item": "Food", "contact": "FreshMart - 9876543214"},
            {"item": "Water", "contact": "AquaPure - 9876543215"}
        ],
        "maids": [
            {"name": "Lakshmi", "contact": "9876543216"},
            {"name": "Radha", "contact": "9876543217"}
        ],
        "packers_movers": [
            {"name": "SafeMove Packers", "contact": "9876543218"},
            {"name": "QuickShift Movers", "contact": "9876543219"}
        ],
        "real_estate": [
            {"type": "Rent", "contact": "HouseRentals - 9876543220"},
            {"type": "Purchase", "contact": "BuyHomes - 9876543221"}
        ]
    },
    # Add housing data for other cities similarly
}


# Function to calculate distance between two locations
def calculate_distance(user_location, hospital_location):
    return geodesic(user_location, hospital_location).miles

# Route for home page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username in users:
            error = 'Username already exists'
            return render_template('register.html', error=error)
        else:
            # Add new user to the database (replace with database insertion)
            users[username] = {
                'username': username,
                'email': email,
                'password_hash': generate_password_hash(password)
            }
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
    return render_template('register.html')

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))

# Route for health services
@app.route('/health', methods=['GET', 'POST'])
def health():
    if request.method == 'POST':
        city = request.form.get('city')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        if not city or not latitude or not longitude:
            flash('Please fill out all fields', 'error')
            return render_template('health.html')

        try:
            user_location = (float(latitude), float(longitude))
        except ValueError:
            flash('Invalid latitude or longitude', 'error')
            return render_template('health.html')

        hospitals_in_city = hospital_data.get(city)
        if hospitals_in_city:
            nearby_hospitals = []
            for hospital in hospitals_in_city:
                hospital_location = (hospital['latitude'], hospital['longitude'])
                distance = calculate_distance(user_location, hospital_location)
                nearby_hospitals.append((hospital['name'], distance))
            sorted_hospitals = sorted(nearby_hospitals, key=lambda x: x[1])
            return render_template('health.html', hospitals=sorted_hospitals)
        else:
            flash('City not found', 'error')
            return render_template('health.html')
    return render_template('health.html')

# Route for education services
@app.route('/education', methods=['GET', 'POST'])
def education():
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Please select a city', 'error')
            return render_template('education.html')

        education_info = education_data.get(city)
        if education_info:
            return render_template('education.html', education_info=education_info)
        else:
            flash('City not found', 'error')
            return render_template('education.html')
    return render_template('education.html')

# Route for transportation services
@app.route('/transportation', methods=['GET', 'POST'])
def transportation():
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Please select a city', 'error')
            return render_template('transportation.html')

        transportation_info = transportation_data.get(city)
        if transportation_info:
            return render_template('transportation.html', transportation_info=transportation_info)
        else:
            flash('City not found', 'error')
            return render_template('transportation.html')
    return render_template('transportation.html')



# Route for finance services
@app.route('/finance', methods=['GET', 'POST'])
def finance():
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Please select a city', 'error')
            return render_template('finance.html')
        finance_info = finance_data.get(city)
        if finance_info:
            return render_template('finance.html', finance_info=finance_info)
        else:
            flash('City not found', 'error')
            return render_template('finance.html')
    return render_template('finance.html')
# Route for government services
@app.route('/government', methods=['GET', 'POST'])
def government():
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Please select a city', 'error')
            return render_template('government.html')
        government_info = gov_services_data.get(city)
        if government_info:
            return render_template('government.html', government_info=government_info)
        else:
            flash('City not found', 'error')
            return render_template('government.html')
    return render_template('government.html')


# Route for housing services
@app.route('/housing', methods=['GET', 'POST'])
def housing():
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Please select a city', 'error')
            return render_template('housing.html')
        housing_info= housing_data.get(city)
        if housing_info:
            return render_template('housing.html', housing_info=housing_info)
        else:
            flash('City not found', 'error')
            return render_template('housing.html')
    return render_template('housing.html')
        
if __name__ == '__main__':
    app.run(debug=True)






















