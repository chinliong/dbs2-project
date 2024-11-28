# routes/staff.py

# from flask import render_template, request, redirect, session, url_for, flash, jsonify
# from . import staff_bp
# from db import get_db_connection
# from utils import is_valid_nric, is_valid_sg_address, is_valid_sg_phone
# import mysql.connector
# from werkzeug.security import generate_password_hash
# from datetime import datetime, timedelta
# import logging

# # Staff Dashboard route
# @staff_bp.route('/staff_dashboard', methods=['GET'])
# def staff_dashboard():
#     if 'is_staff' in session and session['is_staff'] == 1:
#         connection = get_db_connection()
#         cursor = connection.cursor()

#         # Get values from the request (GET parameters)
#         user_id = request.args.get('user_id', '')
#         username = request.args.get('username', '')
#         email = request.args.get('email', '')
#         address = request.args.get('address', '')
#         contact_number = request.args.get('contact_number', '')
#         name = request.args.get('name', '')
#         nric = request.args.get('nric', '')
#         gender = request.args.get('gender', '')
#         height = request.args.get('height', '')
#         weight = request.args.get('weight', '')
#         dob = request.args.get('dob', '')
#         diagnosis = request.args.get('diagnosis', '') 
#         diagnosis_date = request.args.get('diagnosis_date', '')  

#         # Query to fetch patient details, similar to @patient_bp.route
#         query = """
#             SELECT u.UserID, u.Username, u.Email, u.Address, u.ContactNumber, 
#                    p.PatientName, p.NRIC, p.PatientGender, p.PatientHeight, 
#                    p.PatientWeight, p.PatientDOB, ph.diagnosis, ph.diagnosis_date
#             FROM Users u
#             LEFT JOIN Patients p ON u.UserID = p.UserID
#             LEFT JOIN (
#                 SELECT ph1.PatientID, ph1.diagnosis, ph1.date as diagnosis_date
#                 FROM PatientHistory ph1
#                 INNER JOIN (
#                     SELECT PatientID, MAX(date) AS latest_date
#                     FROM PatientHistory
#                     GROUP BY PatientID
#                 ) ph2 ON ph1.PatientID = ph2.PatientID AND ph1.date = ph2.latest_date
#             ) ph ON p.PatientID = ph.PatientID
#             WHERE u.IsStaff = 0
#         """
        
#         filters = []
#         params = []

#         # Add filters dynamically if they exist
#         if user_id:
#             filters.append("u.UserID = %s")
#             params.append(user_id)
#         if username:
#             filters.append("u.Username LIKE %s")
#             params.append(f"%{username}%")
#         if email:
#             filters.append("u.Email LIKE %s")
#             params.append(f"%{email}%")
#         if address:
#             filters.append("u.Address LIKE %s")
#             params.append(f"%{address}%")
#         if contact_number:
#             filters.append("u.ContactNumber LIKE %s")
#             params.append(f"%{contact_number}%")
#         if name:
#             filters.append("p.PatientName LIKE %s")
#             params.append(f"%{name}%")
#         if nric:
#             filters.append("p.NRIC LIKE %s")
#             params.append(f"%{nric}%")
#         if gender:
#             filters.append("p.PatientGender = %s")
#             params.append(gender)
#         if height:
#             filters.append("p.PatientHeight = %s")
#             params.append(height)
#         if weight:
#             filters.append("p.PatientWeight = %s")
#             params.append(weight)
#         if dob:
#             try:
#                 formatted_dob = datetime.strptime(dob, '%Y-%m-%d').date()
#                 filters.append("p.PatientDOB = %s")
#                 params.append(formatted_dob)
#             except ValueError:
#                 logging.warning(f"Invalid date format for DOB: {dob}")
#         if diagnosis:
#             filters.append("ph.diagnosis LIKE %s")
#             params.append(f"%{diagnosis}%")
#         if diagnosis_date:
#             try:
#                 formatted_date = datetime.strptime(diagnosis_date, '%Y-%m-%d').date()
#                 filters.append("DATE(ph.diagnosis_date) = %s")
#                 params.append(formatted_date)
#             except ValueError:
#                 logging.warning(f"Invalid date format for diagnosis_date: {diagnosis_date}")

#         # If there are filters, append them to the query
#         if filters:
#             query += " AND " + " AND ".join(filters)

#         # Execute the query with parameters
#         cursor.execute(query, params)
#         patients = cursor.fetchall()

#         cursor.close()
#         connection.close()

#         return render_template('staff_dashboard.html', patients=patients)
#     else:
#         flash('Please login or create a new account to access our services.')
#         return redirect(url_for('auth.login'))
    
# # Edit patient records route
# @staff_bp.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
# def edit_patient(patient_id):
#     if 'is_staff' not in session or session['is_staff'] != 1:
#         flash('You do not have access to this page.')
#         return redirect(url_for('auth.login'))

#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     errors = {}

#     if request.method == 'POST':
        
#         print(f"Full form data: {request.form}")
#         # Retrieve form data
#         patient_name = request.form['patient_name']
#         nric = request.form['nric']
#         patient_gender = request.form['patient_gender']
#         patient_height = request.form['patient_height']
#         patient_weight = request.form['patient_weight']
#         patient_dob = request.form['patient_dob']
#         email = request.form['email']
#         username = request.form['username']
#         contact_number = request.form['contact_number']
#         address = request.form['address']
#         password = request.form.get('password')

#         # Handle past diagnosis update or add
#         diagnosis_id = request.form.getlist('diagnosis_id')
#         print(f"Diagnosis IDs: {diagnosis_id}")
#         diagnosis_text = request.form.getlist('diagnosis_text')
#         diagnosis_date = request.form.getlist('diagnosis_date')
#         diagnosis_notes = request.form.getlist('diagnosis_notes')
#         appt_id = request.form.getlist('appt_id')  # Fetch the ApptID list
        
#         # Fetch PatientID from Patients table
#         cursor.execute("SELECT PatientID FROM Patients WHERE UserID = %s", (patient_id,))
#         patient_data = cursor.fetchone()
#         if not patient_data:
#             flash('Patient not found.', 'danger')
#             return redirect(url_for('staff.staff_dashboard'))

#         actual_patient_id = patient_data['PatientID']  # Use PatientID instead of UserID

#         # Validations
#         if not is_valid_nric(nric):
#             errors['nric'] = 'Invalid NRIC format. It must start with S, T, F, G, or M, followed by 7 digits and one letter.'

#         if not is_valid_sg_phone(contact_number):
#             errors['contact_number'] = 'Invalid phone number format. It must start with 6, 8, or 9 and be 8 digits long.'

#         if not is_valid_sg_address(address):
#             errors['address'] = 'Invalid address. Please include a valid 6-digit postal code.'

#         cursor.execute("SELECT IsStaff FROM Users WHERE UserID = %s", (patient_id,))
#         existing_is_staff = cursor.fetchone()['IsStaff']

#         cursor.execute("SELECT * FROM Users WHERE (Email = %s OR ContactNumber = %s OR Username = %s) AND UserID != %s",
#                        (email, contact_number, username, patient_id))
#         existing_user = cursor.fetchone()

#         cursor.execute("SELECT * FROM Patients WHERE NRIC = %s AND UserID != %s", (nric, patient_id))
#         existing_nric = cursor.fetchone()

#         if existing_user:
#             if existing_user['Email'] == email:
#                 errors['email'] = 'Email is already in use.'
#             if existing_user['ContactNumber'] == contact_number:
#                 errors['contact_number'] = 'Contact number is already in use.'
#             if existing_user['Username'] == username:
#                 errors['username'] = 'Username is already in use.'

#         if existing_nric:
#             errors['nric'] = 'NRIC is already in use.'

#         # If no errors, update the patient details into DB
#         if not errors:
#             try:
#                 # Handle empty height and weight fields (user does not have weight and height by default)
#                 patient_height = patient_height if patient_height.strip() else None
#                 patient_weight = patient_weight if patient_weight.strip() else None
                
#                 cursor.execute("""
#                     UPDATE Patients
#                     SET PatientName = %s, NRIC = %s, PatientGender = %s, PatientHeight = %s, 
#                         PatientWeight = %s, PatientDOB = %s
#                     WHERE UserID = %s
#                 """, (patient_name, nric, patient_gender, patient_height, patient_weight, patient_dob, patient_id))

#                 # Update password if provided
#                 cursor.execute("SELECT Password FROM Users WHERE UserID = %s", (patient_id,))
#                 existing_hashed_password = cursor.fetchone()['Password']

#                 if password and password.strip():
#                     hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
#                     cursor.execute("""
#                         UPDATE Users
#                         SET Password = %s
#                         WHERE UserID = %s
#                     """, (hashed_password, patient_id))

#                 # Update Users table for other details
#                 cursor.execute("""
#                     UPDATE Users
#                     SET Username = %s, Email = %s, ContactNumber = %s, Address = %s, IsStaff = %s
#                     WHERE UserID = %s
#                 """, (username, email, contact_number, address, existing_is_staff, patient_id))

#                 # Handle diagnosis updates and inserts
#                 for idx, diag_id in enumerate(diagnosis_id):
                    
#                     # If diagnosis ID (HistoryID) exists, update the existing diagnosis
#                     if diag_id:
#                         cursor.execute("""
#                             UPDATE PatientHistory 
#                             SET diagnosis = %s, date = %s, notes = %s, ApptID = %s
#                             WHERE HistoryID = %s AND PatientID = %s
#                         """, (diagnosis_text[idx], diagnosis_date[idx], diagnosis_notes[idx], appt_id[idx], diag_id, actual_patient_id))

#                 connection.commit()

#                 flash('Patient details and diagnoses updated successfully!', 'success')
#                 return redirect(url_for('staff.staff_dashboard'))
#             except mysql.connector.Error as err:
#                 connection.rollback()  # Rollback in case there is an error with adding record
#                 flash(f'An error occurred: {err}', 'danger')

#     # Fetch patient details
#     cursor.execute("SELECT UserID, PatientID, PatientName, NRIC, PatientGender, PatientHeight, PatientWeight, PatientDOB FROM Patients WHERE UserID = %s", (patient_id,))
#     patient = cursor.fetchone()

#     if not patient:
#         flash('Patient not found', 'danger')
#         return redirect(url_for('staff.staff_dashboard'))

#     # Fetch user details related to the patient
#     cursor.execute("SELECT * FROM Users WHERE UserID = %s", (patient_id,))
#     user = cursor.fetchone()

#     # Fetch past diagnoses using PatientID
#     cursor.execute("SELECT HistoryID, ApptID, diagnosis, date, notes FROM PatientHistory WHERE PatientID = %s ORDER BY date DESC", (patient['PatientID'],))
#     patient_diagnoses = cursor.fetchall()

#     # Change date format to Year/Month/Date (default format in DB)
#     for diag in patient_diagnoses:
#         if diag['date']:
#             diag['date'] = diag['date'].strftime('%Y-%m-%d')

#     cursor.close()
#     connection.close()

#     return render_template('edit_patient.html', patient=patient, user=user, diagnoses=patient_diagnoses, errors=errors)

# # Delete patient records route. Only staff should be able to delete patient records due to how a clinic works
# @staff_bp.route('/delete_patient/<int:patient_id>', methods=['POST'])
# def delete_patient(patient_id):
#     if 'is_staff' not in session or session['is_staff'] != 1:
#         flash('You do not have access to this page.')
#         return redirect(url_for('auth.login'))

#     connection = get_db_connection()
#     cursor = connection.cursor()

#     try:
#         # Delete from all tables associated to patients
#         # Presriptions, PatientHistory, Appointments, Patients, Users in order
#         cursor.execute("DELETE FROM Prescriptions WHERE PatientID = (SELECT PatientID FROM Patients WHERE UserID = %s)", (session['user_id'],))
#         cursor.execute("DELETE FROM PatientHistory WHERE PatientID = (SELECT PatientID FROM Patients WHERE UserID = %s)", (session['user_id'],))
#         cursor.execute("DELETE FROM Appointments WHERE PatientID = (SELECT PatientID FROM Patients WHERE UserID = %s)", (patient_id,))
#         cursor.execute("DELETE FROM Patients WHERE UserID = %s", (patient_id,))
#         cursor.execute("DELETE FROM Users WHERE UserID = %s", (patient_id,))

#         connection.commit()
#         flash('Patient and associated appointments deleted successfully!', 'success')
#     except mysql.connector.Error as err:
#         connection.rollback()
#         flash(f'An error occurred: {err}', 'danger')

#     cursor.close()
#     connection.close()

#     return redirect(url_for('staff.staff_dashboard'))

# # Manage appointment route
# # It is for doctors to see what appointments there are for the next 7 days.
# @staff_bp.route('/manage_appointment')
# def manage_appointment():
#     if 'is_staff' in session and session['is_staff'] == 1:
#         connection = get_db_connection()
#         cursor = connection.cursor()

#         # Calculate the date range for the next 7 days
#         start_date = datetime.now()
#         end_date = start_date + timedelta(days=7)

#         # Fetch appointments in the next 7 days sorted by earliest first
#         cursor.execute("""
#             SELECT * FROM Appointments 
#             WHERE ApptDate BETWEEN %s AND %s AND ApptStatus = %s
#             ORDER BY ApptDate, ApptTime
#         """, (start_date.date(), end_date.date(), "Pending"))
#         appointments = cursor.fetchall()

#         cursor.close()
#         connection.close()
#         return render_template('manage_appointment.html', appointments=appointments)
#     else:
#         flash('Please login or create a new account to access our services.')

# # View patient details
# @staff_bp.route('/view_patient/<int:patient_id>/<int:appt_id>', methods=['GET', 'POST'])
# def view_patient(patient_id, appt_id):
#     connection = get_db_connection()
#     cursor = connection.cursor(buffered=True)

#     if request.method == 'POST':
#         # Check if we are saving a prescription
#         if 'medication' in request.form:
#             medication_name = request.form['medication']
#             # Extract only the medication name from the display text
#             med_name_only = medication_name.split(' (')[0]  # Gets everything before the first opening parenthesis
#             duration = request.form['duration']
#             notes = request.form['notes']

#             # Fetch the MedID based on med name
#             cursor.execute("SELECT MedID, quantity FROM Medications WHERE name = %s", (med_name_only,))
#             med = cursor.fetchone()

#             if med:
#                 med_id = med[0]
#                 current_quantity = med[1]
#                 requested_dosage = int(duration)
#                 print(current_quantity, type(current_quantity))
#                 print(requested_dosage, type(requested_dosage))

#                 # Check if there is enough medication
#                 if current_quantity >= requested_dosage:
#                     # Insert into Prescriptions table
#                     cursor.execute("""
#                         INSERT INTO Prescriptions (PatientID, ApptID, MedID, Dosage, Date, Notes) 
#                         VALUES (%s, %s, %s, %s, %s, %s)
#                     """, (patient_id, appt_id, med_id, requested_dosage, datetime.now(), notes))
                    
#                     # Deduct the quantity
#                     new_quantity = current_quantity - requested_dosage
#                     cursor.execute("UPDATE Medications SET quantity = %s WHERE MedID = %s", (new_quantity, med_id))

#                     # Insert an entry into Inventory logs
#                     cursor.execute("""
#                         INSERT INTO InventoryLogs (MedID, change_type, quantity_changed, date) 
#                         VALUES (%s, 'subtract', %s, %s)
#                     """, (med_id, requested_dosage, datetime.now()))

#                     connection.commit()
#                     flash('Prescription added successfully!', 'success')
#                 else:
#                     flash('Not enough medication in stock!', 'danger')
#             else:
#                 flash('Medication not found!', 'danger')

#         else:
#             # Save the diagnosis and notes
#             diagnosis = request.form['diagnosis']
#             notes = request.form['notes']
#             date = datetime.now()

#             cursor.execute("""
#                 INSERT INTO PatientHistory (PatientID, ApptID, diagnosis, notes, date) 
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (patient_id, appt_id, diagnosis, notes, date))

#             connection.commit()
#             flash('Patient history updated successfully!', 'success')

#     # Fetch past patient information, past diagnosis and prescriptions to display
#     cursor.execute("SELECT * FROM Patients WHERE PatientID = %s", (patient_id,))
#     patient_info = cursor.fetchone()
#     cursor.execute("SELECT * FROM PatientHistory WHERE PatientID = %s", (patient_id,))
#     patient_history = cursor.fetchall()
#     cursor.execute("""
#     SELECT p.PrescriptionID, m.name, p.Dosage, p.Date, p.Notes 
#     FROM Prescriptions p 
#     JOIN Medications m ON p.MedID = m.MedID 
#     WHERE p.PatientID = %s
#     """, (patient_id,))
#     past_prescriptions = cursor.fetchall()

#     cursor.close()
#     connection.close()
#     return render_template('view_patient.html', patient=patient_info, history=patient_history, prescriptions=past_prescriptions, appt_id=appt_id)

# # Fetch medications route
# @staff_bp.route('/fetch_medications')
# def fetch_medications():
#     query = request.args.get('query', '')
#     connection = get_db_connection()
#     cursor = connection.cursor()

#     # Fetch medications that match the user's input
#     cursor.execute("SELECT * FROM Medications WHERE LOWER(name) LIKE %s", (f'%{query}%',))
#     medications = cursor.fetchall()
    
#     cursor.close()
#     connection.close()
    
#     # Prepare response data based on columns in med table
#     medication_list = [
#         {
#             'name': med[1],      
#             'form': med[2],      
#             'dosage': med[3],    
#         }
#         for med in medications
#     ]
    
#     return jsonify(medication_list)

# # Advanced search routes
# # Search feature for staff only using different parameters to find patients
# @staff_bp.route('/advanced_search', methods=['POST'])
# def advanced_search():
#     if 'is_staff' not in session or session['is_staff'] != 1:
#         return jsonify({'error': 'Unauthorized'}), 403

#     # Get search parameters from the form
#     filters = {
#         'Username': request.form.get('username'),
#         'Email': request.form.get('email'),
#         'Address': request.form.get('address'),
#         'ContactNumber': request.form.get('contact_number'),
#         'PatientName': request.form.get('patient_name'),
#         'NRIC': request.form.get('nric'),
#         'PatientGender': request.form.get('gender'),
#         'PatientHeight': request.form.get('height'),
#         'PatientWeight': request.form.get('weight'),
#         'PatientDOB': request.form.get('dob'),
#         'diagnosis': request.form.get('diagnosis'),
#         'diagnosis_date': request.form.get('diagnosis_date')
#     }

#     # Catch-all query to get the data
#     query = """
#     SELECT u.UserID, u.Username, u.Email, u.Address, u.ContactNumber, 
#            p.PatientName, p.NRIC, p.PatientGender, p.PatientHeight, 
#            p.PatientWeight, p.PatientDOB, ph.diagnosis, ph.diagnosis_date
#     FROM Users u
#     LEFT JOIN Patients p ON u.UserID = p.UserID
#     LEFT JOIN (
#         SELECT ph1.PatientID, ph1.diagnosis, ph1.date AS diagnosis_date
#         FROM PatientHistory ph1
#         INNER JOIN (
#             SELECT PatientID, MAX(date) AS latest_date
#             FROM PatientHistory
#             GROUP BY PatientID
#         ) ph2 ON ph1.PatientID = ph2.PatientID AND ph1.date = ph2.latest_date
#     ) ph ON p.PatientID = ph.PatientID
#     WHERE u.IsStaff = 0
#     """

#     conditions = []
#     params = []

#     # Add filters dynamically if they exist
#     for field, value in filters.items():
#         if value:
#             if field in ['Username', 'Email', 'Address', 'ContactNumber', 'PatientName', 'NRIC', 'diagnosis']: 
#                 conditions.append(f"{field} LIKE %s")
#                 params.append(f"%{value}%")
#             elif field == 'PatientGender':
#                 gender_map = {'Male': 'M', 'Female': 'F'}
#                 conditions.append(f"p.PatientGender = %s")
#                 params.append(gender_map.get(value, value))
#             elif field in ['PatientHeight', 'PatientWeight']:
#                 try:
#                     float_value = float(value)
#                     conditions.append(f"ABS(p.{field} - %s) < 0.01")
#                     params.append(float_value)
#                 except ValueError:
#                     pass
#             elif field == 'PatientDOB':
#                 conditions.append(f"p.PatientDOB = %s")
#                 params.append(value)
#             elif field == 'diagnosis_date':
#                 try:
#                     formatted_date = datetime.strptime(value, '%Y-%m-%d').date()
#                     conditions.append(f"DATE(ph.diagnosis_date) = %s")
#                     params.append(formatted_date)
#                 except ValueError:
#                     logging.warning(f"Invalid date format for diagnosis_date: {value}")
#                     continue

#     # Add conditions to the query
#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     query += " ORDER BY u.UserID"

#     # Execute the query
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute(query, params)
#     results = cursor.fetchall()

#     # Check DoB format
#     for result in results:
#         if result['PatientDOB']:
#             result['PatientDOB'] = result['PatientDOB'].strftime('%Y-%m-%d')
#         if result['diagnosis_date']:  # Ensure diagnosis_date is formatted correctly
#             result['diagnosis_date'] = result['diagnosis_date'].strftime('%Y-%m-%d')

#     cursor.close()
#     connection.close()

#     return jsonify(results)

# # Staff only feature: edit appointments for patients
# # Initially we allowed patients/users to delete, but it is not correct
# # And does not work in real-life, since we are also recording NRIC
# @staff_bp.route('/edit_appointment/<int:appt_id>', methods=['GET', 'POST'])
# def edit_appointment(appt_id):
#     connection = get_db_connection()
#     cursor = connection.cursor()

#     if request.method == 'POST':
#         date = request.form['date']
#         time = request.form['time']
#         status = request.form['status']
#         reason = request.form['reason']

#         cursor.execute("""
#             UPDATE Appointments 
#             SET ApptDate = %s, ApptTime = %s, ApptStatus = %s, ApptReason = %s 
#             WHERE ApptID = %s
#         """, (date, time, status, reason, appt_id))

#         connection.commit()
#         flash('Appointment updated successfully!', 'success')
#         return redirect(url_for('staff.manage_appointment'))

#     cursor.execute("SELECT * FROM Appointments WHERE ApptID = %s", (appt_id,))
#     appointment = cursor.fetchone()

#     cursor.close()
#     connection.close()
    
#     return render_template('edit_appointment.html', appointment=appointment)

# # Book appointment route
# # Staff can also help to book appointments
# # Copied from @patient_bp.route
# @staff_bp.route('/staff_book_appointment', methods=['GET', 'POST'])
# def staff_book_appointment():
#     if 'user_id' not in session:
#         flash('Please log in as staff to book an appointment.')
#         return redirect(url_for('auth.login'))

#     # Get the current date and the date one week from now
#     today = datetime.now().date()
#     one_week_later = today + timedelta(days=7)

#     if request.method == 'POST':
#         nric = request.form.get('patient_nric')
#         appt_date = request.form.get('appt_date')
#         appt_time = request.form.get('appt_time')
#         appt_reason = request.form.get('appt_reason')

#         #Validation
#         if not nric or not appt_date or not appt_time or not appt_reason:
#             flash('All fields are required.')
#             return redirect(url_for('staff.staff_book_appointment'))

#         try:
#             appt_date_obj = datetime.strptime(appt_date, '%Y-%m-%d').date()
#             appt_time_obj = datetime.strptime(appt_time, '%H:%M').time()
#             if appt_time_obj.minute not in [0, 30]:
#                 flash('Appointments must be booked at 30-minute intervals.')
#                 return redirect(url_for('staff.staff_book_appointment'))
#         except ValueError:
#             flash('Invalid date or time format.')
#             return redirect(url_for('staff.staff_book_appointment'))

#         if appt_date_obj < datetime.today().date():
#             flash('Appointment date must be in the future.')
#             return redirect(url_for('staff.staff_book_appointment'))

#         if appt_date_obj < today or appt_date_obj > one_week_later:
#             flash('Appointments can only be booked within the next 7 days.')
#             return redirect(url_for('staff.staff_book_appointment'))

#         connection = get_db_connection()
#         cursor = connection.cursor()

#         try:
#             # Check if the patient exists
#             cursor.execute("SELECT PatientID FROM Patients WHERE nric = %s", (nric,))
#             patient = cursor.fetchone()

#             if not patient:
#                 flash('Patient NRIC not found. Please contact support.')
#                 return redirect(url_for('staff.staff_book_appointment'))

#             patient_id = patient[0]  # Get the PatientID from the result
            
#             # Check if the appointment slot is available
#             cursor.execute("""
#                 SELECT COUNT(*) FROM Appointments 
#                 WHERE ApptDate = %s AND ApptTime = %s
#             """, (appt_date_obj, appt_time_obj))
#             existing_appointments = cursor.fetchone()[0]

#             if existing_appointments > 0:
#                 flash('This appointment slot is already taken. Please choose another time.')
#                 return redirect(url_for('staff.staff_book_appointment'))

#             # Insert entry into the Appointments table
#             cursor.execute("""
#                 INSERT INTO Appointments (PatientID, ApptDate, ApptTime, ApptStatus, ApptReason)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (patient_id, appt_date_obj, appt_time_obj, 'Pending', appt_reason))
#             connection.commit()

#             flash('Appointment booked successfully!', 'success')
#             return redirect(url_for('staff.staff_dashboard'))

#         except mysql.connector.Error as err:
#             print(f"Error: {err}")
#             flash('An error occurred while booking the appointment. Please try again.', 'danger')
#             return redirect(url_for('staff.staff_book_appointment'))

#         finally:
#             cursor.close()
#             connection.close()

#     return render_template('staff_book_appointment.html', min_date=today, max_date=one_week_later)

# # Delete appointments route
# # Only staff can delete appointments
# # Reasoning is because patients might jave malicious intent and keep spam booking and deleting
# # Hogging up the time slots
# @staff_bp.route('/delete_appointment/<int:appt_id>', methods=['POST'])
# def delete_appointment(appt_id):
#     connection = get_db_connection()
#     cursor = connection.cursor()

#     cursor.execute("DELETE FROM Appointments WHERE ApptID = %s", (appt_id,))
#     connection.commit()
    
#     flash('Appointment deleted successfully!', 'success')
#     cursor.close()
#     connection.close()
    
#     return redirect(url_for('staff.manage_appointment'))  # Redirect to appointments list

# # Update ApptStatus route
# # Update ApptStatus to complete, which will then no longer be shown in @staff_bp.route('/manage_appointment')
# @staff_bp.route('/complete_appointment/<int:appt_id>', methods=['POST'])
# def complete_appointment(appt_id):
#     connection = get_db_connection()
#     cursor = connection.cursor()

#     try:
#         # Update the appointment status in the database
#         cursor.execute("UPDATE Appointments SET ApptStatus = 'Completed' WHERE ApptID = %s", (appt_id,))
#         connection.commit()
#         flash('Appointment completed successfully!', 'success')
#     except Exception as e:
#         connection.rollback()
#         flash('Error completing the appointment: {}'.format(str(e)), 'danger')
#     finally:
#         cursor.close()
#         connection.close()

#     # Redirect back to the view patient page after completion
#     return redirect(url_for('staff.manage_appointment'))  # Redirect to appointments list





from flask import render_template, request, redirect, session, url_for, flash, jsonify
from . import staff_bp
from db import get_db_connection
from utils import is_valid_nric, is_valid_sg_address, is_valid_sg_phone
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from bson import json_util
import logging
from db_config import DatabaseManager

# Staff Dashboard route
@staff_bp.route('/staff_dashboard', methods=['GET'])
def staff_dashboard():
    if 'is_staff' in session and session['is_staff'] == 1:
        db = get_db_connection()

        # Get values from the request (GET parameters)
        user_id = request.args.get('user_id', '')
        username = request.args.get('username', '')
        email = request.args.get('email', '')
        address = request.args.get('address', '')
        contact_number = request.args.get('contact_number', '')
        name = request.args.get('name', '')
        nric = request.args.get('nric', '')
        gender = request.args.get('gender', '')
        height = request.args.get('height', '')
        weight = request.args.get('weight', '')
        dob = request.args.get('dob', '')
        diagnosis = request.args.get('diagnosis', '')
        diagnosis_date = request.args.get('diagnosis_date', '')

        # Build the base query for non-staff users
        query = {"IsStaff": 0}

        # Add filters for User fields
        if user_id:
            try:
                query["_id"] = ObjectId(user_id)
            except Exception:
                flash("Invalid User ID format.")
                return redirect(url_for('staff.staff_dashboard'))
        if username:
            query["Username"] = {"$regex": username, "$options": "i"}
        if email:
            query["Email"] = {"$regex": email, "$options": "i"}
        if address:
            query["Address"] = {"$regex": address, "$options": "i"}
        if contact_number:
            query["ContactNumber"] = {"$regex": contact_number, "$options": "i"}

        # Fetch users who are not staff and match the criteria
        user_matches = list(db.Users.find(query))
        
        # Prepare list to store patient data with latest diagnoses
        patients = []

        for user in user_matches:
            # Find corresponding patient record
            patient_query = {"UserID": user["_id"]}

            # Add patient-specific filters
            if name:
                patient_query["PatientName"] = {"$regex": name, "$options": "i"}
            if nric:
                patient_query["NRIC"] = {"$regex": nric, "$options": "i"}
            if gender:
                gender_map = {'Male': 'M', 'Female': 'F'}
                patient_query["PatientGender"] = gender_map.get(gender, gender)
            if height:
                try:
                    patient_query["PatientHeight"] = float(height)
                except ValueError:
                    continue
            if weight:
                try:
                    patient_query["PatientWeight"] = float(weight)
                except ValueError:
                    continue
            if dob:
                try:
                    patient_query["PatientDOB"] = datetime.strptime(dob, '%Y-%m-%d')
                except ValueError:
                    continue

            patient = db.Patients.find_one(patient_query)
            
            if patient:
                # Attach user information to patient details
                patient['user'] = user

                # Fetch latest diagnosis
                diagnosis_query = {"patient_id": patient["_id"]}
                if diagnosis:
                    diagnosis_query["diagnosis"] = {"$regex": diagnosis, "$options": "i"}
                if diagnosis_date:
                    try:
                        date_obj = datetime.strptime(diagnosis_date, '%Y-%m-%d')
                        diagnosis_query["date"] = date_obj
                    except ValueError:
                        continue

                # Get the latest diagnosis
                latest_diagnosis = db.PatientHistory.find_one(
                    diagnosis_query,
                    sort=[("date", -1)]
                )

                if latest_diagnosis:
                    patient['latest_diagnosis'] = latest_diagnosis.get("diagnosis", "")
                    # Format the date if it exists
                    if 'date' in latest_diagnosis and latest_diagnosis['date']:
                        if isinstance(latest_diagnosis['date'], datetime):
                            patient['diagnosis_date'] = latest_diagnosis['date'].strftime('%Y-%m-%d')
                        else:
                            # Handle string dates
                            try:
                                date_obj = datetime.strptime(str(latest_diagnosis['date']), '%Y-%m-%d')
                                patient['diagnosis_date'] = date_obj.strftime('%Y-%m-%d')
                            except ValueError:
                                patient['diagnosis_date'] = str(latest_diagnosis['date'])
                else:
                    patient['latest_diagnosis'] = "No diagnosis"
                    patient['diagnosis_date'] = "N/A"

                patients.append(patient)

        # Format patient dates before passing to template
        for patient in patients:
            if 'PatientDOB' in patient and patient['PatientDOB']:
                if isinstance(patient['PatientDOB'], datetime):
                    patient['PatientDOB'] = patient['PatientDOB'].strftime('%Y-%m-%d')
                elif isinstance(patient['PatientDOB'], str):
                    # If it's already a string, try to parse and reformat it
                    try:
                        date_obj = datetime.strptime(patient['PatientDOB'], '%Y-%m-%d')
                        patient['PatientDOB'] = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        pass

        return render_template('staff_dashboard.html', patients=patients)
    else:
        flash('Please login or create a new account to access our services.')
        return redirect(url_for('auth.login'))

# Edit patient records route
@staff_bp.route('/edit_patient/<string:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if 'is_staff' not in session or session['is_staff'] != 1:
        flash('You do not have access to this page.')
        return redirect(url_for('auth.login'))

    db = get_db_connection()
    errors = {}

    # Fetch patient details
    patient = db.Patients.find_one({"_id": ObjectId(patient_id)})
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('staff.staff_dashboard'))

    # Fetch the corresponding user using UserID
    user = db.Users.find_one({"_id": ObjectId(patient['UserID'])})
    if not user:
        flash('User not found for the given patient.', 'danger')
        return redirect(url_for('staff.staff_dashboard'))
    
    # If PatientDOB exists, format it to YYYY-MM-DD
    if patient.get('PatientDOB'):
        patient['PatientDOB'] = patient['PatientDOB'].strftime('%Y-%m-%d')

    if request.method == 'POST':
        # Retrieve form data
        patient_name = request.form['patient_name']
        nric = request.form['nric']
        patient_gender = request.form['patient_gender']
        patient_height = request.form['patient_height']
        patient_weight = request.form['patient_weight']
        patient_dob = request.form['patient_dob']
        email = request.form['email']
        username = request.form['username']
        contact_number = request.form['contact_number']
        address = request.form['address']
        password = request.form.get('password')

        # Handle past diagnosis update or add
        diagnosis_text = []
        diagnosis_date = []
        diagnosis_notes = []
        appt_id = []

        # Collect the diagnosis form data using dynamic field names
        idx = 1
        while f"diagnosis_text_{idx}" in request.form:
            diagnosis_text.append(request.form[f"diagnosis_text_{idx}"])
            diagnosis_date.append(request.form[f"diagnosis_date_{idx}"])
            diagnosis_notes.append(request.form[f"diagnosis_notes_{idx}"])
            appt_id.append(request.form[f"appt_id_{idx}"])
            idx += 1

        # Validations
        if not is_valid_nric(nric):
            errors['nric'] = 'Invalid NRIC format. It must start with S, T, F, G, or M, followed by 7 digits and one letter.'

        if not is_valid_sg_phone(contact_number):
            errors['contact_number'] = 'Invalid phone number format. It must start with 6, 8, or 9 and be 8 digits long.'

        if not is_valid_sg_address(address):
            errors['address'] = 'Invalid address. Please include a valid 6-digit postal code.'

        # Check for existing user with the same email, contact number, or username
        existing_user = db.Users.find_one({
            "$or": [
                {"Email": email},
                {"ContactNumber": contact_number},
                {"Username": username}
            ],
            "_id": {"$ne": ObjectId(patient['UserID'])}  # Use patient's UserID to properly exclude
        })

        existing_nric = db.Patients.find_one({
            "NRIC": nric,
            "_id": {"$ne": ObjectId(patient_id)}
        })

        if existing_user:
            if existing_user['Email'] == email:
                errors['email'] = 'Email is already in use.'
            if existing_user['ContactNumber'] == contact_number:
                errors['contact_number'] = 'Contact number is already in use.'
            if existing_user['Username'] == username:
                errors['username'] = 'Username is already in use.'

        if existing_nric:
            errors['nric'] = 'NRIC is already in use.'

        # If no errors, update the patient details in the DB
        if not errors:
            patient_update = {
                "PatientName": patient_name,
                "NRIC": nric,
                "PatientGender": patient_gender,
                "PatientHeight": float(patient_height) if patient_height.strip() else None,
                "PatientWeight": float(patient_weight) if patient_weight.strip() else None,
                "PatientDOB": datetime.strptime(patient_dob, '%Y-%m-%d')
            }
            db.Patients.update_one({"_id": ObjectId(patient_id)}, {"$set": patient_update})

            user_update = {
                "Username": username,
                "Email": email,
                "ContactNumber": contact_number,
                "Address": address
            }
            if password and password.strip():
                user_update["Password"] = generate_password_hash(password, method='pbkdf2:sha256')
            db.Users.update_one({"_id": ObjectId(patient['UserID'])}, {"$set": user_update})

           # Handle diagnosis updates and inserts
            for idx, appt in enumerate(appt_id):
                # Convert appt_id to ObjectId if it's a valid string
                try:
                    appt_object_id = ObjectId(appt)  # This will raise an error if appt is not a valid ObjectId string
                except Exception as e:
                    logging.error(f"Invalid appt_id: {appt}, Error: {str(e)}")
                    flash(f"Invalid appointment ID: {appt}", 'danger')
                    return redirect(url_for('staff.staff_dashboard'))

                diagnosis_data = {
                    "diagnosis": diagnosis_text[idx],
                    "date": datetime.strptime(diagnosis_date[idx], '%Y-%m-%d'),
                    "notes": diagnosis_notes[idx],
                    "appt_id": appt_object_id  # Store as ObjectId
                }

                # Check if diagnosis already exists in PatientHistory for the given patient and appt_id
                existing_diagnosis = db.PatientHistory.find_one({
                    "patient_id": ObjectId(patient_id),  # Make sure patient_id is ObjectId
                    "appt_id": appt_object_id  # Compare with ObjectId in the query
                })

                if existing_diagnosis:
                    # If the diagnosis already exists, update it
                    db.PatientHistory.update_one(
                        {"_id": existing_diagnosis["_id"]},
                        {"$set": diagnosis_data}
                    )
                else:
                    # If the diagnosis doesn't exist, insert a new record
                    diagnosis_data["patient_id"] = ObjectId(patient_id)  # Ensure patient_id is an ObjectId
                    db.PatientHistory.insert_one(diagnosis_data)

            flash('Patient details and diagnoses updated successfully!', 'success')
            return redirect(url_for('staff.staff_dashboard'))

    # Fetch patient diagnoses
    patient_diagnoses = list(db.PatientHistory.find({"patient_id": ObjectId(patient_id)}).sort("date", -1))

    # Format diagnosis date
    for diag in patient_diagnoses:
        if diag.get('date'):
            diag['date'] = diag['date'].strftime('%Y-%m-%d')

    return render_template('edit_patient.html', patient=patient, user=user, diagnoses=patient_diagnoses, errors=errors)


# Delete patient records route. Only staff should be able to delete patient records due to how a clinic works
@staff_bp.route('/delete_patient/<string:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if 'is_staff' not in session or session['is_staff'] != 1:
        flash('You do not have access to this page.')
        return redirect(url_for('auth.login'))

    db = get_db_connection()

    try:
        # Delete from all collections associated with patients
        db.Prescriptions.delete_many({"patient_id": ObjectId(patient_id)})
        db.PatientHistory.delete_many({"patient_id": ObjectId(patient_id)})
        db.Appointments.delete_many({"patient_id": ObjectId(patient_id)})
        db.Patients.delete_one({"_id": ObjectId(patient_id)})
        db.Users.delete_one({"_id": ObjectId(patient_id)})

        flash('Patient and associated appointments deleted successfully!', 'success')
    except Exception as err:
        flash(f'An error occurred: {err}', 'danger')

    return redirect(url_for('staff.staff_dashboard'))

# Manage appointment route
# It is for doctors to see what appointments there are for the next 7 days.
@staff_bp.route('/manage_appointment')
def manage_appointment():
    if 'is_staff' in session and session['is_staff'] == 1:
        db = get_db_connection()

        # Calculate the date range for the next 7 days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)

        # Fetch appointments in the next 7 days sorted by earliest first
        appointments = list(db.Appointments.find({
            "appt_date": {"$gte": start_date, "$lte": end_date},
            "appt_status": "Pending"
        }).sort([("appt_date", 1), ("appt_time", 1)]))

        # Modify appointments to ensure date and time are formatted as strings
        for appointment in appointments:
            if 'appt_date' in appointment and isinstance(appointment['appt_date'], str):
                try:
                    appointment['appt_date'] = datetime.strptime(appointment['appt_date'], '%Y-%m-%d')
                except ValueError:
                    appointment['appt_date'] = None  # Handle invalid date formats

            if 'appt_time' in appointment and isinstance(appointment['appt_time'], str):
                try:
                    appointment['appt_time'] = datetime.strptime(appointment['appt_time'], '%H:%M').time()
                except ValueError:
                    appointment['appt_time'] = None  # Handle invalid time formats

        return render_template('manage_appointment.html', appointments=appointments)
    else:
        flash('Please login or create a new account to access our services.')
        return redirect(url_for('auth.login'))


# View patient details
@staff_bp.route('/view_patient/<string:patient_id>/<string:appt_id>', methods=['GET', 'POST'])
def view_patient(patient_id, appt_id):
    db = get_db_connection()

    # Convert patient_id to ObjectId
    try:
        patient_object_id = ObjectId(patient_id)
    except Exception as e:
        flash(f"Error converting patient_id to ObjectId: {e}", "danger")
        return redirect(url_for('staff.staff_dashboard'))

    # Check if POST for adding medication or diagnosis
    if request.method == 'POST':
        if 'medication' in request.form:
            # Handle medication prescription
            medication_name = request.form['medication']
            med_name_only = medication_name.split(' (')[0]
            duration = request.form['duration']
            notes = request.form['notes']

            med = db.Medications.find_one({"name": med_name_only})

            if med:
                med_id = med['_id']
                current_quantity = med['quantity']
                requested_dosage = int(duration)

                if current_quantity >= requested_dosage:
                    # Insert prescription
                    db.Prescriptions.insert_one({
                        "patient_id": patient_object_id,
                        "appt_id": ObjectId(appt_id),
                        "med_id": med_id,
                        "dosage": requested_dosage,
                        "date": datetime.now(),
                        "notes": notes
                    })
                    # Update quantity
                    db.Medications.update_one({"_id": med_id}, {"$inc": {"quantity": -requested_dosage}})

                    # Insert inventory log
                    db.InventoryLogs.insert_one({
                        "med_id": med_id,
                        "change_type": 'subtract',
                        "quantity_changed": requested_dosage,
                        "date": datetime.now()
                    })

                    flash('Prescription added successfully!', 'success')
                else:
                    flash('Not enough medication in stock!', 'danger')
            else:
                flash('Medication not found!', 'danger')
        else:
            # Handle patient history addition
            diagnosis = request.form['diagnosis']
            notes = request.form['notes']
            date = datetime.now()

            db.PatientHistory.insert_one({
                "patient_id": patient_object_id,
                "appt_id": ObjectId(appt_id),
                "diagnosis": diagnosis,
                "notes": notes,
                "date": date
            })

            flash('Patient history updated successfully!', 'success')

    # Fetch patient information
    patient_info = db.Patients.find_one({"_id": patient_object_id})
    if not patient_info:
        flash(f"Patient not found for patient_id: {patient_id}", "danger")
        return redirect(url_for('staff.staff_dashboard'))

    # Fetch patient history
    patient_history = list(db.PatientHistory.find({"patient_id": patient_object_id}))

    # Format dates in patient history
    for record in patient_history:
        if 'date' in record:
            if isinstance(record['date'], datetime):
                record['date'] = record['date'].strftime('%Y-%m-%d')
            elif isinstance(record['date'], str):
                try:
                    # Try to parse the string date and format it
                    date_obj = datetime.strptime(record['date'], '%Y-%m-%d')
                    record['date'] = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    record['date'] = record['date']  # Keep original string if parsing fails

    # Fetch past prescriptions
    past_prescriptions = list(db.Prescriptions.aggregate([
        {"$match": {"patient_id": patient_object_id}},
        {"$lookup": {
            "from": "Medications",
            "localField": "med_id",
            "foreignField": "_id",
            "as": "medication_details"
        }},
        {"$unwind": "$medication_details"},
        {"$project": {
            "prescription_id": "$_id",
            "medication_name": "$medication_details.name",
            "dosage": 1,
            "date": 1,
            "notes": 1
        }}
    ]))

    # Format dates in prescriptions
    for prescription in past_prescriptions:
        if 'date' in prescription:
            if isinstance(prescription['date'], datetime):
                prescription['date'] = prescription['date'].strftime('%Y-%m-%d')
            elif isinstance(prescription['date'], str):
                try:
                    # Try to parse the string date and format it
                    date_obj = datetime.strptime(prescription['date'], '%Y-%m-%d')
                    prescription['date'] = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    prescription['date'] = prescription['date']  # Keep original string if parsing fails

    return render_template('view_patient.html', 
                         patient=patient_info, 
                         history=patient_history, 
                         prescriptions=past_prescriptions, 
                         appt_id=appt_id)


# Fetch medications route
@staff_bp.route('/fetch_medications')
def fetch_medications():
    query = request.args.get('query', '')
    db = get_db_connection()

    # Fetch medications that match the user's input
    medications = list(db.Medications.find({"name": {"$regex": query, "$options": "i"}}))

    # Prepare response data based on columns in med table
    medication_list = [
        {
            'name': med['name'],
            'form': med['form'],
            'dosage': med['dosage']
        }
        for med in medications
    ]

    return jsonify(medication_list)

# Advanced search routes
# Search feature for staff only using different parameters to find patients
@staff_bp.route('/advanced_search', methods=['POST'])
def advanced_search():
    if 'is_staff' not in session or session['is_staff'] != 1:
        return jsonify({'error': 'Unauthorized'}), 403

    db = get_db_connection()

    pipeline = [
        {
            '$lookup': {
                'from': 'Users',
                'localField': 'UserID',
                'foreignField': '_id',
                'as': 'user'
            }
        },
        {
            '$unwind': '$user'
        },
        # Add PatientHistory lookup by default
        {
            '$lookup': {
                'from': 'PatientHistory',
                'let': { 'patient_id': '$_id' },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': { '$eq': ['$patient_id', '$$patient_id'] }
                        }
                    },
                    {
                        '$sort': { 'date': -1 }
                    },
                    {
                        '$limit': 1
                    }
                ],
                'as': 'latest_history'
            }
        },
        {
            '$addFields': {
                'latest_diagnosis': {
                    '$cond': {
                        'if': { '$gt': [{ '$size': '$latest_history' }, 0] },
                        'then': { '$arrayElemAt': ['$latest_history.diagnosis', 0] },
                        'else': 'No diagnosis'
                    }
                },
                'diagnosis_date': {
                    '$cond': {
                        'if': { '$gt': [{ '$size': '$latest_history' }, 0] },
                        'then': { '$arrayElemAt': ['$latest_history.date', 0] },
                        'else': None
                    }
                }
            }
        }
    ]

    # Build match conditions
    match_conditions = {
        'user.IsStaff': 0
    }

    # Get form data for all fields
    username = request.form.get('username', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    contact_number = request.form.get('contact_number', '')
    patient_name = request.form.get('patient_name', '')
    nric = request.form.get('nric', '')
    gender = request.form.get('gender', '')
    dob = request.form.get('dob', '')
    height = request.form.get('height', '')
    weight = request.form.get('weight', '')
    diagnosis = request.form.get('diagnosis', '')
    diagnosis_date = request.form.get('diagnosis_date', '')

    # Add filter conditions
    if username:
        match_conditions['user.Username'] = {'$regex': username, '$options': 'i'}
    if email:
        match_conditions['user.Email'] = {'$regex': email, '$options': 'i'}
    if address: 
        match_conditions['user.Address'] = {'$regex': address, '$options': 'i'}
    if patient_name:
        match_conditions['PatientName'] = {'$regex': patient_name, '$options': 'i'}
    if contact_number:  
        match_conditions['user.ContactNumber'] = {'$regex': contact_number, '$options': 'i'}
    if nric:
        match_conditions['NRIC'] = {'$regex': nric, '$options': 'i'}
    if gender:
        if gender in ['Male', 'Female']:
            gender_map = {'Male': 'M', 'Female': 'F'}
            match_conditions['PatientGender'] = gender_map[gender]
    if height:
        try:
            match_conditions['PatientHeight'] = float(height)
        except ValueError:
            pass
    if weight:
        try:
            match_conditions['PatientWeight'] = float(weight)
        except ValueError:
            pass
    if dob:
        try:
            match_conditions['PatientDOB'] = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            pass
    if diagnosis:
        match_conditions['latest_diagnosis'] = {'$regex': diagnosis, '$options': 'i'}
    if diagnosis_date:
        try:
            diag_date = datetime.strptime(diagnosis_date, '%Y-%m-%d')
            match_conditions['diagnosis_date'] = diag_date
        except ValueError:
            pass

    # Add match conditions to pipeline
    if match_conditions:
        pipeline.append({'$match': match_conditions})

    try:
        patients = list(db.Patients.aggregate(pipeline))
        
        # Format dates and convert ObjectIds to strings
        for patient in patients:
            # Convert ObjectId to string
            patient['_id'] = str(patient['_id'])
            patient['UserID'] = str(patient['UserID'])
            
            # Convert user ObjectId
            if 'user' in patient:
                patient['user']['_id'] = str(patient['user']['_id'])
            
            # Format dates
            if 'PatientDOB' in patient and patient['PatientDOB']:
                if isinstance(patient['PatientDOB'], datetime):
                    patient['PatientDOB'] = patient['PatientDOB'].strftime('%Y-%m-%d')
                    
            if 'diagnosis_date' in patient and patient['diagnosis_date']:
                if isinstance(patient['diagnosis_date'], datetime):
                    patient['diagnosis_date'] = patient['diagnosis_date'].strftime('%Y-%m-%d')
                else:
                    patient['diagnosis_date'] = 'N/A'
            else:
                patient['diagnosis_date'] = 'N/A'

            # Clean up the temporary latest_history field
            if 'latest_history' in patient:
                del patient['latest_history']

        return json_util.dumps(patients)
    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'error': str(e)}), 500

# Staff only feature: edit appointments for patients
@staff_bp.route('/edit_appointment/<string:appt_id>', methods=['GET', 'POST'])
def edit_appointment(appt_id):
    db = get_db_connection()

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        status = request.form['status']
        reason = request.form['reason']

        db.Appointments.update_one({"_id": ObjectId(appt_id)}, {"$set": {
            "appt_date": datetime.strptime(date, '%Y-%m-%d'),
            "appt_time": time,
            "appt_status": status,
            "appt_reason": reason
        }})

        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('staff.manage_appointment'))

    appointment = db.Appointments.find_one({"_id": ObjectId(appt_id)})
    return render_template('edit_appointment.html', appointment=appointment)

@staff_bp.route('/staff_book_appointment', methods=['GET', 'POST'])
def staff_book_appointment():
    if 'user_id' not in session:
        flash('Please log in as staff to book an appointment.')
        return redirect(url_for('auth.login'))

    # Get the current date and the date one week from now
    today = datetime.now().date()
    one_week_later = today + timedelta(days=7)

    if request.method == 'POST':
        nric = request.form.get('patient_nric')
        appt_date = request.form.get('appt_date')
        appt_time = request.form.get('appt_time')
        appt_reason = request.form.get('appt_reason')

        # Validation
        if not all([nric, appt_date, appt_time, appt_reason]):
            flash('All fields are required.')
            return redirect(url_for('staff.staff_book_appointment'))

        try:
            appt_date_obj = datetime.strptime(appt_date, '%Y-%m-%d').date()
            appt_time_obj = datetime.strptime(appt_time, '%H:%M').time()
            
            if appt_time_obj.minute not in [0, 30]:
                flash('Appointments must be booked at 30-minute intervals.')
                return redirect(url_for('staff.staff_book_appointment'))
                
            if appt_date_obj < today or appt_date_obj > one_week_later:
                flash('Appointments can only be booked within the next 7 days.')
                return redirect(url_for('staff.staff_book_appointment'))

        except ValueError:
            flash('Invalid date or time format.')
            return redirect(url_for('staff.staff_book_appointment'))

        try:
            # Get database manager instance for atomic operations
            db_manager = DatabaseManager()
            db = db_manager.get_db()

            # Find the patient by NRIC
            patient = db.Patients.find_one({"NRIC": nric})
            if not patient:
                flash('Patient NRIC not found. Please contact support.')
                return redirect(url_for('staff.staff_book_appointment'))

            # Convert date/time for MongoDB
            appt_date_datetime = datetime.combine(appt_date_obj, datetime.min.time())
            appt_time_str = appt_time_obj.strftime('%H:%M')

            # Prepare appointment data
            appointment_data = {
                "patient_id": patient['_id'],
                "appt_date": appt_date_datetime,
                "appt_time": appt_time_str,
                "appt_status": 'Pending',
                "appt_reason": appt_reason
            }

            # Use atomic booking operation
            if db_manager.atomic_book_appointment(appointment_data):
                flash('Appointment booked successfully!', 'success')
                return redirect(url_for('staff.staff_dashboard'))
            else:
                flash('This appointment slot is already taken. Please choose another time.')
                return redirect(url_for('staff.staff_book_appointment'))

        except Exception as e:
            flash(f'An error occurred while booking the appointment: {str(e)}', 'danger')
            return redirect(url_for('staff.staff_book_appointment'))

    # For GET request, render the booking form
    return render_template('staff_book_appointment.html', min_date=today, max_date=one_week_later)

# Delete appointments route
@staff_bp.route('/delete_appointment/<string:appt_id>', methods=['POST'])
def delete_appointment(appt_id):
    db = get_db_connection()
    db.Appointments.delete_one({"_id": ObjectId(appt_id)})

    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('staff.manage_appointment'))

# Update ApptStatus route
@staff_bp.route('/complete_appointment/<string:appt_id>', methods=['POST'])
def complete_appointment(appt_id):
    db = get_db_connection()

    try:
        db.Appointments.update_one({"_id": ObjectId(appt_id)}, {"$set": {"appt_status": 'Completed'}})
        flash('Appointment completed successfully!', 'success')
    except Exception as e:
        flash('Error completing the appointment: {}'.format(str(e)), 'danger')

    return redirect(url_for('staff.manage_appointment'))
