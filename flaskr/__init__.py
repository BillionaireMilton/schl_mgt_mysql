
# Milton Codes School Api Project ;)
import json
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt

# from flask_migrate import Migrate

from models import setup_db, School, Teacher


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    bcrypt = Bcrypt(app)

    # db = SQLAlchemy()
    # migrate = Migrate(app, db)
    setup_db(app)

    CORS(app)

 ## ________________________________________________________________________ ##
 # this basically allows for after request trigger
 ## ________________________________________________________________________ ##
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

 ## ________________________________________________________________________ ##
 # these are the error handlers
 ## ________________________________________________________________________ ##
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
        "success": False, 
        "error": 409,
        "message": "one of the required infos already exists"
        }), 409
        
    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
        "success": False, 
        "error": 405,
        "message": "method not allowed"
        }), 405
 ## ________________________________________________________________________ ##
 ## ________________________________________________________________________ ##


 ## ________________________________________________________________________ ##
 # Schools Api Introduction
 ## ________________________________________________________________________ ##

    @app.route('/')
    def hello_schl():
        return 'Welcome to school management api!'


 ## ________________________________________________________________________ ##
 # view all Schools
 ## ________________________________________________________________________ ##
    @app.route('/schools', methods=['GET', 'POST'])
    def schools():

        ## ___________________________________________ ##
        ## IF METHOD IS GET
        ## ___________________________________________ ##
        if request.method=='GET':
            page = request.args.get('page', 1, type=int) #this is for pagination purpose 
            start = (page - 1) * 10 # state the start
            end = start + 10 # state the end
            schools = School.query.order_by(School.id).all()
            # if schools is None:
            if len(schools) < 1:
                abort(404)
            else:  
                formatted_schools = [school.format() for school in schools]
                return jsonify({
                    'success': True,
                    # this is how you normally do it
                    'schools': formatted_schools,
                    # but to paginate you use the below approach 
                    # 'schools': formatted_schools[start:end],
                    'total_schools': len(formatted_schools)
                })
        ## ___________________________________________ ##
        ## IF METHOD IS POST
        ## ___________________________________________ ##
        if request.method=='POST':
            body = request.get_json()

            new_school_name = body.get('school_name', None)
            new_school_owner = body.get('school_owner', None)
            new_school_email = body.get('school_email', None)
            new_school_phone = body.get('school_phone', None)
            new_school_address = body.get('school_address', None)
            new_school_password = body.get('school_password', None)
            new_school_type = body.get('school_type', None)
            new_school_status = body.get('school_status', None)
            new_date_added = datetime.now(timezone.utc)
            search = body.get('search', None)

            # try:
            ## ___________________________________________ ##
            #  added this. if  judgment sentence for search
            ## ___________________________________________ ##
            if search:
                selection = School.query.order_by(School.id).filter(School.school_name.ilike('%{}%'.format(search)))
                # current_schools = paginate_schools(request, selection)
                schools = [school.format() for school in selection]
                if len(schools) == 0:
                    abort(404)
                else:
                    return jsonify(
                        {
                            'success': True,
                            'schools': schools,
                            'total_schools': len(selection.all())
                        }
                    )
            ## ___________________________________________ ##
            ## For adding new school
            ## ___________________________________________ ##
            else:
                school = School(
                    school_name=new_school_name,
                    school_owner=new_school_owner,
                    school_email=new_school_email,
                    school_phone=new_school_phone,
                    school_address=new_school_address,
                    school_password=new_school_password,
                    school_type=new_school_type,
                    school_status=new_school_status,
                    date_added=new_date_added
                )
                print(school)
                school_name_exists = bool(School.query.filter_by(school_name=new_school_name).first())
                school_email_exists = bool(School.query.filter_by(school_email=new_school_email).first())
                school_phone_exists = bool(School.query.filter_by(school_phone=new_school_phone).first())
                if school_name_exists or school_email_exists or school_phone_exists:
                    abort(409)
                else:
                    school.insert()

                    selection = School.query.order_by(School.id).all()
                    schools = [school.format() for school in selection]
                    new_school = School.query.filter(School.school_name==new_school_name).one_or_none()


                    return jsonify({
                        "success": True,
                        "new_school": new_school.format(),
                        "total_schools": len(School.query.all())
                        })
            # except:
            #     abort(422)

 ## ________________________________________________________________________ ##
 # School Login
 ## ________________________________________________________________________ ##
    @app.route('/school/login', methods=["POST"])
    def school_login():
        if request.method == "POST":
            body = request.get_json()
            auth_school_email = body.get('school_email', None)
            auth_school_password = body.get('school_password', None)
            found_School = School.query.filter_by(school_email=auth_school_email).first()
            if found_School:
                print(found_School.school_name)
                if found_School.school_password is not None:
                    authenticated_School = bcrypt.check_password_hash(found_School.school_password, auth_school_password)
                    if authenticated_School:
                        the_school = School.query.filter(School.school_email==auth_school_email).one_or_none()
                        auth_school = the_school.format()
                        return jsonify({
                            "success": True,
                            "auth_school": auth_school,
                            "login_access": "Approved"
                            })
                    else:
                        abort(400)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            abort(405)

 ## ________________________________________________________________________ ##
 # Set School password
 ## ________________________________________________________________________ ##
    @app.route('/school/set-password', methods=["POST"])
    def set_school_password():
        if request.method == "POST":
            body = request.get_json()
            auth_school_email = body.get('school_email', None)
            auth_school_password = body.get('school_password', None)
            found_School = School.query.filter_by(school_email=auth_school_email).first()
            if found_School:
                the_school = School.query.filter(School.school_email==auth_school_email).one_or_none()
                # below function is to check if password hasn't been created already
                # but deprecated till further notice
            # if found_School.school_password is None:
                if 'school_password' in body:
                    the_school.school_password = bcrypt.generate_password_hash(body['school_password']).decode('UTF-8')
                the_school.update()
                auth_school = the_school.format()
                return jsonify({
                    "success": True,
                    "auth_school": auth_school,
                    "password_reset": "Successfully"
                    })
            # else:
            #     abort(404)
            else:
                abort(404)
        else:
            abort(405)



 ## ________________________________________________________________________ ##
 # Get School by Name
 ## ________________________________________________________________________ ##
    @app.route('/school/<string:school_name>', methods=["GET"])
    def get_school(school_name):
        school = School.query.filter(School.school_name==school_name).one_or_none()
        if school is None:
            abort(404)
        else:  
            formatted_school =  school.format()
            return jsonify({
                'success': True,
                'school': formatted_school,
                'total_fetched': len([formatted_school])
            })



 ## ________________________________________________________________________ ##
 # Edit/Update specific School
 ## ________________________________________________________________________ ##
    @app.route('/schools/<int:school_id>', methods=['PATCH'])
    def update_school(school_id):
        data = request.get_json()
        print(data)
        school = School.query.filter(School.id == school_id).one_or_none()
        print(school.school_name)
        print(data['school_type'])

        if school is None:
            abort(404)
        
        if 'school_name' in data:
            print(data)
            school.school_name = data['school_name']
        
        if 'school_owner' in data:
            print(data)
            school.school_owner = data['school_owner']

        if 'school_email' in data:
            print(data)
            school.school_email = data['school_email']
        
        if 'school_phone' in data:
            print(data)
            school.school_phone = data['school_phone']

        if 'school_address' in data:
            print(data)
            school.school_address = data['school_address']
        
        if 'school_type' in data:
            print(data)
            school.school_type = data['school_type']

        if 'school_status' in data:
            print(data)
            school.school_status = data['school_status']
        print(school)
        school.update()

        # formatted_schools = [school for school in School.query.all()]
        formatted_schools = school.format()

        return jsonify({
            'success': True,
            'schools': formatted_schools
        })

 ## ________________________________________________________________________ ##
 ## TEACHERS
 ## ________________________________________________________________________ ##

    def responseJsonify(selection, sortedList):
        jsonify(
            {
                'success': True,
                'teachers': sortedList,
                'total_teachers': len(selection.all())
            })


  ## ________________________________________________________________________ ##
 # view all Teachers
 ## ________________________________________________________________________ ##
    @app.route('/teachers', methods=['GET', 'POST'])
    def teachers():

        ## ___________________________________________ ##
        ## IF METHOD IS GET
        ## ___________________________________________ ##
        if request.method=='GET':
            page = request.args.get('page', 1, type=int) #this is for pagination purpose 
            start = (page - 1) * 10 # state the start
            end = start + 10 # state the end
            teachers = Teacher.query.order_by(Teacher.id).all()
            # if teachers is None:
            if len(teachers) < 1:
                abort(404)
            else:  
                formatted_teachers = [teacher.format() for teacher in teachers]
                return jsonify({
                    'success': True,
                    # this is how you normally do it
                    'teachers': formatted_teachers,
                    # but to paginate you use the below approach 
                    # 'teachers': formatted_teachers[start:end],
                    'total_teachers': len(formatted_teachers)
                })
        ## ___________________________________________ ##
        ## IF METHOD IS POST
        ## ___________________________________________ ##
        if request.method=='POST':
            body = request.get_json()

            new_school_id = body.get('school_id', None)
            new_date_of_joining = body.get('date_of_joining', None)
            new_teacher_first_name = body.get('teacher_first_name', None)
            new_teacher_last_name = body.get('teacher_last_name', None)
            new_teacher_course = body.get('teacher_course', None)
            new_teacher_gender = body.get('teacher_gender', None)
            new_date_of_birth = body.get('date_of_birth', None)
            new_teacher_phone = body.get('teacher_phone', None)
            new_teacher_type = body.get('teacher_type', None)
            new_teacher_status = body.get('teacher_status', None)
            new_teacher_address = body.get('teacher_address', None)
            new_is_teaching = body.get('is_teaching', None)
            new_profile_image = body.get('profile_image', None)
            new_teacher_email = body.get('teacher_email', None)
            new_teacher_password = body.get('teacher_password', None)
            # new_teacher_password = bcrypt.generate_password_hash(body['teacher_password']).decode('UTF-8')
            search = body.get('search', None)

            # try:
            ## ___________________________________________ ##
            #  added this. if  judgment sentence for search
            ## ___________________________________________ ##

            if search:
                selection = Teacher.query.order_by(Teacher.id).filter(Teacher.teacher_first_name.ilike('%{}%'.format(search)))
                # current_teachers = paginate_teachers(request, selection)
                teachers = [teacher.format() for teacher in selection]
                if len(teachers) == 0:
                    abort(404)
                else:
                    return jsonify(
                        {
                            'success': True,
                            'teachers': teachers,
                            'total_teachers': len(selection.all())
                        }
                    )

            ## ___________________________________________ ##
            ## For adding new teacher
            ## ___________________________________________ ##
            else:
                teacher = Teacher(
                    school_id=new_school_id,
                    date_of_joining=new_date_of_joining,
                    teacher_first_name=new_teacher_first_name,
                    teacher_last_name=new_teacher_last_name,
                    teacher_course=new_teacher_course,
                    teacher_gender=new_teacher_gender,
                    date_of_birth=new_date_of_birth,
                    teacher_phone=new_teacher_phone,
                    teacher_type=new_teacher_type,
                    teacher_status=new_teacher_status,
                    teacher_address=new_teacher_address,
                    is_teaching=new_is_teaching,
                    profile_image=new_profile_image,
                    teacher_email=new_teacher_email,
                    teacher_password=new_teacher_password,
                )
                print(teacher)
                teacher_first_name_exists = bool(Teacher.query.filter_by(teacher_first_name=new_teacher_first_name).first())
                teacher_last_name_exists = bool(Teacher.query.filter_by(teacher_last_name=new_teacher_last_name).first())
                teacher_email_exists = bool(Teacher.query.filter_by(teacher_email=new_teacher_email).first())
                teacher_phone_exists = bool(Teacher.query.filter_by(teacher_phone=new_teacher_phone).first())
                if teacher_email_exists or teacher_phone_exists:
                    abort(409)
                else:
                    teacher.insert()

                    selection = Teacher.query.order_by(Teacher.id).all()
                    teachers = [teacher.format() for teacher in selection]
                    new_teacher = Teacher.query.filter(Teacher.teacher_email==new_teacher_email).one_or_none()


                    return jsonify({
                        "success": True,
                        "new_teacher": new_teacher.format(),
                        "total_teachers": len(Teacher.query.all())
                        })
            # except:
            #     abort(422)

 ## ________________________________________________________________________ ##
 # Teacher Login
 ## ________________________________________________________________________ ##
    @app.route('/teacher/login', methods=["POST"])
    def teacher_login():
        if request.method == "POST":
            body = request.get_json()
            auth_teacher_email = body.get('teacher_email', None)
            auth_teacher_password = body.get('teacher_password', None)
            found_Teacher = Teacher.query.filter_by(teacher_email=auth_teacher_email).first()
            if found_Teacher:
                print(found_Teacher.teacher_first_name + " " + found_Teacher.teacher_last_name)
                if found_Teacher.teacher_password is not None:
                    print(found_Teacher.teacher_first_name + " password:" + found_Teacher.teacher_password)
                    authenticated_Teacher = bcrypt.check_password_hash(found_Teacher.teacher_password, auth_teacher_password)
                    if authenticated_Teacher:
                        the_teacher = Teacher.query.filter(Teacher.teacher_email==auth_teacher_email).one_or_none()
                        auth_teacher = the_teacher.format()
                        return jsonify({
                            "success": True,
                            "auth_teacher": auth_teacher,
                            "login_access": "Approved"
                            })
                    else:
                        abort(400)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            abort(405)
 ## ________________________________________________________________________ ##
 # Set School password
 ## ________________________________________________________________________ ##
    @app.route('/teacher/set-password', methods=["POST"])
    def set_teacher_password():
        if request.method == "POST":
            body = request.get_json()
            auth_teacher_email = body.get('teacher_email', None)
            auth_teacher_password = body.get('teacher_password', None)
            found_Teacher = Teacher.query.filter_by(teacher_email=auth_teacher_email).first()
            if found_Teacher:
                the_teacher = Teacher.query.filter(Teacher.teacher_email==auth_teacher_email).one_or_none()
                # below function is to check if password hasn't been created already
                # but deprecated till further notice
            # if found_Teacher.teacher_password is None:
                if 'teacher_password' in body:
                    the_teacher.teacher_password = bcrypt.generate_password_hash(body['teacher_password']).decode('UTF-8')
                the_teacher.update()
                auth_teacher = the_teacher.format()
                return jsonify({
                    "success": True,
                    "auth_teacher": auth_teacher,
                    "password_reset": "Successfully"
                    })
            # else:
            #     abort(404)
            else:
                abort(404)
        else:
            abort(405)



 ## ________________________________________________________________________ ##
 # Get Teacher by id
 ## ________________________________________________________________________ ##
    @app.route('/teacher/<string:teacher_id>', methods=["GET"])
    def get_teacher(teacher_id):
        teacher = Teacher.query.filter(Teacher.id==teacher_id).one_or_none()
        if teacher is None:
            abort(404)
        else:  
            formatted_teacher =  teacher.format()
            return jsonify({
                'success': True,
                'teacher': formatted_teacher,
                'total_fetched': len([formatted_teacher])
            })


 ## ________________________________________________________________________ ##
 # Edit/Update specific Teacher
 ## ________________________________________________________________________ ##
    @app.route('/teacher/<int:teacher_id>', methods=['PATCH'])
    def update_teacher(teacher_id):
        data = request.get_json()
        print(data)
        teacher = Teacher.query.filter(Teacher.id == teacher_id).one_or_none()
        print(teacher.teacher_first_name)
        print(data['teacher_phone'])

        if teacher is None:
            abort(404)
        
        if 'school_id' in data:
            print(data)
            teacher.school_id = data['school_id']

        if 'date_of_joining' in data:
            print(data)
            teacher.date_of_joining = data['date_of_joining']

        if 'teacher_first_name' in data:
            print(data)
            teacher.teacher_first_name = data['teacher_first_name']

        if 'teacher_last_name' in data:
            print(data)
            teacher.teacher_last_name = data['teacher_last_name']
        
        if 'teacher_course' in data:
            print(data)
            teacher.teacher_course = data['teacher_course']
        
        if 'teacher_gender' in data:
            print(data)
            teacher.teacher_gender = data['teacher_gender']
        
        if 'date_of_birth' in data:
            print(data)
            teacher.date_of_birth = data['date_of_birth']
        
        if 'teacher_phone' in data:
            print(data)
            teacher.teacher_phone = data['teacher_phone']
                
        if 'teacher_type' in data:
            print(data)
            teacher.teacher_type = data['teacher_type']

        if 'teacher_status' in data:
            print(data)
            teacher.teacher_status = data['teacher_status']

        if 'teacher_address' in data:
            print(data)
            teacher.teacher_address = data['teacher_address']

        if 'is_teaching' in data:
            print(data)
            teacher.is_teaching = data['is_teaching']

        if 'profile_image' in data:
            print(data)
            teacher.profile_image = data['profile_image']

        if 'teacher_email' in data:
            print(data)
            teacher.teacher_email = data['teacher_email']
        print(teacher)
        teacher.update()

        # formatted_teachers = [teacher for teacher in Teacher.query.all()]
        formatted_teachers = teacher.format()

        return jsonify({
            'success': True,
            'teachers': formatted_teachers
        })
 ## ________________________________________________________________________ ##
 ## ________________________________________________________________________ ##

    
    return app
    

# export FLASK_APP=flaskr
# export FLASK_ENV=development
# export FLASK_DEBUG=True
# flask run --reload