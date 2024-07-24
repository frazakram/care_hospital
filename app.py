from flask import Flask, request, render_template, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Initialize the data structure
columns = ['Patient Name', 'Diseases', 'Days Stayed', 'Doctor Name']
patients_df = pd.DataFrame(columns=columns)

def add_patient(name, diseases, days_stayed, doctor):
    global patients_df
    new_patient = pd.DataFrame([{
        'Patient Name': name,
        'Diseases': diseases,
        'Days Stayed': days_stayed,
        'Doctor Name': doctor
    }])
    patients_df = pd.concat([patients_df, new_patient], ignore_index=True)

def calculate_bill(diseases, days_stayed):
    total_sum = sum(diseases.values()) * days_stayed
    return total_sum

def generate_bill(patient_name):
    global patients_df
    if patient_name not in patients_df['Patient Name'].values:
        return None
    patient = patients_df[patients_df['Patient Name'] == patient_name].iloc[0]
    total_sum = calculate_bill(patient['Diseases'], patient['Days Stayed'])
    
    # Pass the necessary context for the template
    return {
        'patient_name': patient['Patient Name'],
        'doctor_name': patient['Doctor Name'],
        'days_stayed': patient['Days Stayed'],
        'diseases': patient['Diseases'],
        'total_sum': total_sum
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'name' in request.form:
            name = request.form['name']
            diseases_str = request.form['diseases']
            diseases = {d.split(':')[0]: float(d.split(':')[1]) for d in diseases_str.split(',')}
            days_stayed = int(request.form['days_stayed'])
            doctor = request.form['doctor']
            add_patient(name, diseases, days_stayed, doctor)
            return redirect(url_for('index'))
        elif 'patient_name' in request.form:
            patient_name = request.form['patient_name']
            bill = generate_bill(patient_name)
            if bill is None:
                return render_template('index.html', bill=None, error="Patient not found.")
            return render_template('index.html', bill=bill, error=None)
    return render_template('index.html', bill=None, error=None)

@app.route('/add_patient', methods=['POST'])
def add_patient_route():
    name = request.form['name']
    diseases_str = request.form['diseases']
    diseases = {d.split(':')[0]: float(d.split(':')[1]) for d in diseases_str.split(',')}
    days_stayed = int(request.form['days_stayed'])
    doctor = request.form['doctor']
    add_patient(name, diseases, days_stayed, doctor)
    return redirect(url_for('index'))

@app.route('/generate_bill', methods=['POST'])
def generate_bill_route():
    patient_name = request.form['patient_name']
    bill_context = generate_bill(patient_name)
    if bill_context is None:
        return render_template('bill.html', bill="Patient not found.")
    return render_template('bill.html', **bill_context)


if __name__ == '__main__':
    app.run(debug=True)
