from dataclasses import dataclass
#from email import message
from flask import *  
import sqlite3
import os
import pandas as pd
import datetime as dt



app = Flask(__name__)  
app.secret_key = "abc" 

################################################################################
## Website Home Page Related Functions                                        ##
## -----------------------------------                                        ##
##                                                                            ##
## 1. Redirects to the login page (index.html                                 ##
##                                                                            ##
################################################################################
@app.route('/')  
def home():  
    return render_template("index.html")  


################################################################################
## User Login Related Functions                                               ##
## -----------------------------                                              ##
##                                                                            ##
## 1. Validate the existance of the user email id in the databas              ##
## 2. Validate the matching of the password                                   ##
## 3. If Matches redirect to the main menu                                    ##
##                                                                            ##
## index.html -> login -> menu.html or message.html                           ##
################################################################################
@app.route("/login",methods = ["POST","GET"])  
def login():  
    if request.method == "POST":  
        try:  
            Emailid = request.form["Emailid"]
            passwd=request.form["passwd"]
            with sqlite3.connect("IR40.db") as con:  
                con.row_factory = sqlite3.Row 
                cur = con.cursor()  
                sql_query="select * from Credentials where Emailid=?"
                cur.execute(sql_query,(Emailid,))  
                rows = cur.fetchall()
                if len(rows)==0:
                    return render_template("message.html", msg="Email ID Does Not Exist!, Check The Input ", ret="/")
                for row in rows:
                    if row["passwd"] == passwd:
                        session['Name']= row["Name"]
                        session['usergroup']=row["usergrp"]
                        session['userid']=row[1]

                        sql_query = "select * from deptnews where status='A'"
                        cur.execute(sql_query)
                        deptnews = cur.fetchall()

                        sql_query = "select * from clubnews where status='A'"
                        cur.execute(sql_query)
                        clubnews = cur.fetchall()

                        return render_template("menu.html", name=session['Name'],usrgrp=session['usergroup'], userid=session['userid'],deptnews=deptnews, clubnews=clubnews)
                    else:
                        return render_template("message.html", msg="Password Does Not Match", ret="/")
        except:  
            msg = "can't be Selected"   


################################################################################
## User Registration Functions                                                ##
## -----------------------------                                              ##
##                                                                            ##
## 1. Landing page from "Signup" link from login page                         ##
## 2. Redirects the sign-up form to take input details                        ##
## 3. When submitting the form the details transfered to function             ##
## 4. Fuction savedetails save the user details in the database               ##
## 5. Forward to Success or Failure message page                              ##
##                                                                            ##
## Signup -> signup.html -> savedetails -> message.html                       ##
################################################################################
@app.route('/signup')  
def signup():  
    return render_template("signup.html")  

@app.route("/savedetails",methods = ["POST","GET"])  
def saveDetails():  
    msg = "msg"  
    if request.method == "POST":  
        try:  
            emailid = request.form["Emailid"]
            id_no = request.form["id_no"]
            uname = request.form["uname"]  
            passwd = request.form["passwd"] 
            dept=request.form["dept"] 
            usergrp = request.form["usergrp"]  
            if usergrp=='P':
                dept=99
            
            with sqlite3.connect("IR40.db") as con:  
                cur = con.cursor()  
                
                insert_query="""INSERT into Credentials 
                (emailid,Id_no,Name,Passwd,Dept,usergrp) 
                values 
                (?,?,?,?,?,?)"""
                    
                cur.execute(insert_query,(emailid,id_no,uname,passwd,dept,usergrp))  
                con.commit()  
                msg = "User Record successfully Added"  
        except:  
            con.rollback()  
            msg = "We can not add the User to the list"  
        finally:  
            con.close()  
            return render_template("message.html",msg = msg, ret="/")  



################################################################################
## List User Records                                                          ##
## -----------------                                                          ##
##                                                                            ##
## 1. Called from main menu option "View Student Records"                     ##
## 2. Records fetched from database table and passed to view_userlist.html    ##
## 3. view_userlist.html displays the data in structed table formant          ##
## 4. From view_userlist.html return to main menu page                        ##
## 5. Option enabled only for Admin and Super Users                           ##
##                                                                            ##
## menu.html -> view_userlist(func) -> view_userlist.html -> menu.html        ##
################################################################################
@app.route("/view_userlist")
def view_userlist():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    sql_query = "select * from Credentials"
    cur.execute(sql_query)
    rows = cur.fetchall()
    return render_template("view_userlist.html", rows=rows, Name= session['Name'])

################################################################################
## Attendance Data Upload to Portal and Database                              ##
## ---------------------------------------------                              ##
##                                                                            ##
## 1. Called from main menu option "Attendance Data Upload"                   ##
## 2. Function upload_attendance called to fectch initial data from database  ##
## 3. Fetched data passed to upload_attendance_excel.html                     ##
## 4. upload_attendance_excel.html provides the following functions           ##
##    - Upload the attendance data shared in csv format                       ##
##    - View the attendacne csv data file content                             ##
##    - Upload the attendance data into database tables                       ##
##    - Delete the attendance data csv file from database and filesystem      ##
## 5. Once data is uploaded, the option of upload is disabled                 ##
## 6. Option enabled only for Admin and Super Users                           ##
##                                                                            ##
## menu.html -> upload_attenadance (func) -> upload_attendance_excel.html     ##
################################################################################
@app.route('/upload_attendance')
def upload_attendance():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from attendance_data")
    data = cur.fetchall()
    con.close()
    return render_template("upload_attendance_excel.html", data=data)

################################################################################
## For Upload the Attendance Data                                             ##
## -------------------------------                                            ##
## upload_attenance_excel.html -> upload_attendance_excel (func) ->           ##
##                             -> upload_attendance_excel.html                ##
################################################################################
@app.route("/upload_attendance_excel", methods=['GET','POST'])
def upload_attendance_excel():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from attendance_data")
    data = cur.fetchall()
    con.close()
    
    if request.method == 'POST':
        uploadExcel = request.files['uploadExcel']
        if uploadExcel.filename != '':
            app.config['UPLOAD_FOLDER']= os.getcwd()+"/static"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploadExcel.filename)
            uploadExcel.save(filepath)
            con = sqlite3.connect("IR40.db")
            cur = con.cursor()
            cur.execute("insert into attendance_data(exceldata)values(?)", (uploadExcel.filename,))
            con.commit()
            flash("Excel Sheet Upload Successfully", "success")

            con = sqlite3.connect("IR40.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("select * from attendance_data")
            data = cur.fetchall()
            con.close()
            return render_template("upload_attendance_excel.html", data=data)

    return render_template("upload_attendance_excel.html",data=data)    


################################################################################
## To View the Attendance Data                                                ##
## -------------------------------                                            ##
## upload_attenance_excel.html -> view_attendance_data(func) ->               ##
## view_attendance_data.html-> upload_attendance_excel (func) ->              ##
## upload_attendance_excel.html                                               ##
################################################################################
@app.route('/view_attendance_data/<string:id>')
def view_attendance_data(id):
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from attendance_data where pid=?",(id))
    data = cur.fetchall()
    cwd = os.getcwd()+"/static"
    print(data)
    for val in data:
        path = os.path.join(cwd,val[1])
        print(val[1])
        data=pd.read_csv(path)
    con.close()
    return render_template("view_attendance_data.html",fname=val[1], data=data.to_html(index=False,classes="table table-bordered").replace('<th>','<th style="text-align:center">'))

################################################################################
## Insert Attendance Records from CSV/Excel to Database                       ##
## -----------------------------------------------------                      ##
##                                                                            ##
## upload_attenance_excel.html -> insert_attendance_into_db (func) ->         ##
## -> message.html -> upload_attendance_excel (func) ->                       ##
## -> upload_attendance_excel.html                                            ##
################################################################################
@app.route("/insert_attendance_into_db/<string:id>")
def insert_attendance_into_db(id):
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from attendance_data where pid=?",(id))
    data = cur.fetchall()
    print(data)
    cwd = os.getcwd()+"/static"
    for val in data:
        path = os.path.join(cwd,val[1])
        print(val[1])
        df=pd.read_csv(path)
    con.close()
    
    try:
        with sqlite3.connect("IR40.db") as con:
            cur = con.cursor()  

            for i in range(len(df)):
                Dept_id=int(df.iloc[i][0])
                Semester=int(df.iloc[i][1])
                Subject_Code=df.iloc[i][2]
                Faculty_id=int(df.iloc[i][3])
                Student_Code=int(df.iloc[i][4])
                Attendance_Date=df.iloc[i][5]
                Present_hours=int(df.iloc[i][6])
                Absent_hours=int(df.iloc[i][7])
                
                insert_query =""" INSERT into Attendance_Master
                    (Dept_id, Semester, Subject_Code, Faculty_id, Student_Code, Attendance_Date, Present_hours, Absent_hours)
                    values 
                    (?,?,?,?,?,?,?,?)"""
                
                cur.execute(insert_query,(Dept_id, Semester, Subject_Code, Faculty_id, Student_Code, Attendance_Date, Present_hours, Absent_hours))  
            con.commit()
            msg ="Attendance Records Updated to Database"

            cur.execute("update attendance_data set dbupdate='Y' where pid=?",[id])
            con.commit
    except:  
        con.rollback()  
        msg = "Database Insert Error!, Attendance Data Not Uploaded."  
    
    finally:  
        con.close()  
        return render_template("message.html",msg = msg, ret="/upload_attendance_excel")  
        

################################################################################
## Delete the Attendance Data                                                 ##
## ---------------------------   -                                            ##
## upload_attenance_excel.html -> delete_attendance_record (func) ->          ##
## -> upload_attendance_excel (func) -> upload_attendance_excel.html          ##
################################################################################

@app.route('/delete_attendance_record/<string:id>')
def delete_attendance_record(id):
    try:
        con=sqlite3.connect("IR40.db")
        con.row_factory = sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from attendance_data where pid=?",(id))
        data = cur.fetchall()
        cwd = os.getcwd()+"/static"
        for val in data:
            path = os.path.join(cwd,val[1])
            print(val[1])
        os.remove(path)    

        cur.execute("delete from attendance_data where pid=?",[id])
        con.commit()
        flash("Record Deleted Successfully","success")
    except:
        flash("Record Deleted Failed", "danger")
    finally:
        return redirect(url_for("upload_attendance_excel"))
        con.close()

################################################################################
## Course Data Upload to Portal and Database                                  ##
## ---------------------------------------------                              ##
##                                                                            ##
## 1. Called from main menu option "Course Data Upload"                       ##
## 2. Function upload_attendance called to fectch initial data from database  ##
## 3. Fetched data passed to upload_attendance_excel.html                     ##
## 4. upload_attendance_excel.html provides the following functions           ##
##    - Upload the attendance data shared in csv format                       ##
##    - View the attendacne csv data file content                             ##
##    - Upload the attendance data into database tables                       ##
##    - Delete the attendance data csv file from database and filesystem      ##
## 5. Once data is uploaded, the option of upload is disabled                 ##
## 6. Option enabled only for Admin and Super Users                           ##
##                                                                            ##
## menu.html -> upload_course (func) -> upload_course.html                    ##
################################################################################
@app.route("/upload_course", methods=['GET','POST'])
def upload_course():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Course_data")
    data = cur.fetchall()
    con.close()
    
    if request.method == 'POST':
        uploadExcel = request.files['uploadExcel']
        if uploadExcel.filename != '':
            app.config['UPLOAD_FOLDER']= os.getcwd()+"/static"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploadExcel.filename)
            uploadExcel.save(filepath)
            con = sqlite3.connect("IR40.db")
            cur = con.cursor()
            cur.execute("insert into Course_data (exceldata) values (?)", (uploadExcel.filename,))
            con.commit()
            flash("Excel Sheet Upload Successfully", "success")

            con = sqlite3.connect("IR40.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("select * from Course_data")
            data = cur.fetchall()
            con.close()
            return render_template("upload_course.html", data=data)

    return render_template("upload_course.html",data=data)    

################################################################################
## To View the Course Data                                                    ##
## ---------------------------                                                ##
## upload_course.html -> view_course(func) -> view_course.html ->             ##
## upload_course (func) > view_course.html                                    ##
################################################################################
@app.route('/view_course/<string:id>')
def view_course(id):
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Course_data where pid=?",(id))
    data = cur.fetchall()
    cwd = os.getcwd()+"/static"
    print(data)
    for val in data:
        path = os.path.join(cwd,val[1])
        print(val[1])
        data=pd.read_csv(path)
    con.close()
    return render_template("view_course.html",fname=val[1], data=data.to_html(index=False,classes="table table-bordered").replace('<th>','<th style="text-align:center">'))

################################################################################
## Insert Course Details Records from CSV/Excel to Database                   ##
## -----------------------------------------------------                      ##
##                                                                            ##
## upload_course.html -> insert_course_into_db (func) ->                      ##
## -> message.html -> upload_course (func) -> upload_course.html              ##
################################################################################
@app.route("/insert_course_into_db/<string:id>")
def insert_course_into_db(id):
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Course_data where pid=?",(id))
    data = cur.fetchall()
    cwd = os.getcwd()+"/static"
    print(data)
    for val in data:
        path = os.path.join(cwd,val[1])
        print(val[1])
        df=pd.read_csv(path)
    con.close()
    
    try:
        with sqlite3.connect("IR40.db") as con:
            cur = con.cursor()  

            for i in range(len(df)):
                Dept_id=int(df.iloc[i][0])
                Semester=int(df.iloc[i][1])
                Subject_Code=df.iloc[i][2]
                Faculty_id=int(df.iloc[i][3])
                Course_Credit=int(df.iloc[i][4])
                Course_Duration=int(df.iloc[i][5])
                
                insert_query =""" INSERT into Course_Master
                    (Dept_id, Semester, Subject_Code, Faculty_id, Course_Credit, Course_Duration)
                    values 
                    (?,?,?,?,?,?)"""
                
                cur.execute(insert_query,(Dept_id, Semester, Subject_Code, Faculty_id, Course_Credit, Course_Duration))  
            con.commit()
            msg ="Course Details Updated to Database"

            cur.execute("update Course_data set dbupdate='Y' where pid=?",[id])
            con.commit
    except:  
        con.rollback()  
        msg = "Database Insert Error!, Attendance Data Not Uploaded."  
    
    finally:  
        return render_template("message.html",msg = msg, ret="/upload_course")  
        con.close()  

################################################################################
## Delete the Course Details Data                                             ##
## -------------------------------                                            ##
## upload_course.html -> delete_course_record (func) -> upload_course (func)->##
## -> upload_course.html                                                      ##
################################################################################

@app.route('/delete_course_record/<string:id>')
def delete_course_record(id):
    try:
        con=sqlite3.connect("IR40.db")
        con.row_factory = sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from Course_data where pid=?",(id))
        data = cur.fetchall()
        cwd = os.getcwd()+"/static"
        for val in data:
            path = os.path.join(cwd,val[1])
            print(val[1])
        os.remove(path)    

        cur.execute("delete from Course_data where pid=?",[id])
        con.commit()
        flash("Record Deleted Successfully","success")
    except:
        flash("Record Deleted Failed", "danger")
    finally:
        return redirect(url_for("upload_course"))
        con.close()


################################################################################
## Assignment Document Upload to Portal                                       ##
## ------------------------------------                                       ##
##                                                                            ##
## 1. Called from main menu option "Assignment Document Upload"               ##
## 2. Function upload_assignment called to fectch initial data from database  ##
## 3. Fetched data passed to upload_assignment_document.html                  ##
## 4. upload_attendance_document.html provides the following functions        ##
##    - Upload the Assignment document into the portal                        ##
##    - View the Assignment document file content                             ##
##    - Delete the Assignment document file from database and filesystem      ##
## 5. Option enabled only for Faculty and Super Users                         ##
##                                                                            ##
## menu.html -> upload_assignment (func) -> upload_assignment_document.html   ##
################################################################################
@app.route("/upload_assignment", methods = ["POST","GET"])
def upload_assignment():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    select_query = """ SELECT pid, assign_file,
       STRFTIME('%d-%m-%Y %H:%M', upload_date), 
       STRFTIME('%d-%m-%Y %H:%M', due_date), 
       cast ((JulianDay(due_date) - JulianDay()) as integer) as difference       
       FROM assignments order by difference ASC"""

    cur.execute(select_query)
    data = cur.fetchall()
    con.close()
    
    if request.method == 'POST':
        uploadassignment = request.files['uploadassignment']
        duedate = request.form["duedate"]
        if uploadassignment.filename != '':
            app.config['UPLOAD_FOLDER']= os.getcwd()+"/static"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploadassignment.filename)
            uploadassignment.save(filepath)
            con = sqlite3.connect("IR40.db")
            cur = con.cursor()

            insert_query ="""insert into assignments
            (assign_file,upload_date,due_date)
            values
            (?,?,?)"""
            n = dt.datetime.today()
            tday = str(n.date())+" "+str(n.hour)+":"+str(n.minute)+":"+str(n.second)
            cur.execute(insert_query, (uploadassignment.filename,tday,duedate))
            con.commit()
            flash("Assignment Document Uploaded Successfully", "success")

            con = sqlite3.connect("IR40.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(select_query)
            data = cur.fetchall()
            con.close()
            return render_template("upload_assignment_document.html", data=data)
    return render_template("upload_assignment_document.html",data=data)    

################################################################################
## Delete the Assignment File                                                 ##
## ---------------------------                                                ##
## upload_assignment_document.html -> delete_assignment (func) ->             ##
## upload_assignment (func) -> upload_assignment_document.html                ##
################################################################################
@app.route('/delete_assignment/<string:id>')
def delete_assignment(id):
    try:
        con=sqlite3.connect("IR40.db")
        con.row_factory = sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from assignments where pid=?",(id))
        data = cur.fetchall()
        cwd = os.getcwd()+"/static"
        for val in data:
            path = os.path.join(cwd,val[1])
            print(val[1])
        os.remove(path)    

        cur.execute("delete from assignments where pid=?",[id])
        con.commit()
        flash("Record Deleted Successfully","success")
    except:
        flash("Record Deleted Failed", "danger")
    finally:
        return redirect(url_for("upload_assignment"))
        con.close()

################################################################################
## View the Assignment File Details                                           ##
## ---------------------------                                                ##
## menu.html -> view_assignment(func) -> view_assignment.html -> menu.html    ##
## menu.html -> view_assignment(func) -> message.html -> menu.html            ##
################################################################################
@app.route("/view_assignment", methods = ["POST","GET"])
def view_assignment():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    select_query = """ SELECT pid, assign_file,
       STRFTIME('%d-%m-%Y %H:%M', upload_date), 
       STRFTIME('%d-%m-%Y %H:%M', due_date), 
       cast ((JulianDay(due_date) - JulianDay()) as integer) as difference       
       FROM assignments order by difference ASC"""

    cur.execute(select_query)
    data = cur.fetchall()
    con.close()
    if len(data)==0:
        msg="No Assignments Uploaded!.. Contact the Faculty."
        return render_template("message.html", msg=msg, ret="/menu")

    return render_template("view_assignment.html",data=data)   




# Called when logout link is clicked in the main menu
@app.route('/logout')  
def logout():  
    if 'Name' in session:  
        username=session['Name']
        session.pop('Name',None)  
        session.pop('usergroup',None)
        session.pop('userid',None)
        return render_template('logout.html', msg=username);  
    else:  
        return '<p>User Already Logged Out</p>'  

# Called when return to main menu option clicked from sub pages
@app.route("/menu")
def menu_display():
    with sqlite3.connect("IR40.db") as con:  
        con.row_factory = sqlite3.Row 
        cur = con.cursor()  
        sql_query = "select * from deptnews"
        cur.execute(sql_query)
        deptnew = cur.fetchall()

        sql_query = "select * from clubnews"
        cur.execute(sql_query)
        clubnews = cur.fetchall()
        return render_template("menu.html", name=session['Name'],usrgrp=session['usergroup'], userid=session['userid'],deptnews=deptnew, clubnews=clubnews )


################################################################################
## Attendance Stats View                                                      ##
## ---------------------------                                                ##
## menu.html -> attendance_stats(func) -> view_stats.html -> menu.html        ##
##                                                                            ##
################################################################################
@app.route("/attendance_stats")       
def attendance_stats():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    userid=int(session['userid'])
    usergrp = session['usergroup']
    if usergrp=='A' or usergrp =='S':
        select_query = """ SELECT  a.Student_Code, a.Subject_Code, b.Course_Duration,
        sum(a.Present_hours) as Present_Hours,
        sum(a.Absent_hours) as Absent_Hours,
        sum(a.Present_hours)+sum(a.Absent_hours) as Total_Hours
        FROM Attendance_Master a,Course_Master b
        where a.subject_code=b.subject_code and
        a.student_code=?
        group by a.student_code,a.Subject_Code"""
        cur.execute(select_query,[userid])
    elif usergrp=='F' or usergrp=='Z':
        select_query = """ SELECT  a.Student_Code, a.Subject_Code, b.Course_Duration,
        sum(a.Present_hours) as Present_Hours,
        sum(a.Absent_hours) as Absent_Hours,
        sum(a.Present_hours)+sum(a.Absent_hours) as Total_Hours
        FROM Attendance_Master a,Course_Master b
        where a.subject_code=b.subject_code 
        group by a.student_code,a.Subject_Code"""
        cur.execute(select_query)

    data = cur.fetchall()
    con.close()
    if len(data)==0:
        msg="No Attendance Records Found!.. Contact the Portal Admin."
        return render_template("message.html", msg=msg, ret="/menu")
    return render_template("view_stats.html  ",data=data)   

################################################################################
## Upgrade a Student Profile to Admin User                                    ##
## ---------------------------------------------                              ##
################################################################################
@app.route("/upgrade_profile", methods = ["POST","GET"])
def upgrade_profile():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
   
    if request.method == "POST": 
        Id_no = "%"+request.form["Id_no"]+"%"
        select_query = """ SELECT * from Credentials where usergrp='S' and Id_no LIKE ? order by Id_no ASC"""
        cur.execute(select_query,(Id_no,))

    elif request.method =="GET":
        Id_no = request.args.get("Id_no")
        if  Id_no is None:
            select_query = """ SELECT * from Credentials where usergrp='S' order by Id_no ASC"""
            cur.execute(select_query)
        else:
            select_query = """ SELECT * from Credentials where usergrp='S' and Id_no=? order by Id_no ASC"""
            cur.execute(select_query,[Id_no])
    else:
        select_query = """ SELECT * from Credentials where usergrp='S' order by Id_no ASC"""
        cur.execute(select_query)

    data = cur.fetchall()
    con.close()
    return render_template("upgrade_profile.html", data=data, dataalert="N")

@app.route("/upgrade_profile_update", methods = ["POST","GET"])
def upgrade_profile_update():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    Id_no = request.args.get("id")
    if  Id_no is None:
        flash("Error!.. Student ID not passed to the Updater.", "success")
        return redirect(url_for("upgrade_profile"))
    else:
        update_query = """ update Credentials set usergrp='A' where Id_no=?"""
        cur.execute(update_query, [Id_no])
        con.commit()   
        con.close()         
        flash("Student Upgraded as Admin Successfully.", "success")
        return redirect(url_for("upgrade_profile"))
    
    
################################################################################
## Add News                                                                   ##
################################################################################
@app.route("/add_news")
def add_news():
    return render_template("add_news.html")

@app.route("/save_news",methods = ["POST","GET"])  
def save_news():  
    if request.method == "POST":  
        try:  
            newstext = request.form["newstext"]
            srcurl = request.form["srcurl"]
            newstype = request.form["news"]  

            with sqlite3.connect("IR40.db") as con:  
                cur = con.cursor()  
                if newstype =='D':               
                    insert_query="""INSERT into deptnews
                    (Newstext,url,status) 
                    values 
                    (?,?,?)"""
                    msg = "Department News Added Successfully"  
                else:
                    insert_query="""INSERT into clubnews
                    (Newstext,url,status) 
                    values 
                    (?,?,?)"""
                    msg = "Club News Added Successfully"  

                cur.execute(insert_query,(newstext,srcurl,'A'))  
                con.commit()  

        except:  
            con.rollback()  
            msg = "Cannot Add News To The List"  
        finally:  
            con.close()  
            return render_template("message.html", msg = msg, ret="/menu")  


################################################################################
## Deactivate News                                                                   ##
################################################################################
@app.route("/deactivate_news", methods=["POST","GET"])
def deactivate_news():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if request.method == "POST":  
        newstype = request.form["news"]  
        newstxt = "%"+request.form["newstxt"]+"%"
        if newstype=="D":
            select_query = """ SELECT * from deptnews where status='A' and Newstext LIKE ? """
        else:
            select_query = """ SELECT * from clubnews where status='A' and Newstext LIKE ? """
        cur.execute(select_query,(newstxt,))

    elif request.method =="GET":
        newstype = request.args.get("news")
        newstxt = request.args.get("newstxt")
        if  newstxt is None:
            select_query = """ SELECT * from deptnews where status='A' """
            newstype='D'
            cur.execute(select_query)
        else:
            if newstype=="D":
                select_query = """ SELECT * from deptnews where status='A' and Newstext LIKE ? """
            else:
                select_query = """ SELECT * from clubnews where status='A' and Newstext LIKE ? """
            cur.execute(select_query,(newstxt,))
    else:
        select_query = """ SELECT * from deptnews where status='A' """
        cur.execute(select_query)

    data = cur.fetchall()
    con.close()
    return render_template("deactivate_news.html", data=data, newstype=newstype)


@app.route("/deactivate_news_update",methods = ["POST","GET"])  
def deactivate_news_update():
    con = sqlite3.connect("IR40.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    Id_no = request.args.get("id")
    newstype = request.args.get("newstype")
    if  Id_no is None:
        flash("Error!.. News  ID not passed to the Updater.", "success")
        return redirect(url_for("deactivate_news"))
    else:
        if newstype =="D":
            update_query = """ update deptnews set status='D' where pid=?"""
        else:
            update_query = """ update clubnews set status='D' where pid=?"""

        cur.execute(update_query, [Id_no])
        con.commit()   
        con.close()         
        if newstype=="D":
            flash("Department News Deactivated Successfully.", "success")
        else:
            flash("Club News Deactivated Successfully.", "success")
        return redirect(url_for("deactivate_news"))
    



################################################################################
## Contact Us link from the Top Navigation Bar                                ##
################################################################################
@app.route("/view_contactus")       
def view_contactus():
     return render_template("view_contactus.html")   

if __name__ == '__main__':  
    app.run(debug = True) 