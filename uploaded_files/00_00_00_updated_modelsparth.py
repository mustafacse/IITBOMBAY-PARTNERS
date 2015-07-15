### CHANGES MENTIONED AT THE BOTTOM

#Final Database Modules

from django.db import models
from datetime import datetime 
from datetime import date
from time import time
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Error : Extension should be .csv only')

def get_upload_file_name(instance,filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.','_'),filename)


class State(models.Model):
	stateid = models.IntegerField(primary_key=True)  # AutoField?
	name = models.CharField(unique=True, max_length=255)
        class Meta:
             managed = True
             
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
	institutename=models.CharField(max_length=100,null=True)
	stateid=models.ForeignKey(State) 
	city=models.CharField(max_length=100)
	pincode=models.IntegerField(null=True)
	address=models.CharField(max_length=250,null=True)
	#accredition=models.IntegerField(max_length=11,null=True)
	#type=models.CharField(max_length=45,null=True)
	#officephone=models.CharField(max_length=40,null=True)
	#isActive=models.IntegerField(max_length=1,null=True)
	#lastupdate=models.DateTimeField(null=False)
	#lastupdateby=models.IntegerField(max_length=11,null=True)
        
        class Meta:
              managed = True
        
              
class T10KT_Remotecenter(models.Model):
	remotecenterid=models.IntegerField(null=False,primary_key=True)
	remotecentername=models.CharField(max_length=100,null=True)
	stateid=models.ForeignKey(State) 
	city=models.CharField(max_length=100)
	instituteid=models.ForeignKey(T10KT_Institute) 
	autonomous=models.CharField(max_length=3,null=True)
	#district=models.CharField(max_length=45,null=True)
	#active=models.IntegerField(max_length=11,null=False)
	#rating=models.IntegerField(max_length=11,null=False)
	#Instituteid=models.IntegerField(max_length=11,null=False)
	#email=models.EmailField(max_length=100,null=False)
	#status=models.CharField(max_length=10,null=False)
	#lastupdatedby=models.CharField(max_length=20,null=False)
	#lastupdate=models.DateTimeField(null=False)
	#acdcalstartdate=models.TextField()
	#affiliateduniversity=models.CharField(max_length=200,null=True)
        class Meta:
              managed = True
              

class T10KT_Approvedinstitute(models.Model):
	remotecenterid=models.ForeignKey(T10KT_Remotecenter) 
	instituteid=models.ForeignKey(T10KT_Institute, unique=True) 
	heademail=models.EmailField(max_length=100,null=False)
        class Meta:
              managed = True

class Lookup(models.Model):
	category=models.CharField(max_length=75,null=True)
	code=models.IntegerField(null=True)
	description=models.CharField(max_length=100, null=True)
	comment=models.CharField(max_length=100,null=True)
 	is_active = models.BooleanField(default=False)

	def __unicode__(self):
		return "%s" %(self.description)


# End 

	
	

# Coursemanagement 
# to be imported from mitali also course grade criteria table and course grade policy

class edxcourses(models.Model):
	courseid = models.CharField(max_length=25, primary_key=True)
	coursename=models.CharField(max_length=50)
	coursesubtitle=models.TextField()
	instructor=models.CharField(max_length=30)
	imagename=models.CharField(max_length=50)
	org=models.CharField(max_length=50)
	start_date=models.DateField(default=date.today())
	end_date=models.DateField(4712-12-31)                                        # Give a fix date 31/Dec/4712
	

class courseenrollment(models.Model):
	courseid =  models.ForeignKey(edxcourses) 
	instituteid=models.ForeignKey(T10KT_Approvedinstitute, to_field='instituteid')
	corresponding_course_name=models.CharField(max_length=100)
	start_date=models.DateField(default=date.today())
	end_date=models.DateField(4712-12-31)
	year=models.IntegerField()
	program=models.CharField(max_length=10)
	total_moocs_students=models.IntegerField()
	total_course_students=models.IntegerField()
	enrollment_date=models.DateField(default=date.today())
	enrolledby=models.CharField(max_length=30)
	comments=models.TextField()
	cancelled_date=models.DateField(null=True)
	cancelledby=models.CharField(max_length=30)
	reason_of_cancelation=models.TextField()
	status=models.IntegerField(default=0)

class gradepolicy(models.Model):
	courseid= models.ForeignKey(edxcourses) 
   	min_count=models.IntegerField()
    	weigth=models.FloatField()
    	type=models.CharField(max_length=100)
    	drop_count=models.IntegerField()
    	short_label=models.CharField(max_length=10)

class gradescriteria(models.Model):
    	courseid= models.ForeignKey(edxcourses) 
    	grade=models.CharField(max_length=5)
    	cutoffs=models.FloatField()

# End Of coursemanagement	      
	
#Registration modle tables

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
	instituteid=models.ForeignKey(T10KT_Approvedinstitute, to_field='instituteid')
	experience=models.CharField(max_length=45,null=True)
	qualification=models.CharField(max_length=45,null=True)
	telephone1=models.IntegerField(null=True)
	telephone2=models.IntegerField(null=True)
	createdondate=models.DateField(default=date.today(),null=False)
	createdby=models.IntegerField(default=0,null=False)
        class Meta:
              managed = True
              
      
class Userlogin(models.Model):
	loginname=models.CharField(max_length=75,null=True)
	password=models.CharField(max_length=75,null=True)
	usertypeid=models.IntegerField(default=1,null=True)
	loginstatus=models.CharField(max_length=75,null=False)
	last_login=models.DateTimeField(default=datetime.now(),null=False)
	nooflogins=models.IntegerField(null=True,default=0)
        class Meta:
              managed = True
              


class Institutelevelusers(models.Model):
	personid=models.ForeignKey(Personinformation)
	instituteid=models.ForeignKey(T10KT_Approvedinstitute, to_field='instituteid')
	roleid=models.IntegerField()
	startdate=models.DateField(default=date.today(),null=False)
	enddate=models.DateField(4712-12-31)           # Give a fix date 31/Dec/4712
        class Meta:
              managed = True
	      
class Courselevelusers(models.Model):
	personid=models.ForeignKey(Personinformation)
	instituteid=models.ForeignKey(T10KT_Approvedinstitute, to_field='instituteid')
	courseid=models.CharField(max_length=75,null=False)   
	roleid=models.IntegerField()
	startdate=models.DateField(default=date.today(),null=False)
	enddate=models.DateField(4712-12-31)     # Give a fix date 31/Dec/4712
        class Meta:
              managed = True

# End Of Registration

# Upload students

class IITBX_authuser(models.Model):
	username = models.CharField(max_length=30, unique=True)
	firstname = models.CharField(max_length=30)
	lastname = models.CharField(max_length=30)
	email = models.EmailField()
	password = models.CharField(max_length=128)
	is_staff = models.BooleanField()
	is_active = models.BooleanField()
	is_superuser = models.BooleanField()
	last_login = models.DateTimeField()
	datejoined = models.DateTimeField()

class IITBX_studentcourseenrollment(models.Model):
	userid = models.ForeignKey(IITBX_authuser)
	courseid = models.ForeignKey(edxcourses)
	created = models.DateTimeField()
	is_active = models.BooleanField()
	mode = models.CharField(max_length=100)

class studentDetails(models.Model):
	userid = models.ForeignKey(IITBX_authuser)	              
	courseid = models.ForeignKey(edxcourses)
	teacherid = models.ForeignKey(Courselevelusers,default=0, related_name='teacher')
	roll_no = models.CharField(max_length=30,default="0")
	last_update_on = models.DateField(null=True)
	last_updated_by = models.ForeignKey(Courselevelusers, related_name='person')

class uploadedfiles(models.Model):
	thumbnail = models.FileField(upload_to=get_upload_file_name,validators=[validate_file_extension], null=True)
	is_read = models.BooleanField(default = 0)
	errorocccur = models.BooleanField(default=0)
	uploadedby = models.ForeignKey(Courselevelusers)
	lastupdatedon = models.DateField(null=True)



# End Students

# System Table

class Responsibility(models.Model):
	ROLE_PERMISSIONS = ( 
        ('Y', 'Yes'),
        ('N', 'No'),
	)
	systype=models.CharField(max_length=30)
	name=models.CharField(max_length=100)
	hoi=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
	pc=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
	cc=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
	ta=models.CharField(max_length=3,choices=ROLE_PERMISSIONS)
	comments=models.TextField()


class PageContent(models.Model):
	systype=models.CharField(max_length=30)
	name=models.CharField(max_length=100)
	html_text=models.TextField()

class EmailContent(models.Model):
	systype=models.CharField(max_length=30)
	name=models.CharField(max_length=100)
	subject=models.CharField(max_length=100)
	email_message=models.CharField(max_length=250)
	is_active=models.IntegerField()


class ErrorContent(models.Model):
	systype=models.CharField(max_length=30)
	name=models.CharField(max_length=100)
	errorcode=models.CharField(max_length=10, unique=True)
	error_message=models.TextField()
	
	def __unicode__(self):
		return "%s:%s" % (self.errorcode, self.error_message)


class filestatus(models.Model):
	fileid = models.ForeignKey(uploadedfiles)
	recordno = models.IntegerField()
	roll_no = models.CharField(max_length = 20)
	username = models.CharField(max_length = 20, null=True)
	email = models.EmailField(null=True)
	errorcode = models.ForeignKey(ErrorContent, to_field='errorcode')

class RequestedUsers(models.Model):
	state_id = models.ForeignKey(State)
	institute_id = models.ForeignKey(T10KT_Institute,to_field='instituteid')
	remotecenterid = models.ForeignKey(T10KT_Remotecenter)
	firstname=models.CharField(max_length=45,null=True)
	lastname=models.CharField(max_length=45,null=True)	
	email=models.EmailField(max_length=100,null=False)
	courseid = models.ForeignKey(edxcourses)
	roleid=models.IntegerField()
	designation=models.IntegerField(null=True)





