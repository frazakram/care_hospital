from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import uuid

app = Flask(__name__)

# Initialize the data structure
columns = ['Patient ID', 'Patient Name', 'Diseases', 'Days Stayed', 'Doctor Name']
patients_df = pd.DataFrame(columns=columns)

# List of doctors
doctors = ['Dr.Mahera Erum', 'Dr.Irfan Anwar']

def add_patient(name, diseases, days_stayed, doctor):
    global patients_df
    if doctor not in doctors:
        return None
    patient_id = str(uuid.uuid4())  # Generate a unique patient ID
    new_patient = pd.DataFrame([{
        'Patient ID': patient_id,
        'Patient Name': name,
        'Diseases': diseases,
        'Days Stayed': days_stayed,
        'Doctor Name': doctor
    }])
    patients_df = pd.concat([patients_df, new_patient], ignore_index=True)
    return patient_id

def calculate_bill(diseases, days_stayed):
    total_sum = sum(diseases.values()) * days_stayed
    return total_sum

def generate_bill(patient_name, patient_id):
    global patients_df
    patient = patients_df[
        (patients_df['Patient Name'] == patient_name) &
        (patients_df['Patient ID'] == patient_id)
    ]
    if patient.empty:
        return None
    patient = patient.iloc[0]
    total_sum = calculate_bill(patient['Diseases'], patient['Days Stayed'])
    
    return {
        'patient_name': patient['Patient Name'],
        'doctor_name': patient['Doctor Name'],
        'days_stayed': patient['Days Stayed'],
        'diseases': patient['Diseases'],
        'total_sum': total_sum
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    global patients_df
    if request.method == 'POST':
        if 'name' in request.form and 'diseases' in request.form:
            name = request.form['name']
            diseases_str = request.form['diseases']
            diseases = {d.split(':')[0]: float(d.split(':')[1]) for d in diseases_str.split(',')}
            days_stayed = int(request.form['days_stayed'])
            doctor = request.form['doctor']
            patient_id = add_patient(name, diseases, days_stayed, doctor)
            if patient_id:
                return redirect(url_for('index', patient_id=patient_id))
            else:
                return render_template('index.html', error="Invalid doctor name.")
        elif 'patient_id' in request.form and 'name' in request.form:
            patient_name = request.form['name']
            patient_id = request.form['patient_id']
            bill_context = generate_bill(patient_name, patient_id)
            if bill_context is None:
                return render_template('index.html', bill="Patient not found.", error="Patient not found.")
            return render_template('index.html', **bill_context, error=None)
    return render_template('index.html', bill=None, error=None, patients=patients_df.to_dict(orient='records'))

@app.route('/add_patient', methods=['POST'])
def add_patient_route():
    name = request.form['name']
    diseases_str = request.form['diseases']
    diseases = {d.split(':')[0]: float(d.split(':')[1]) for d in diseases_str.split(',')}
    days_stayed = int(request.form['days_stayed'])
    doctor = request.form['doctor']
    patient_id = add_patient(name, diseases, days_stayed, doctor)
    if patient_id:
        return redirect(url_for('index', patient_id=patient_id))
    else:
        return render_template('index.html', error="Invalid doctor name.")

@app.route('/generate_bill', methods=['POST'])
def generate_bill_route():
    patient_name = request.form['name']
    patient_id = request.form['patient_id']
    bill_context = generate_bill(patient_name, patient_id)
    if bill_context is None:
        return render_template('bill.html', bill="Patient not found.")
    return render_template('bill.html', **bill_context)

if __name__ == '__main__':
    app.run(debug=True)
