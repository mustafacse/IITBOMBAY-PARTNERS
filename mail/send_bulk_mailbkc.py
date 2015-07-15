# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 01:07:28 2015

@author: parth
"""
project_dir="/home/edx/blendedpartnerv2/IITBOMBAYX_PARTNERS"

import sys,os
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE']='IITBOMBAYX_PARTNERS.settings'

import csv
import django
django.setup()
from django.db import models
from SIP.models import *
from SIP.validations import *
from SIP.views import *

    
#Checks whether the csv file can be open or not
try:   
    reader = csv.reader(open(sys.argv[1],'rb'))
    print "Reading CSV.."
except:
    print "Cannot open CSV file!"




#reads csv file line by line and simultaneosly checks for valid email 

# There are three parts ofthe interface LOAD,VALIDATE and SEND REGISTRATION LINK
section = 1 # Definesthe current executing section


#This function gets each row from csv file, validates the format of email, institutename and insert into mail_interface table; in case data is not acceptable, it adds an error into the error_message field

for line in reader:
    if line:
       if line[0]!="RCID":
       # try: 
            error = ''
            if validateFname(line[2]) == 0: #checks that a first name format is acceptable or not; returns 0 if not
                error += 'First name format not valid!, '
            if len(line[3])>0:    
                    if validateLname(line[3]) == 0: #checks that a last name format is acceptable or not; returns 0 if not
                           error += 'Last name format not valid!, '
            if validateEmail(line[4]) == 0: #checks that a email format is acceptable or not; returns 0 if not
                error += 'Email format not valid!, '
            if validateInstitute(line[1] == 0): #checks that a Institutename present into database or not;  returns 0 if not
                error += 'Institute name not valid!, '
            if validateRole(line[6]) == 0: #checks that a role is acceptable or not; returns 0 if not
                error += 'Role is  not valid!, '
            if  line[6] == 'Teacher':    
                    if validateCourse(line[7]) == 0: #checks that course exists; returns 0 if not
                          error += 'Course format not valid!, '
            if (line[6] =='Head' or line[6] =='Program Coordinator') and len(line[7]) > 0:
                    print type(line[6])
                    error += line[6]+ "   should not have course assigned" 
            # checking that mail interface table should not repeat entry 
            if mail_interface.objects.filter(email=line[4],role = line[6],instituteid = T10KT_Institute.objects.get(institutename = line[1]),course = line[7]).exists():
               print "Entry for "+ line[4]+"   for  " +line[6]+"  in "+line[1]+"  already exist" 
               
            else:             
                 mail_obj= mail_interface(instituteid = T10KT_Institute.objects.get(institutename = line[1]),fname = line[2], lname = line[3], email = line[4], designation=line[5], role = line[6], course = line[7], error_message = error)
            
                 if len(error)==0:
                    mail_obj.status="Valid"
                    section = 2
                 else:
                    mail_obj.status="Invalid"
                 mail_obj.save()       


if section == 2:   
   
        #accesing email content for reset password 
        ec_id = EmailContent.objects.get(systype = 'Login', name = 'resetpass').id
        for row in mail_interface.objects.filter(status='Valid'):
            #Validate credential return 1 means  credential exist in user table
                if Validatecredential(row.email)==1:
                   print "Credential allready present"
            #Validatecredential =0 means  create credential  in user table
                else :
                    pwd1 = make_password("user123",salt=None,hasher='pbkdf2_sha256')
                    login_obj = Userlogin (usertypeid=1,email=row.email,password=pwd1) # 1 means IITBOMBAYX Partner system
                    login_obj.save()
            
		status = 'Valid'

                # validateUser checks  if user is present in personinformation,courseleveluser or instituteleveluser table 
                # return 0  if user entry is present in personinformation and courseleveluser or instituteleveluser table.
                if validateUser(row.email, Lookup.objects.get(category = 'role', comment = row.role).code, row.course,row.instituteid.instituteid) == 0 :
		    row.error_message += 'The person already has the same role in the same institute teaching the same course'
                    row.save()
                    status = 'Invalid'
                    continue

                #  return 2 if user entry is not even present in personinformation and courseleveluser or instituteleveluser table.
                elif validateUser(row.email, Lookup.objects.get(category = 'role', comment = row.role).code,row.course,row.instituteid.instituteid) ==2 :#
                     pers_obj=Personinformation(email=row.email,firstname = row.fname, lastname = row.lname,designation=Lookup.objects.get(category = 'Designation', description = row.designation).code,createdondate=datetime.now(),telephone1=0)
                     pers_obj.save()

                #  return 1 if user entry is  present in personinformation but not in  courseleveluser or instituteleveluser table.    
                
                per_obj = Personinformation.objects.get(email =row.email)  

                # checking if course is present in mail_interface table then entry will be created in courselevel (for teacher or course coordinator)                
                if row.course:
                    print row.email,"mila kya",bool(row.course)
                    req_obj  = RequestedUsers(courseid = edxcourses.objects.get(course = row.course),  state = row.instituteid.state, instituteid = row.instituteid, remotecenterid = T10KT_Remotecenter.objects.get(instituteid = row.instituteid), firstname = row.fname, lastname = row.lname, email = row.email, roleid = Lookup.objects.get(category = 'role', comment = row.role).code, status = status, createdon = timezone.now(), updatedon = timezone.now(),designation=Lookup.objects.get(category = 'Designation', description = row.designation).code)
                    req_obj.save()
                    Course_level=Courselevelusers(personid=per_obj,instituteid = row.instituteid,courseid =edxcourses.objects.get(course = row.course),roleid = Lookup.objects.get(category = 'role', comment = row.role).code,startdate= datetime.now(),enddate="4712-12-31")
                    Course_level.save() 

                # else store in institute level user
                else:
                     req_obj  = RequestedUsers(state = row.instituteid.state, instituteid = row.instituteid, remotecenterid = T10KT_Remotecenter.objects.get(instituteid = row.instituteid), firstname = row.fname, lastname = row.lname, email = row.email, roleid = Lookup.objects.get(category = 'role', comment = row.role).code, status = status, createdon = timezone.now(), updatedon = timezone.now(),designation=Lookup.objects.get(category = 'Designation', description = row.designation).code)
                     req_obj.save()
                     Institute_level=Institutelevelusers(personid=per_obj,instituteid = row.instituteid,roleid = Lookup.objects.get(category = 'role', comment = row.role).code,startdate= datetime.now(),enddate="4712-12-31")
                     Institute_level.save()

                # sending mail to reset password for each automated created login 
                
                send_email(ec_id, req_obj.id, per_obj.id)
                row.status = 'Invited'
                row.save()
                print 'Email send successfully to ',row.email
    
