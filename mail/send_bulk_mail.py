
# There are three parts of the interface LOAD,VALIDATE and SEND REGISTRATION LINK

#Global Variable 
project_dir="/home/saibaba/Downloads/blendedpartnerv2/IITBOMBAYX_PARTNERS/"
debug_mode=1
default_password="Welcome123"
member=1
VALID ="Valid"
INVALID="Invalid"
EXISTS="Exists"
CREATED="Created"
SENDMAIL="sendmail"
ERROR="ERROR"
default_end_date="4712-12-31"

import sys,os

sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE']='IITBOMBAYX_PARTNERS.settings'
import csv
import django
django.setup()
from django.db import transaction
from django.db import models
from SIP.models import *
from SIP.validations import *
from SIP.views import *
from django.db import transaction

#Prints on the console
def print_debug(str):
   if debug_mode == 1:
     print str

#Checks the csv file and returns the python list of content
def read_file(csvfile):    
   #Checks whether the csv file can be open or not
   try:   
      reader = csv.reader(open(csvfile,'rb'))
      print_debug("Reading CSV..")
      return reader
   except:
      sys.exit("Cannot open CSV file!")
# End read_file    

def from_file_to_interface(reader,filename):
     csvrecordc=0
     # Defines the current executing section
     #This function gets each row from csv file, validates the format of email, institutename and insert into mail_interface table; in case data is not acceptable, it adds an error into the error_message field
     #Check head record 
     heading = next(reader, None) 
     
     if heading[0]== "RCID" and heading[1]=="InstituteName" and heading[2]=="First Name" and heading[3]=="Last Name" and heading[4] =="Email" and heading[5] == "Designation" and heading[6] == "Role" and heading[7] == "Course" and heading[8] == "Status": 
        pass
        
     else:
          sys.exit("Please upload data in correct template format")
     # Check for user data
     for line in reader:
         
         err_message = ''
         status=VALID
         #First name is mandatory 
         #checks that a first name format is acceptable or not; returns 0 if not 
         if validateFname(line[2]) == 0: 
              err_message += 'First name format not valid!'+'\n'
              status=INVALID 
         #Last name is not mandatory 
         #checks if last name exists and if exists, format is acceptable or not; returns 0 if not
         if len(line[3])>0:    
              if validateLname(line[3]) == 0: 
                   err_message += 'Last name format not valid!'+'\n'
                   status=INVALID 
         
         #checks that a email format is acceptable or not; returns 0 if not
         if validateEmail(line[4]) == 0: 
              err_message += 'Email format not valid!'+'\n'
              status=INVALID 
         
         #checks that a Institutename present into database or not;  returns 0 if not else instituteid
         instituteid=validateInstitute(line[1])
         if (instituteid == 0): 
                err_message += 'Institute name not valid!'+'\n'
                status=INVALID
         #checks that a remotecenterid present into database or not;  returns 0 if not else instituteid
         remotecenterid=validateRemotecenter(line[0])
         if (remotecenterid == 0): 
                err_message += 'rcid  does not exist in remotecenter table!'+'\n'
                status=INVALID  
         
         #checks that a role is valid or not; returns 0 if not   
        
         role_id=validateRole(line[6])
         if role_id == 0: 
               err_message += 'Role is  not valid!'+'\n'
               status=INVALID 
         
         #Head and Program Coordinator should not be assigned to a Course   
         if (line[6] =='Head' or line[6] =='Program Coordinator') and len(line[7]) > 0:
               err_message += line[6]+ " should not have course assigned"+"\n" 
               status=INVALID 
        
         #Teacher should  be assigned to a valid Course
         courseid=validateCourse(line[7])   
         if  line[6] == 'Teacher' and courseid== 0:    
               err_message += 'Course format not valid! '+"\n"
               status=INVALID 
         
         # checking that mail interface table should not duplicate
         if mail_interface.objects.filter(email=line[4],role = line[6],instituteid = instituteid,course = line[7],status =VALID).exists():
               err_message += "Entry for "+ line[4]+"   for  " +line[6]+"  in "+line[1]+"  already exist" +"\n"
               status=INVALID
         else:
               csvrecordc+=1
         
         mail_obj= mail_interface(rcid=line[0],role_id=role_id,courseid=courseid,institutename=line[1],instituteid = instituteid,fname = line[2], lname = line[3], email = line[4], designation=line[5], role = line[6], course = line[7],status=status, error_message = err_message,filename=filename)
         mail_obj.save()
     return csvrecordc
            
     #end for         
#end from_file_to_interface

def createusers(filename):   
    
    #accesing email content for reset password 
   
    encyrypt_pwd = make_password(default_password,salt=None,hasher='pbkdf2_sha256')
    current_date=date.today()
    #Select Valid Records inserted in the file
    for row in mail_interface.objects.filter(status="Valid",filename=filename):
        #ifLoginExists return 1 means  Login exist in user table and ifPersonExists return 1 means  Personinformation has entry of this user
        LoginExist=ifLoginExists(row.email)
        PersonExist=ifPersonExists(row.email)
        
         
        
        if LoginExist == 0 and PersonExist == 0:
            try:           
                person_obj = createsingleuser(row,encyrypt_pwd)
                print "sdgf",person_obj
            except:
                row.message ="User data not getting inserted"
                row.status=ERROR
                row.save()
                continue
            print "aassdfdgdfhd",person_obj
        elif (LoginExist == 0 and PersonExist == 1) or (LoginExist == 1 and PersonExist == 0):
            row.message = "User Data inconsistent in system Error"                   
            row.status=ERROR
            row.save()
            continue 
        else :
            person_obj=Personinformation.objects.get(email=row.email) 
        if row.course:
                print row.email,"ourse"
                CourseEnrollExist=IfCourseEnrolled(row.courseid)
                if CourseEnrollExist==0:
                   print row.email,"ourdfdfdse"
                   edxcourseid= edxcourses.objects.get(id=row.courseid)
                   institute=T10KT_Approvedinstitute.objects.get(instituteid=row.instituteid)
                   courseObj=courseenrollment(courseid=edxcourseid, instituteid=institute, enrollment_date=date.today(), status=1)
                   courseObj.save()

                if Courselevelusers.objects.filter(personid=person_obj,instituteid = row.instituteid,courseid =edxcourses.objects.get(course = row.course),roleid = row.role_id).exists():
                    row.error_message += 'The person already has the same role in the same institute teaching the same course'
                    row.status = EXISTS
                    row.save()
                else:
                    req_obj=createcourseleveluser(edxcourses.objects.get(course = row.course),row.instituteid,T10KT_Remotecenter.objects.get(remotecenterid=row.rcid),row.fname,row.lname,row.email,row.role,row.status,row.designation,person_obj,row.role_id) 
                    row.status = CREATED
                    row.save()
                              
        else: 
                print row.email, "insti"        
                if Institutelevelusers.objects.filter(personid=person_obj,instituteid = row.instituteid,roleid =row.role_id,startdate__lte=current_date,enddate__gt=current_date).exists():
                     row.error_message += 'The person already has the same role in the same institute teaching the same course'
                     row.status = EXISTS
                     row.save()
                else:
                      print row.email,"sdsfdourse"
                      req_obj=createinstituteleveluser(row.instituteid,T10KT_Remotecenter.objects.get(remotecenterid=row.rcid),row.fname,row.lname,row.email,row.role,row.status,row.designation,person_obj, row.role_id)
                      row.status = CREATED
                      row.save()
@transaction.atomic
def createsingleuser(row,encyrypt_pwd):                                         
   login_obj = Userlogin (usertypeid=member,email=row.email,password=encyrypt_pwd) 
   login_obj.save()
   person_obj=createpersoninformation(row.email,row.fname,row.lname,row.designation,row.instituteid)
   return  person_obj
                                     
                
#function to create institutelevel user                
def createinstituteleveluser(instituteid,rcid,fname,lname,email,role,status,designation,person_obj,role_id) : 

    req_obj  = RequestedUsers(state = instituteid.state, instituteid = instituteid, remotecenterid = rcid, firstname = fname, lastname = lname, email = email, roleid = role_id, status = status, createdon = timezone.now(), updatedon = timezone.now(),designation=Lookup.objects.get(category = 'Designation', description = designation).code)
    req_obj.save()

    Institute_level=Institutelevelusers(personid=person_obj,instituteid = instituteid,roleid =role_id,startdate= datetime.now(),enddate=default_end_date)
    Institute_level.save() 
    return req_obj


#function to create courselevel user
def createcourseleveluser(courseid,instituteid,rcid,fname,lname,email,role,status,designation,person_obj,role_id) : 
    req_obj  = RequestedUsers(courseid = courseid,  state = instituteid.state, instituteid = instituteid, remotecenterid =rcid, firstname = fname, lastname = lname, email = email, roleid = role_id, status = status, createdon = timezone.now(), updatedon = timezone.now(),designation=Lookup.objects.get(category = 'Designation', description = designation).code)
    req_obj.save()
    Course_level=Courselevelusers(personid=person_obj,instituteid = instituteid,courseid =courseid,roleid = role_id,startdate= datetime.now(),enddate=default_end_date)
    Course_level.save() 
    return req_obj


# create Personinformation entry
def createpersoninformation(email,fname,lname,designation,instituteid):
    print "am here"
    person_obj=Personinformation(email=email,firstname = fname, instituteid=instituteid,lastname =lname,designation=Lookup.objects.get(category = 'Designation', description = designation).code,createdondate=datetime.now(),telephone1=0)
    print_debug(person_obj) 
    person_obj.save()
    print_debug("after save")
    return person_obj

def emailusers(filename):  
     ec_id = EmailContent.objects.get(systype = 'Login', name = 'createpass').id
     emailsendc=0
     emailnotsendc=0
     for row in mail_interface.objects.filter(status=CREATED,filename=filename):
        person_obj=Personinformation.objects.get(email=row.email)
        req_obj=RequestedUsers.objects.filter(email=row.email,instituteid = row.instituteid,roleid=row.role_id).latest('createdon')
        if req_obj.status == "Valid":
           send_email(ec_id, req_obj.id, person_obj.id)  
           req_obj.status=SENDMAIL
           req_obj.save()
           emailsendc+=1
        else:
           emailnotsendc+=1  
     return (emailsendc, emailnotsendc)

def report(filename,csvrecordc,emailsendc,emailnotsendc):  
     
     validrecordc=0
     invalidrecordc=0
     errorrecordc=0
     rolecreated=0
     personcreated=0
     courselevelc=0
     institutelevelc=0
     for row in mail_interface.objects.filter(filename=filename):
        
        if row.status==VALID:
           validrecordc+=1
        if row.status==INVALID:
           invalidrecordc+=1
        if row.error_message:
           errorrecordc+=1
        if row.status=="Created":
           rolecreated+=1
           personcreated+=1
           if row.courseid==0:
              institutelevelc+=1
           else:
              courselevelc+=1
     print "Total number of records in csv file:" , csvrecordc
     print "Total number of valid records in csv file:", validrecordc
     print "Total number of error records in csv file: ", errorrecordc 

     print "Total number of records selected:" , csvrecordc
     print "Total number of person created:" , personcreated
     print " Total number of roles created:" , rolecreated
     print "Total number of InstituteLevelUsers:" , institutelevelc
     print "Total number of CourseLevelUsers:" , courselevelc
     totalrecinsys=institutelevelc +courselevelc
     print "Total number of records moved to system: ", totalrecinsys
     print "Total number of mails send:" ,     emailsendc
     print "Total number of mails not send:" ,     emailnotsendc      
        
                
def main():
  
   csvfile=sys.argv[1]
   reader=read_file(csvfile)
   csvrecordc=from_file_to_interface(reader,csvfile)
   createusers(csvfile)
   #emailsendc ,emailnotsendc =emailusers(csvfile)
   #report(csvfile,csvrecordc,emailsendc,emailnotsendc)
if __name__ == "__main__":
    main()
   
