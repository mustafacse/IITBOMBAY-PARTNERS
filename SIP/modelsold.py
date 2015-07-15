# VERSION 2.1
# DATED 20 JUNE 2015
# TIME 10:00 AM
# models.py includes all the classes corresponding to database tables
# This file contains foreign key dependency
'''
Change log prepared by PARTH(19/06/2015: 10:30PM)
-renamed table filestatus to student_interface
-removed table studentcourseenrollment as it was a replica of IITBX_studentcourseenrollment
-removed validators in uploadedfiles class
-added columns status, createdon, createdby, updatedon, updatedby in Requestedusers class
-renamed thumbnail to filename in uploadedfiles class
-renamed column lastupdatedon by uploadedon in uploadedfiles class
-corrected foreign key dependencies
-renamed column name with personid  in Responsibility class
-added foreign key arg to verticalid in problemid class
-added foreign key arg to studentid in coursewarestudentmodule
-added foreign key arg to last_updated_by in studentdetails
-added foreign key arg to enrolledby, cancelledby in courseenrollment
-changed loginname to email in userlogin class
-changed loginstatus to status and changed it to booleanfield
-changed createdby, updatedby to foreignkey with Personinformation
-added id column to IITBX_authuser
 '''


#Final Database Modules

from django.db import models
from datetime import datetime,time
from datetime import date
from django.utils import timezone
from time import time
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Error : Extension should be .csv only')
def validate_image_extension(value):
    img=['.jpeg','.png']
    if not value.name.endswith(img):
        raise ValidationError('Error : Extension should be .jpeg or .png only')


def get_upload_file_name(instance,filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.','_'),filename)

def get_upload_image(instance,filename):
	return "static/upload/upload_images/%s" % filename


class T10KT_State(models.Model): # make it T10KT_state
	##stateid = models.IntegerField(primary_key=True)  # AutoField?
	state = models.CharField(unique=True, max_length=255)
	isActive=models.BooleanField(default=1) # Changes here
        
'''
class StudentMoocCity(models.Model):
	id = models.IntegerField(primary_key=True)  # AutoField?
	name = models.CharField(max_length=255)
	state = models.ForeignKey('State')
	class Meta:
              managed = True
'''
              
# Configuration tables interfaced from IITB-NMEICT T10KT website

#Start

class T10KT_Institute(models.Model):
     instituteid=models.IntegerField(primary_key=True)
     institutename=models.CharField(max_length=100,null=False)
     state=models.CharField(max_length=50)
     city=models.CharField(max_length=100)
     pincode=models.IntegerField(null=True) # null is true because in csv many rows have null pincode
     address=models.CharField(max_length=250,null=True) # null is true because in csv many rows have null address
	
    
           
class T10KT_Remotecenter(models.Model):
	remotecenterid=models.IntegerField(primary_key=True)
	remotecentername=models.CharField(max_length=100,null=False)
	state=models.CharField(max_length=50)
	city=models.CharField(max_length=100)
	instituteid=models.ForeignKey(T10KT_Institute) #changes made here
	autonomous=models.BooleanField(default=1)
              

class T10KT_Approvedinstitute(models.Model):
	remotecenterid=models.ForeignKey(T10KT_Remotecenter,null=True)
	instituteid=models.ForeignKey(T10KT_Institute,null=True, unique=True)
	heademail=models.EmailField(max_length=100,null=False)

class Lookup(models.Model): # remove T10KT , make it just Lookup 
	category=models.CharField(max_length=75,null=False)
	code=models.IntegerField(null=False)
	description=models.CharField(max_length=100, null=False)
	comment=models.CharField(max_length=100,null=True)
	is_active = models.BooleanField(default=1)

	#def __unicode__(self):
		#return "%s" %(self.code)           
# End 




# Coursemanagement 
# to be imported from mitali also course grade criteria table and course grade policy

class Personinformation(models.Model):
    GENDER_CHOICES = ( 
     ('MALE', 'Male'),
     ('FEMALE', 'Female'),
	)
    email=models.EmailField(max_length=100,null=False)
    titleid=models.IntegerField(null=True)
    firstname=models.CharField(max_length=45,null=True)
    lastname=models.CharField(max_length=45,null=True)
    designation=models.IntegerField(null=True)
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES, default = 'MALE')
    streamid=models.IntegerField(null=True)
    #instituteid=models.ForeignKey(T10KT_Institute)    #can be modified later 'do not remove'
    experience=models.CharField(max_length=45,null=True)
    qualification=models.CharField(max_length=45,null=True)
    telephone1=models.CharField(null=False, max_length=12, default=0)
    telephone2=models.CharField(default=0, max_length=12, null=True)
    createdondate=models.DateField(default=date.today(),null=False)
    #createdby=models.IntegerField(default=0,null=False)
    isactive=models.BooleanField(default=1) #added this to know whether the person is currently attached with the system    
    
    
class IITBX_authuser(models.Model):
    id=models.IntegerField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    firstname = models.CharField(max_length=30,null=True)
    lastname = models.CharField(max_length=30,null=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    is_superuser = models.BooleanField()
    last_login = models.DateTimeField(default=datetime.now())
    datejoined = models.DateTimeField()



class edxcourses(models.Model):   
    tag =  models.CharField(max_length=100,null=True)
    org =  models.CharField(max_length=100,null=True)
    course =  models.CharField(max_length=100,null=True)
    year =  models.CharField(max_length=100,null=True)
    courseid =  models.CharField(max_length=100,null=True, unique=True)
    coursename=models.CharField(max_length=100, null=True)
    enrollstart =  models.DateTimeField(null=True)
    enrollend =  models.DateTimeField(null=True)
    coursestart =  models.DateTimeField(null=True)
    courseend =  models.DateTimeField(null=True)
    image=models.ImageField(upload_to=get_upload_image)
    instructor=models.CharField(max_length=50)
    coursesubtitle=models.TextField()
    

class courseenrollment(models.Model):
	courseid =  models.ForeignKey(edxcourses, to_field='courseid')  #foreign key with edxcourses
	instituteid=models.ForeignKey(T10KT_Approvedinstitute, to_field='instituteid')  #foreign key with T10KT_Approvedinstitute.instituteid
	corresponding_course_name=models.CharField(max_length=100)
	start_date=models.DateField(default=date.today())
	end_date=models.DateField(4712-12-31)
	year=models.IntegerField()
	program=models.CharField(max_length=50)
	total_moocs_students=models.IntegerField()
	total_course_students=models.IntegerField()
	enrollment_date=models.DateField(default=date.today())
	enrolledby=models.ForeignKey(Personinformation, related_name='courseenid')
	comments=models.TextField(null=True)
	cancelled_date=models.DateField(null=True)
	cancelledby=models.ForeignKey(Personinformation, related_name='coordinatorid',null=True)
	reason_of_cancellation=models.TextField(null=True)
	status=models.BooleanField(default=0)

class gradepolicy(models.Model):
	courseid =  models.ForeignKey(edxcourses, to_field='courseid')  #foreign key with edxcourses
   	min_count=models.IntegerField(null=True)
    	weight=models.FloatField(null=True)
    	type=models.CharField(max_length=100,null=True)
    	drop_count=models.IntegerField(null=True)
    	short_label=models.CharField(max_length=10,null=True)

class gradescriteria(models.Model):
    	courseid =  models.ForeignKey(edxcourses, to_field='courseid')  #foreign key with edxcourses
    	grade=models.CharField(max_length=5,null=True)
    	cutoffs=models.FloatField(null=True)
    
class verticalid(models.Model):#
    courseid =  models.ForeignKey(edxcourses, to_field='courseid')
    verticalid =  models.CharField(max_length=255,null=True, unique=True)
    display_name =  models.CharField(max_length=255,null=True)

class problemid(models.Model):#
    verticalid=  models.ForeignKey(verticalid,to_field='verticalid')    #foreign key with verticalid
    problemid=  models.CharField(max_length=100,null=True)
    verticalname=  models.CharField(max_length=255,null=True)
    problemname=  models.CharField(max_length=255,null=True)
    
class coursewarestudentmodule(models.Model):#
    id=models.IntegerField(primary_key=True)
    moduletype =  models.CharField(max_length=32,null=True)
    moduleid =  models.CharField(max_length=255,null=True)
    studentid =  models.ForeignKey(IITBX_authuser)  #foreign key with IITBX_authuser
    grade =  models.FloatField(default=0)
    state =  models.CharField(max_length=255,null=True)    
    created =  models.DateTimeField()
    modified =  models.DateTimeField()
    max_grade =  models.CharField(max_length=20,null=True)
    done =  models.CharField(max_length=8,null=True)
    courseid =  models.ForeignKey(edxcourses, to_field='courseid')
        
        
# End Of coursemanagement	
        




#Registration module tables

              
      
class Responsibility(models.Model):#personid
    '''ROLE_PERMISSIONS = ( 
        ('Y', 'Yes'),
        ('N', 'No'),
    )'''
    #systype=models.CharField(max_length=30)
    personid=models.ForeignKey(Personinformation); #foreign key with personinformation table
    #hoi=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
    #pc=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
    #cc=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
    #ta=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
    admin=models.BooleanField(default=0)
    hoi = models.BooleanField(default=0)
    pc = models.BooleanField(default=0)
    cc=models.BooleanField(default=0)
    ta=models.BooleanField(default=0)
    comments=models.TextField(null=True)
 
class Userlogin(models.Model):
    #loginname=models.CharField(max_length=75,null=True)
    email=models.CharField(max_length=75,null=False)
    password=models.CharField(max_length=75,null=False)
    usertypeid=models.IntegerField(default=1)
    status=models.BooleanField(default=0)
    last_login=models.DateTimeField(default=datetime.now(),null=False)
    nooflogins=models.IntegerField(null=True,default=0)

class Institutelevelusers(models.Model):
    personid=models.ForeignKey(Personinformation)
    instituteid=models.ForeignKey(T10KT_Institute)
    #roleid=models.ForeignKey(Responsibility)
    roleid=models.IntegerField()
    startdate=models.DateField(default=date.today(),null=False)
    enddate=models.DateField(4712-12-31)           #Give a fix date 31/Dec/4712
        
	      
class Courselevelusers(models.Model):
    #personid=models.ForeignKey(Personinformation, unique=True) # remove unique from here
    personid=models.ForeignKey(Personinformation)
    instituteid=models.ForeignKey(T10KT_Institute) 
    #courseid=models.CharField(max_length=75,null=False)   
    courseid=models.ForeignKey(edxcourses)
    #roleid=models.ForeignKey(Responsibility)
    roleid=models.IntegerField()
    startdate=models.DateField(default=date.today(),null=False)
    enddate=models.DateField(4712-12-31)     #Give a fix date 31/Dec/4712
        


# End Of Registration
	
	
	


# Upload students


class IITBX_studentcourseenrollment(models.Model):
    userid = models.ForeignKey(IITBX_authuser)   #foreign key with IITBX_authuser
    courseid =  models.ForeignKey(edxcourses, to_field='courseid')   #foreign key with edxcourses
    createdon =  models.DateField(default=date.today())
    is_active =  models.BooleanField(default=1)
    mode =  models.CharField(max_length=100,null=True)     


class studentDetails(models.Model):
	userid = models.ForeignKey(IITBX_authuser)	              
	courseid = models.ForeignKey(edxcourses, to_field='courseid')
	teacherid = models.ForeignKey(Personinformation,related_name='teacherid')# replaced Courseleveluser with Personinformation
	roll_no = models.CharField(max_length=30,default="0")
	last_update_on = models.DateField(default=date.today())
	last_updated_by = models.ForeignKey(Personinformation, related_name='updaterid') # replaced Courseleveluser with Personinformation

class uploadedfiles(models.Model):
	filename = models.FileField(upload_to=get_upload_file_name, null=True)
	is_read = models.BooleanField(default = 0)
	errorocccur = models.BooleanField(default=0)
	uploadedby = models.ForeignKey(Personinformation,default=1)  # replaced Courseleveluser with Personinformation
	uploadedon = models.DateField(default=date.today())


# End Students

# System Table




class PageContent(models.Model):
	systype=models.CharField(max_length=30)
	name=models.CharField(max_length=100)
	html_text=models.TextField()

class EmailContent(models.Model):
	systype=models.CharField(max_length=30)
	name=models.CharField(max_length=100)
	subject=models.CharField(max_length=100)
	message=models.TextField()


class ErrorContent(models.Model):
	systype=models.CharField(max_length=30)
	name=models.CharField(max_length=100)
	errorcode=models.CharField(max_length=20, unique=True, default='null')
	error_message=models.TextField()


class student_interface(models.Model):
	fileid = models.ForeignKey(uploadedfiles)  #foreign key with uploadedfiles
	recordno = models.IntegerField()
	roll_no = models.CharField(max_length = 20)
	username = models.CharField(max_length = 20, null=True)
	email = models.EmailField(null=True)
	errorcode = models.ForeignKey(ErrorContent,to_field='errorcode')  #foreign key with ErrorContent
 
class RequestedUsers(models.Model):
    courseid = models.ForeignKey(edxcourses,null=True)
    state = models.CharField(max_length=255)
    instituteid = models.ForeignKey(T10KT_Institute)
    remotecenterid = models.ForeignKey(T10KT_Remotecenter)
    firstname=models.CharField(max_length=45,null=True)
    lastname=models.CharField(max_length=45,null=True)	
    email=models.EmailField(max_length=100,null=False)
    #roleid=models.ForeignKey(Responsibility)
    roleid=models.IntegerField()
    designation=models.IntegerField(null=True)
    status=models.CharField(max_length=50)
    createdon=models.DateTimeField(0001-01-01) 
    createdby=models.ForeignKey(Personinformation, related_name='user',null=True)
    updatedon=models.DateTimeField() 
    updatedby=models.ForeignKey(Personinformation, related_name='higherauthority',null=True)
    
    
#end of System table      
#  performance table
class performance_interface(models.Model):
	courseid = models.CharField(max_length=100)
	userid = models.IntegerField()
	email = models.EmailField()
	username = models.CharField(max_length=15)
	grade = models.CharField(max_length=2, null=True)
	quiz1 = models.IntegerField(null=True)
	quiz2 = models.IntegerField(null=True)
	quiz3 = models.IntegerField(null=True)
	quiz4 = models.IntegerField(null=True)
	quiz5 = models.IntegerField(null=True)
	quiz6 = models.IntegerField(null=True)
	quiz7 = models.IntegerField(null=True)
	quiz8 = models.IntegerField(null=True)
	quiz9 = models.IntegerField(null=True)
	quiz10 = models.IntegerField(null=True)

class Reports(models.Model):
	reportid=models.CharField(max_length=20,primary_key=True)
	usertype=models.IntegerField()
	sqlquery=models.CharField(max_length=200)
	report_title=models.CharField(max_length=100)
	comments=models.CharField(max_length=200)

class mail_interface(models.Model):
    fname = models.CharField(max_length=75)
    lname = models.CharField(max_length=75)
    email = models.EmailField()
    instituteid = models.ForeignKey(T10KT_Institute)
    role = models.CharField(max_length=30)
    course = models.CharField(max_length = 50, null = True)
    error_message = models.CharField(max_length = 300, null = True)
