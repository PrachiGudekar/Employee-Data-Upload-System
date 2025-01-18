from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import pandas as pd
from app import db
from models import Employee
from datetime import datetime
import re

upload_file = Blueprint('upload_file', __name__)

@upload_file.route('/', methods=['GET', 'POST'])
def upload_file_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Read the file into a DataFrame
                data = pd.read_excel(file)

                # Clean column names
                data.columns = data.columns.str.strip()

                # Check if required columns are in the DataFrame
                required_columns = [
                    'Employee ID', 'Employee Name', 'Date of Joining', 'Date of Birth',
                    'Department', 'Reporting Authority Employee ID', 'Mobile Number',
                    'Email ID', 'PAN Number', 'Fixed Salary', 'Bonus Salary', 'Total Salary',
                    'Designation'
                ]

                missing_columns = [col for col in required_columns if col not in data.columns]
                if missing_columns:
                    flash(f'Missing columns: {", ".join(missing_columns)}', 'error')
                    return redirect(request.url)

                # Process data
                successful_records, failed_records, error_messages = process_data(data)
                
                # Log upload results
                log_upload_results(successful_records, failed_records, error_messages, request)

                # Store results in session
                session['upload_results'] = {
                    'successful_records': successful_records,
                    'failed_records': failed_records,
                    'error_messages': error_messages
                }

                return redirect(url_for('upload_file.upload_results'))

            except Exception as e:
                flash(f'Error processing file: {e}', 'error')
                return redirect(request.url)
    
    return render_template('upload.html')

@upload_file.route('/results')
def upload_results():
    results = session.get('upload_results', {})
    session.pop('upload_results', None)  # Clear results from session

    return render_template('results.html', results=results)

def process_data(data):
    successful_records = 0
    failed_records = 0
    error_messages = []
    for index, row in data.iterrows():
        try:
            # Print row for debugging
            print(f"Processing row {index}: {row}")

            # Validation logic here
            validate_row(row)

            # Check if Employee ID already exists
            if Employee.query.filter_by(employee_id=row['Employee ID']).first():
                raise ValueError(f"Employee ID '{row['Employee ID']}' already exists.")

            new_employee = Employee(
                employee_id=row['Employee ID'],
                employee_name=row['Employee Name'],
                date_of_joining=pd.to_datetime(row['Date of Joining'], errors='coerce'),
                date_of_birth=pd.to_datetime(row['Date of Birth'], errors='coerce'),
                department=row['Department'],
                reporting_authority_id=row['Reporting Authority Employee ID'],
                mobile_number=row['Mobile Number'],
                email_id=row['Email ID'],
                pan_number=row['PAN Number'],
                fixed_salary=row['Fixed Salary'],
                bonus_salary=row['Bonus Salary'],
                total_salary=row['Total Salary'],
                designation=row['Designation']
            )
            db.session.add(new_employee)
            db.session.commit()
            successful_records += 1
        except Exception as e:
            error_message = f"Error processing row {index}: {str(e)}"
            print(error_message)  # Print error for debugging
            error_messages.append(error_message)
            db.session.rollback()
            failed_records += 1

    return successful_records, failed_records, error_messages

def validate_row(row):
    # Validation functions for each field
    def validate_row(row):
    # Validate Employee ID
     employee_id = str(row['Employee ID']).strip()
     if not isinstance(employee_id, str) or not employee_id.isalnum():
        raise ValueError("Employee ID must be unique and alphanumeric.")
    
    # Validate Employee Name
    employee_name = str(row['Employee Name']).strip()
    if not re.match(r'^[A-Za-z\s]+$', employee_name):
        raise ValueError("Employee Name must contain only alphabetic characters and be non-empty.")
    
    # Validate Date of Joining
    date_of_joining = pd.to_datetime(row['Date of Joining'], errors='coerce')
    if date_of_joining is pd.NaT or date_of_joining >= datetime.now():
        raise ValueError("Date of Joining must be a valid date in the past.")
    
    # Validate Date of Birth
    dob = pd.to_datetime(row['Date of Birth'], errors='coerce')
    if dob is pd.NaT or (datetime.now() - dob).days / 365 < 18:
        raise ValueError("Date of Birth must be a valid date with the employee at least 18 years old.")
    
    # Validate Department
    valid_departments = ["HR", "IT", "Finance", "Marketing"]  # Example list
    if row['Department'] not in valid_departments:
        raise ValueError("Department must be a valid department name from a predefined list.")
    
    # Validate Mobile Number
    mobile_number = str(row['Mobile Number']).strip()
    if not re.match(r'^\d{10}$', mobile_number):
        raise ValueError("Mobile Number must be a valid 10-digit number without any special characters or spaces.")
    
    # Validate Email ID
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(row['Email ID'])):
        raise ValueError("Email ID must be a valid email format.")
    
    # Validate PAN Number
    if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', str(row['PAN Number'])):
        raise ValueError("PAN Number must be a valid PAN format.")
    
    # Validate Salaries
    if row['Fixed Salary'] < 0 or row['Bonus Salary'] < 0 or row['Total Salary'] != (row['Fixed Salary'] + row['Bonus Salary']):
        raise ValueError("Fixed Salary and Bonus Salary must be non-negative, and Total Salary must be the sum of Fixed Salary and Bonus Salary.")


    # Print debug information
    print(f"Row validation passed: {row}")

def log_upload_results(successful_records, failed_records, error_messages, request):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user = session.get('user', 'Anonymous')  # Replace 'user' with actual user session variable if applicable
    log_entry = f"Upload Attempt: {timestamp}\n"
    log_entry += f"User: {user}\n"
    log_entry += f"Total Records Processed: {successful_records + failed_records}\n"
    log_entry += f"Successful Records: {successful_records}\n"
    log_entry += f"Failed Records: {failed_records}\n"
    if error_messages:
        log_entry += "Errors:\n" + "\n".join(error_messages) + "\n"
    
    with open('upload_log.txt', 'a') as log_file:
        log_file.write(log_entry + "\n")
            
def allowed_file(filename):
    return filename.lower().endswith(('.xls', '.xlsx'))
