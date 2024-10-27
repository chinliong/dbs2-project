from flask import render_template, request, redirect, session, url_for, flash
from . import medication_bp
from db import get_db_connection
from datetime import datetime
from bson.objectid import ObjectId

@medication_bp.route('/medications')
def medications():
    if not session.get('is_staff') == 1:
        flash("You do not have permission to access the Medication List.")
        return redirect(url_for('patient.patient_dashboard'))

    db = get_db_connection()
    medications_collection = db['Medications']

    # Get the search query from the URL parameters (GET request)
    search_query = request.args.get('search')

    if search_query:
        # Filter medications by name using a case-insensitive regex
        medications = list(medications_collection.find({"name": {"$regex": search_query, "$options": "i"}}).sort("name", 1))
    else:
        # Fetch all medications sorted ASC by name
        medications = list(medications_collection.find().sort("name", 1))

    return render_template('medications.html', medications=medications)

# Medication quantity updates route
@medication_bp.route('/update_medication_quantity', methods=['POST'])
def update_medication_quantity():
    if not session.get('is_staff') == 1:
        flash("You do not have permission to update medication quantities.")
        return redirect(url_for('patient.patient_dashboard'))

    # Get the form data
    medication_id = request.form.get('medication_id')
    quantity_change = int(request.form.get('quantity_change'))

    # Check for valid medication and quantity
    if not medication_id or not quantity_change:
        flash('Invalid input, please try again.', 'danger')
        return redirect(url_for('medication.medications'))

    db = get_db_connection()
    medications_collection = db['Medications']
    inventory_logs_collection = db['InventoryLogs']

    # Fetch current quantity of the medication
    medication = medications_collection.find_one({"_id": ObjectId(medication_id)})

    if not medication:
        flash('Medication not found.', 'danger')
        return redirect(url_for('medication.medications'))

    # Update the quantity in the DB
    new_quantity = medication['quantity'] + quantity_change
    medications_collection.update_one({"_id": ObjectId(medication_id)}, {"$set": {"quantity": new_quantity}})

    # Add a tracking log to InventoryLogs collection based on the user input
    change_type = 'addition' if quantity_change > 0 else 'subtract'
    inventory_logs_collection.insert_one({
        "MedID": ObjectId(medication_id),
        "change_type": change_type,
        "quantity_changed": quantity_change,
        "date": datetime.now()
    })

    flash(f'Medication ID {medication_id} updated. New quantity: {new_quantity}', 'success')

    return redirect(url_for('medication.medications'))

# Adding med route
@medication_bp.route('/manage_medication', methods=['POST'])
def manage_medication():
    if not session.get('is_staff') == 1:
        flash("You do not have permission to add medications.")
        return redirect(url_for('patient.patient_dashboard'))

    # Get form data
    name = request.form.get('name')
    form = request.form.get('form')
    dosage = request.form.get('dosage')
    quantity = request.form.get('quantity')
    indication = request.form.get('indication')

    if not (name and form and dosage and quantity and indication):
        flash('All fields are required to add a medication.', 'danger')
        return redirect(url_for('medication.medications'))

    db = get_db_connection()
    medications_collection = db['Medications']

    # Insert new medication into the Medications collection
    medications_collection.insert_one({
        "name": name,
        "form": form,
        "dosage": dosage,
        "quantity": int(quantity),
        "indication": indication
    })

    flash(f'Medication "{name}" added successfully.', 'success')

    return redirect(url_for('medication.medications'))

# Deleting med route
@medication_bp.route('/delete_medication', methods=['POST'])
def delete_medication():
    if not session.get('is_staff') == 1:
        flash("You do not have permission to delete medications.")
        return redirect(url_for('patient.patient_dashboard'))

    medication_id = request.form.get('medication_id')

    if not medication_id:
        flash('Invalid medication ID, please try again.', 'danger')
        return redirect(url_for('medication.medications'))

    db = get_db_connection()
    medications_collection = db['Medications']

    # Pre-check to see if medication exists
    medication = medications_collection.find_one({"_id": ObjectId(medication_id)})

    if not medication:
        flash('Medication not found.', 'danger')
        return redirect(url_for('medication.medications'))

    # Delete the medication from the collection
    medications_collection.delete_one({"_id": ObjectId(medication_id)})

    flash(f'Medication ID {medication_id} deleted successfully.', 'success')

    return redirect(url_for('medication.medications'))