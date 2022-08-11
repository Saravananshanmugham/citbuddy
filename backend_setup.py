import sqlite3  
  
con = sqlite3.connect("IR40.db")  
cur = con.cursor() 

print("Database opened successfully...\n")  
create_table = """ create table if not exists Credentials (
    emailid TEXT PRIMARY KEY,
    Id_no INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Passwd TEXT NOT NULL,
    Dept integer NOT NULL,
    usergrp TEXT NO NULL
)
"""
con.execute(create_table)  
print("Table Credentials created successfully...")  

create_table = """ create table if not exists Deptnews (
    pid integer primary key AUTOINCREMENT,
    Newstext TEXT,
    url TEXT,
    status TEXT default 'A'

)
"""
con.execute(create_table)  
print("Table Department News created successfully...")  

create_table = """ create table if not exists Clubnews (
    pid integer primary key AUTOINCREMENT,
    Newstext TEXT,
    url TEXT,
    status TEXT default 'A'

)
"""
con.execute(create_table)  
print("Table Club News created successfully...")  

create_table= """create table if not exists attendance_data (
    pid integer primary key,
    exceldata TEXT,
    dbupdate TEXT default 'N'
    )
    """
con.execute(create_table)  
print("Table attendance_data created successfully...")  

create_table= """create table if not exists Course_data (
    pid integer primary key,
    exceldata TEXT,
    dbupdate TEXT default 'N'
    )
    """
con.execute(create_table)  
print("Table Course_data created successfully...")  


create_table= """create table if not exists assignments (
    pid integer primary key AUTOINCREMENT,
    assign_file TEXT,
    upload_date TEXT  DEFAULT (CURRENT_DATE),
    due_date TEXT DEFAULT (CURRENT_DATE)
    )
    """
con.execute(create_table)  
print("Table assignments created successfully...")  


create_table= """create table if not exists Course_Master (
    Pid integer primary key AUTOINCREMENT,
    Dept_id interger not null,
    Semester integer not null,
    Subject_Code TEXT Not null,
    Faculty_id integer not null,
    Course_Credit integer not null,
    Course_Duration interger not null
    )
    """
con.execute(create_table)  
print("Table Course_Master created successfully...")  

create_table= """create table if not exists Attendance_Master (
    Pid integer primary key AUTOINCREMENT,
    Dept_id interger not null,
    Semester integer not null,
    Subject_Code TEXT Not null,
    Faculty_id integer not null,
    Student_Code integer not null,
    Attendance_Date TEXT not null,
    Present_hours interger not null,
    Absent_hours interger not null
    )
    """
con.execute(create_table)  
print("Table Attendance_Master created successfully...")  


insert_query = """
INSERT into Credentials (emailid,Id_no,Name,Passwd,Dept,usergrp)
values (?,?,?,?,?,?)"""
cur.execute(insert_query, ('71762108018@cit.edu.in',71762108018, 'Karthick Srinivas S', 'Karthick@09',1,'A'))
cur.execute(insert_query, ('71762108019@cit.edu.in',71762108019, 'Bala Satvik', 'Bala@09',1,'A'))
cur.execute(insert_query, ('superuser@cit.edu.in',  99999999999, 'Super User', 'Super',99,'Z'))
con.commit()
print("Admin Users Created Successfully...")  


con.close()  