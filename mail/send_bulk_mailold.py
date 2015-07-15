# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 01:07:28 2015

@author: parth
"""
project_dir="/home/edx/blendedpartnerv2/IITBOMBAYX_PARTNERS/"

import sys,os
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE']='IITBOMBAYX_PARTNERS.settings'
import csv
import django
django.setup()
from django.db import models
from SIP.models import *
from SIP.validations import *
    
#Checks whether the csv file can be open or not
try:   
    reader = csv.reader(open(sys.argv[1],'rb'))
    print "Reading CSV.."
except:
    print "Cannot open CSV file!"




#reads csv file line by line and simultaneosly checks for valid email 
'''

    line[0] = firstname
    line[1] = lastname
    line[2] = email
    line[3] = institutename
    line[4] = role
    line[5] = course
    
# id, firstname, lastname, email, institutename, role, course



class mail_interface(models.Model):
    fname = models.CharField(max_length=75)
    lname = models.CharField(max_length=75)
    email = models.EmailFiled()
    instituteid = models.ForeignKey(T10KT_Institute)
    role = models.CharField(max_length=30)
    course = models.CharField(max_length = 50, null = True)
    error_message = models.CharField(max_length= 300)    
    
    
def validateInstitute(institutename):
    if T10KT_Institute.objects.get(institutename = instututename)::
        return 1
    return 0
    
def validateFirstname(fname):
    if len(fname) > 1:
        if re.match("^[A-Z][a-zA-Z]+$", email) != None:
            return 1
    return 0

'''
# There are three parts ofthe interface LOAD,VALIDATE and SEND REGISTRATION LINK
section = 1 # Definesthe current executing section

'''
This function gets each row from csv file, validates the format of email, institutename and insert into mail_interface table; in case data is not acceptable, it adds an error into the error_message field
'''
for line in reader:
    if line:
       try:
            print line,"line"
            error = ''
            if validateFname(line[0]) == 0: #checks that a first name format is acceptable or not; returns 0 if not
                error += 'First name format not valid!, '
            if len(line[1])>0:    
                    if validateLname(line[1]) == 0: #checks that a last name format is acceptable or not; returns 0 if not
                           error += 'Last name format not valid!, '
            if validateEmail(line[2]) == 0: #checks that a email format is acceptable or not; returns 0 if not
                error += 'Email format not valid!, '
            if validateInstitute(line[3] == 0): #checks that a Institutename present into database or not;  returns 0 if not
                error += 'Institute name not valid!, '
            if validateRole(line[4]) == 0: #checks that a role is acceptable or not; returns 0 if not
                error += 'Role is  not valid!, '
            if line[4] =='Course Coordinator' or line[4] == 'Teacher':    
                    if validateCourse(line[5]) == 0: #checks that course exists; returns 0 if not
                          error += 'Email format not valid!, '
            instituteid_id= T10KT_Institute.objects.get(institutename = line[3])
            print instituteid_id
            mail_obj= mail_interface(fname = line[0], lname = line[1], email = line[2], instituteid= T10KT_Institute.objects.get(institutename = line[3]), role = line[4], error_message = error)        
            mail_obj.save()
            section = 2
       except:
            print "some error occured while inserting data to mail_interface table"
'''
  This function gets each entry from mail_interface table and does the following:
  1) if the role is HOI, it inserts the heademail into the appropriate column of Approvedinstitute table
  2) else,it inserts a new row for each entry in the RequestedUsers table
'''


if section == 2:   
        #try:
        print "Successful loading data into database"
        for row in mail_interface.objects.all():
            if row.role == 'Head of Institute':    #Save data to Approvedinstitute if the person is HOI
                appins_obj = T10KT_Approvedinstitute.objects.get(instituteid = row.instituteid)
                if appins_obj.instituteid != '':
                    row.error_message += 'Institute already has a Head of Institute'
                    row.save()
                else:
                    print "setting headmail"
                    appins_obj.heademail = row.email
                    appins_obj.save()
                    print "done"
                    ec_id = emailContent.objects.get(systype = 'TM_MGMT_PC', name = 'register').id
                    mail_obj = emailContent.objects.filter(id=ec_id)
                    link = ROOT_URL + '/' +mail_obj[0].name + '/%d/1' %appins_obj.id 
                    message = mail_obj[0].message %(row.fname, row.role, link)
                    send_mail(mail_obj[0].subject, message , EMAIL_HOST_USER ,[row.email], fail_silently=False)    
            elif row.role == 'Program Coordinator':   #Save data to RequestedUsers if the person is PC
                status = 'Valid'
                if validatePC(row.email, Lookup.objects.get(category = 'role', comment = row.role).code) == 0 :
                    row.error_message += 'The person already has the same role in the same institute'
                    row.save()
                    status = 'Invalid'
                obj = RequestedUsers(state = row.instituteid.state, instituteid = row.instituteid, remotecenterid = T10KT_Remotecenter.objects.get(instituteid = row.instituteid), firstname = row.fname, lastname = row.lname, email = row.email, roleid = Lookup.objects.get(category = 'role', comment = row.role).code, status = status, createdon = timezone.now(), updatedon = datetime.now())
                obj.save()
            else :  #Save data to RequestedUsers if the person is CC/TA
		status = 'Valid'
                if validateUser(row.email, Lookup.objects.get(category = 'role', comment = row.role).code, course = edxcourses.objects.get(course = row.course)) == 0 :
		    print "in cc/TA"
                    row.error_messaage += 'The person already has the same role in the same institute teaching the same course'
                    row.save()
                    status = 'Invalid'
                obj  = RequestedUsers(courseid = edxcourses.objects.get(course = row.course),  state = row.instituteid.state, instituteid = row.instituteid, remotecenterid = T10KT_Remotecenter.objects.get(instituteid = row.instituteid), firstname = row.fname, lastname = row.lname, email = row.email, roleid = Lookup.objects.get(category = 'role', comment = row.role).code, status = status, createdon = timezone.now(), updatedon = timezone.now())
                obj.save()
        section = 3
    #except:
        #print 'Some error occured while parsing data from mail_interface table'
        
'''
This function gets each entry from RequestedUsers table and send email to PC/CC/TA only when status is Valid and changes it to invited
'''

if section == 3:
    #try:
        print 'Starting to send email'
        for row in RequestedUsers.objects.all():
            if row.status == 'Valid':
                if row.roleid == Lookup.objects.get(category = 'Role', comment='Program Coordinator').code:
                    ec_id = EmailContent.objects.get(systype = 'TM_MGMT_PC', name = 'register').id
                else :
                    ec_id = EmailContent.objects.get(systype = 'TM_MGMT_C', name = 'register').id
                send_email(ec_id, row.id, row.id)
                row.status = 'Invited'
                row.save()
                print 'Email send successfully to ',row.email    
    #except:
        #print 'Some error occured while sending email'      
