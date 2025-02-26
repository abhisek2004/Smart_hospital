from flask import Blueprint,request,session,redirect,render_template,url_for,flash,send_file

from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib.styles import getSampleStyleSheet # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image # type: ignore
import qrcode #type:ignore
import io
from flask_bcrypt import Bcrypt
from modules.login_required import login_required
from modules.db import contact_collection,admin_collection,doctors_collection,appointment_collection,hospital_data_collection,hospital_discharge_collection,inventory_collection,patients_collection,superadmin_collection,stock_collection
admin_blueprint = Blueprint('admin_blueprint',__name__)
bcrypt = Bcrypt()

@admin_blueprint.route('/admin/', methods=['GET', 'POST'])
# @token_required('admin')
@login_required('admin')
def admin():
    hospital_name = session.get('hospital_name')
    print(hospital_name)
    total_appointment = appointment_collection.count_documents(
        {"hospital_name": hospital_name})
    data = hospital_data_collection.find_one({'hospital_name': hospital_name})
    if data:
        g_beds = data['number_of_general_beds']
        vacent_general = g_beds-data['occupied_general']
        icu_beds = data['number_of_icu_beds']
        vacent_icu = icu_beds-data['occupied_icu']
        v_beds = data['number_of_ventilators']
        vacent_ventilator = v_beds-data['occupied_ventilator']
        total_patient = patients_collection.count_documents(
            {'hospital_name': hospital_name})
        total_doc = doctors_collection.count_documents(
            {"hospital_name": hospital_name})
        nurses = data['total_number_of_nurses']
        staff = data['administrative_staff_count']

        return render_template('admin_dashboard.html', count=total_appointment, general_total=g_beds, icu_total=icu_beds, vantilator_total=v_beds, patient=total_patient, doc=total_doc,
                               vacent_general=vacent_general, vacent_icu=vacent_icu, vacent_ventilator=vacent_ventilator, hospital_name=hospital_name, nurses=nurses, staff=staff)
    else:
        return redirect('/admin/add_detail')


@login_required('admin')
def add_patient():
    if request.method == 'POST':
        name = request.form['Name']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        aadhaar = request.form['aadhaar']
        bed_type = request.form['bedtype']
        bed_no = request.form['bedno']

        session['bed_type'] = bed_type
        session['patient_name'] = name
        hospital_name_patient = session.get('hospital_name')
        if bed_type == 'general':
            data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'phone': phone,
                'email': email,
                "aadhaar": aadhaar,
                "bed_type": bed_type,
                "bed no": "G"+bed_no,
                "hospital_name": hospital_name_patient
            }
        elif bed_type == 'icu':
            data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'phone': phone,
                'email': email,
                "aadhaar": aadhaar,
                "bed_type": bed_type,
                "bed no": "I"+bed_no,
                "hospital_name": hospital_name_patient
            }

        else:
            data = {
                'name': name,
                'dob': dob,
                'gender': gender,
                'address': address,
                'phone': phone,
                'email': email,
                "aadhaar": aadhaar,
                "bed_type": bed_type,
                "bed no": "V"+bed_no,
                "hospital_name": hospital_name_patient
            }

        print(hospital_name_patient)

        patients_collection.insert_one(data)

        hospital_data_collection.update_one(
            {'hospital_name': hospital_name_patient},
            # Increment the occupied beds count by 1
            {'$inc': {f'occupied_{bed_type}': 1}}
        )
        return redirect(url_for('confirmation'))
    return render_template('add patient.html')


@admin_blueprint.route('/admin/patient_details', methods=['GET', 'POST'])
@login_required('admin')
def patient_details():
    patients = patients_collection.find(
        {'hospital_name': session.get('hospital_name')})
    return render_template('manage_patient.html', patients=patients)


@admin_blueprint.route("/admin/contact-us")
@login_required('admin')
def admin_contact_us():
    contacts = contact_collection.find()
    return render_template("manage_appointment.html", contacts=contacts)


@admin_blueprint.route('/admin/confirmation')
@login_required('admin')
def confirmation():
    return render_template('success_admin.html')


@admin_blueprint.route('/admin/manage_appointment', methods=['GET', 'POST'])
@login_required('admin')
def manage():
    hospital_name = session.get('hospital_name')
    appointments = appointment_collection.find(
        {"hospital_name": hospital_name})
    return render_template('manage_appointment.html', appointments=appointments)


@admin_blueprint.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        pa = request.form['password']
        password = bcrypt.generate_password_hash(pa).decode('utf-8')
        # print('this is executed')

        admin = admin_collection.find_one({'hospital_mail': username})
        if admin:
            # Compare the entered password with the stored hashed password
            if bcrypt.check_password_hash(admin['hospital_password'], pa):
                # print('this is executed')
                # token=jwt.encode({
                #     'user_username':username,
                #     'role':'admin',
                #     'exp':datetime.utcnow()+timedelta(hours=1)
                # },app.config['SECRET_KEY'],algorithm="HS256")

                # response=make_response(redirect('/admin'))
                # response.set_cookie('access_token',token,httponly=True)
                # response.set_cookie('user_username',username,httponly=True)
                session['username'] = username
                session['role'] = 'admin'
                admin_email = session['username']
                hospital_data = admin_collection.find_one(
                    {"hospital_mail": admin_email})
                hospital_name_doctor = hospital_data.get("hospital_name")
                session['hospital_name'] = hospital_name_doctor
                print(f'session details:{session}')
                # return response
                return redirect('/admin')

            else:
                flash('Wrong Password', 'error')
                return redirect('/admin_login')

        else:
            flash('User not found', 'error')
            return redirect('/admin_login')
    return render_template("login_admin.html")


@admin_blueprint.route('/admin/', methods=['GET', 'POST'])
# @token_required('admin')
@login_required('admin')
def login_by_admin():
    hospital_name = session.get('hospital_name')
    print(hospital_name)
    total_appointment = appointment_collection.count_documents(
        {"hospital_name": hospital_name})
    data = hospital_data_collection.find_one({'hospital_name': hospital_name})
    if data:
        g_beds = data['number_of_general_beds']
        vacent_general = g_beds-data['occupied_general']
        icu_beds = data['number_of_icu_beds']
        vacent_icu = icu_beds-data['occupied_icu']
        v_beds = data['number_of_ventilators']
        vacent_ventilator = v_beds-data['occupied_ventilator']
        total_patient = patients_collection.count_documents(
            {'hospital_name': hospital_name})
        total_doc = doctors_collection.count_documents(
            {"hospital_name": hospital_name})
        nurses = data['total_number_of_nurses']
        staff = data['administrative_staff_count']

        return render_template('admin_dashboard.html', count=total_appointment, general_total=g_beds, icu_total=icu_beds, vantilator_total=v_beds, patient=total_patient, doc=total_doc,
                               vacent_general=vacent_general, vacent_icu=vacent_icu, vacent_ventilator=vacent_ventilator, hospital_name=hospital_name, nurses=nurses, staff=staff)
    else:
        return redirect('/admin/add_detail')


# @admin.route("/admin/contact-us")
# @login_required('admin')
# def admin_contact_us():
#     contacts = contact_collection.find()
#     return render_template("manage_appointment.html", contacts=contacts)


@admin_blueprint.route('/admin/add_detail', methods=['GET', 'POST'])
@login_required('admin')
def add_details():
    if request.method == 'POST':
        name = request.form['hospitalName']
        ID = request.form['hospitalID']
        address1 = request.form['addressLine1']
        city = request.form['city']
        state = request.form['stateProvince']
        postal_code = request.form['postalCode']
        contact_number = request.form['contactNumber']
        emergency = request.form['emergencyContactNumber']
        email = request.form['emailAddress']
        website = request.form['websiteURL']
        no_beds = int(request.form['numberOfBeds'])
        occupied_beds = int(request.form['Beds_occupied'])
        no_icu = int(request.form['numberOfICUBeds'])
        occupied_icu = int(request.form['icu_occupied'])
        no_ventilator = int(request.form['numberOfVentilators'])
        occupied_ventilator = int(request.form['ventilator_occupied'])
        emergency_dept = request.form['emergencyDepartment']
        spetialisation = request.form['specialization']
        operating_hour = request.form['hospitalOperatingHours']
        visiting_hour = request.form['visitingHours']
        pharmacy_onsite = request.form['pharmacyOnSite']
        no_nurse = int(request.form['totalNumberOfNurses'])
        no_admin_staff = int(request.form['administrativeStaffCount'])
        ambulance = request.form['ambulanceServices']
        bload_bank = request.form['bloodBank']
        diagonis_services = request.form['diagnosticServices']

        data = {
            "hospital_name": name,
            "hospital_id": ID,
            "address_line1": address1,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "contact_number": contact_number,
            "emergency_contact_number": emergency,
            "email_address": email,
            "website_url": website,
            "number_of_general_beds": no_beds,
            "occupied_general": occupied_beds,
            "number_of_icu_beds": no_icu,
            "occupied_icu": occupied_icu,
            "number_of_ventilators": no_ventilator,
            "occupied_ventilator": occupied_ventilator,
            "emergency_department": emergency_dept,
            "specialization": spetialisation,
            "hospital_operating_hours": operating_hour,
            "visiting_hours": visiting_hour,
            "pharmacy_on_site": pharmacy_onsite,
            "total_number_of_nurses": no_nurse,
            "administrative_staff_count": no_admin_staff,
            "ambulance_services": ambulance,
            "blood_bank": bload_bank,
            "diagnostic_services": diagonis_services}

    # Insert the data into the hospital collection
        hospital_data_collection.insert_one(data)
        return redirect('/admin')
    return render_template('hospital_details.html',)


@admin_blueprint.route('/add_doc', methods=['POST', 'GET'])
# @token_required('admin')
@login_required('admin')
def doctor_register():
    if request.method == 'POST':
        name = request.form['doctor_name']
        specialization = request.form['specialization']
        qualification = request.form['qualification']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        phone = request.form['phone']
        aadhar = request.form['aadhaar']
        # Doctor and hospital relation
        session['doctor_name'] = name
        admin_email = session['username']
        hospital_data = admin_collection.find_one(
            {"hospital_mail": admin_email})
        hospital_name_doctor = hospital_data.get("hospital_name")
        session['hospital_name'] = hospital_name_doctor

        # print(hospital_name_patient)
        doctor_data = {
            'name': name,
            'specialization': specialization,
            'qualification': qualification,
            'email': email,
            'username': username,
            'password': hash_password,
            'phone': phone,
            'aadhar': aadhar,
            "hospital_name": hospital_name_doctor
        }
        if doctors_collection.find_one({'username': username}) or doctors_collection.find_one({'email': email}):
            return redirect('/add_doc')
        else:
            doctors_collection.insert_one(doctor_data)
            return redirect('/admin')
        # return render_template('add doc.html')
    return render_template('add doc.html')


@admin_blueprint.route('/admin/inv_admin', methods=['GET', 'POST'])
@login_required('admin')
def inv_details():
    return render_template('inv_admin.html')


@admin_blueprint.route('/admin/inv_med_order', methods=['GET', 'POST'])
@login_required('admin')
def inv_med():
    if request.method == 'POST':
        medicine_name = request.form.get('medicine-name')
        medicine_composition = request.form.get('medicine-composition')
        medicine_quantity = request.form.get('medicine-quantity')
        order_comment = request.form.get('order-comment')
        hospital_name = session.get('hospital_name')
        # Create a document to insert into MongoDB
        order_data = {
            "medicine_name": medicine_name,
            "medicine_composition": medicine_composition,
            "medicine_quantity": int(medicine_quantity),  # Convert to integer
            "order_comment": order_comment,
            "hospital_name": hospital_name
        }

        # Insert the document into the inventory collection
        inventory_collection.insert_one(order_data)

    # return "Order submitted successfully!"
    return render_template('inv_med_order.html')

@admin_blueprint.route('/admin/inv_order_status', methods=['GET', 'POST'])
@login_required('admin')
def order_status():
    # data=
    datas = inventory_collection.find(
        {'hospital_name': session.get('hospital_name')})

    return render_template('inv_order_status.html', datas=datas)


@admin_blueprint.route('/admin/inv_stock_product', methods=['GET', 'POST'])
@login_required('admin')
def stock_details():
    return render_template('inv_stock_product.html')


@admin_blueprint.route('/admin/discharge', methods=['POST', 'GET'])
@login_required('admin')
def submit_discharge():
    if request.method == 'POST':
        # Extracting form data
        patient_id = request.form.get('patient_id')
        patient_name = request.form.get('patient_name')
        admission_date = request.form.get('admission_date')
        discharge_date = request.form.get('discharge_date')
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        doctor_name = request.form.get('doctor_name')
        discharge_summary = request.form.get('discharge_summary')
        follow_up_instructions = request.form.get('follow_up_instructions')
        medications = request.form.get('medications')
        contact_info = request.form.get('contact_info')
        gender = request.form.get('gender')
        address = request.form.get('address')
        bed_type = request.form.get('bedtype')

        hospital_name_patient = session.get('hospital_name')
        data_discharge = {
            'patient_id': patient_id,
            'patient_name': patient_name,
            'admission_date': admission_date,
            'discharge_date': discharge_date,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'doctor_name': doctor_name,
            'discharge_summary': discharge_summary,
            'follow_up_instructions': follow_up_instructions,
            'medications': medications,
            'contact_info': contact_info,
            'gender': gender,
            'address': address
        }
        hospital_discharge_collection.insert_one(data_discharge)
        hospital_data_collection.update_one(
            {'hospital_name': hospital_name_patient},
            # Increment the occupied beds count by 1
            {'$inc': {f'occupied_{bed_type}': -1}}
        )
        # Generate PDF with the provided details
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        # Patient details inside the pdf
        elements = []
        elements.append(Paragraph("Patient ID Card", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(f"Full Name: {patient_name}", styles['Normal']))
        elements.append(Paragraph(f"Admission Date: {                       admission_date}", styles['Normal']))
        elements.append(Paragraph(f"Gender: {gender}", styles['Normal']))
        elements.append(Paragraph(f"Address: {address}", styles['Normal']))
        elements.append(Paragraph(f"Phone Number: {contact_info}", styles['Normal']))
        elements.append(Paragraph(f"Diagnosis: {diagnosis}", styles['Normal']))
        elements.append(Paragraph(f"Discharge Summary: {discharge_summary}", styles['Normal']))

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(
            f"Name: {patient_name}\Admission Date: {admission_date}\nPhone: {contact_info}\nDischarge Summary: {diagnosis}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_buffer = io.BytesIO()
        img.save(qr_buffer, 'PNG')
        qr_buffer.seek(0)

        # Add QR code to PDF
        elements.append(Spacer(1, 12))
        elements.append(Image(qr_buffer, width=100, height=100))

        doc.build(elements)

        pdf_buffer.seek(0)
        # @after_this_request
        # def redirect_to_admin(reponse=302):
        #     return redirect('/admin')
        return send_file(pdf_buffer, as_attachment=True, download_name='patient_id_card.pdf', mimetype='application/pdf')
        # return redirect('/admin')
    return render_template('Patient_discharge.html')