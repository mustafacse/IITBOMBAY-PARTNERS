from .models import *
from django.shortcuts import render_to_response, render, redirect
import re
from SIP.models import ErrorContent
from django.http import HttpResponseRedirect
from datetime import datetime 
from SIP.models import Userlogin,Institutelevelusers,T10KT_Approvedinstitute,T10KT_Institute,Personinformation
from SIP.models import *
from datetime import *
import csv
from django.core import serializers
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from globalss import *
from django.http import HttpResponse
from IITBOMBAYX_PARTNERS.settings import *
######################## Registration  #####################################

''' VALIDATION OF USER EXISTENCE AFTER FILLING REQUEST REGISTRATION FORM '''  
def Validate_user_existence(email, institute, course, role,page):
        insobj=T10KT_Institute.objects.filter(institutename=institute)
        instituteid = insobj[0].instituteid
        
	lookupobj = Lookup.objects.filter(description=role) 
        roleid = lookupobj[0].code

	if role !="PC":
		courseobj = edxcourses.objects.filter(course=course)
		courseid = courseobj[0].id
             	requserobj = RequestedUsers.objects.filter(email=email, instituteid=instituteid, courseid= courseid, roleid=roleid)
        else:
		requserobj = RequestedUsers.objects.filter(email=email, instituteid=instituteid, roleid=roleid)
        

	print requserobj[0].status,"my status";
        Context={}
        if requserobj:    # user exists then print appropriate error
	    print requserobj[0].status,'asfd'
 	    fname = requserobj[0].firstname
	    reqid=requserobj[0].id  
 	    email=requserobj[0].email 
            if requserobj[0].status == "Requested": # Already Requested user
		pageobj = PageContent.objects.filter(systype="Registration",name="Requested")
		head_message = pageobj[0].html_text
                #head_message="Email id already requested and verified <br><br> Your email id is waiting for approval from Programme Coordinator of institute."
            elif requserobj[0].status == "Rejected": # Rejected by Authorities 
		pageobj = PageContent.objects.filter(systype="Registration",name="Rejected")
		head_message = pageobj[0].html_text    
                #head_message=" Your email id has been rejected by the authorities"
            elif requserobj[0].status == "Registered": # user already registered
		 pageobj = PageContent.objects.filter(systype="Registration",name="Registered")
		 head_message = pageobj[0].html_text
                 #head_message="Email id already registered <br><br> Your email id is already registered. <a href='/'>Click here</a> to login."
            elif requserobj[0].status == "Pending": # user already requested but verification pending
                print "validations"  
		pageobj = PageContent.objects.filter(systype="Registration",name="Pending")
		head_message = pageobj[0].html_text  % (fname,1,reqid);       
                #head_message = "<h>Registration Initiated</h><br><br> Dear %s <br><br> You have already initiated the registration process on IIT Bombayx Partners Portal <br><br> Please verify your email address by clicking the VERIFICATION LINK mailed to you. If you don't get the verification email <a href='/resend_verification_mail/%d/%d'>CLICK HERE.</a> <br><br> After verification, an approval email will be sent to your institute registered Program Coordinator.!" % (fname,1,reqid)
            elif requserobj[0].status == "Approved": #Approved by institutes
                pageobj = PageContent.objects.filter(systype="Registration",name="Approved")
		head_message = pageobj[0].html_text %(reqid)
                #head_message="Email id approved <br> Your email id is already approved by the authorities. To Register <a href='/register/%d/2'> Click Here </a>"% reqid          
		if page=="Registration":
			return Context 
	    
            elif requserobj[0].status == "Invited":
		return Context
	    elif requserobj[0].status == "Pending Consent":
		pageobj = PageContent.objects.filter(systype="Registration",name="Pending Consent")
		head_message = pageobj[0].html_text;
		#head_message="Please check your email<br/><br/>You are already invited for this role."
	    elif requserobj[0].status == "Cancelled":
		pageobj = PageContent.objects.filter(systype="Registration",name="Cancelled")
		head_message = pageobj[0].html_text;
		#head_message = "Your Request was cancelled by the authorities";
	    elif requserobj[0].status == "Declined":
		pageobj = PageContent.objects.filter(systype="Registration",name="Declined")
		head_message = pageobj[0].html_text;
		#head_message = "You have already declined the invitation ";

            Context={'head_message':head_message}
                
        return Context



''' added on 28th '''
#-------- server side field validations ----------#
def registration_field_validations(request,pageid,args):
  
    error=0 #Initialize error variable to 0 i.e no error
    
    ck_fname = r"^[A-Za-z]{2,20}$"
    ck_lname = r"^[A-Za-z]{1,30}$"
    ck_email = r"^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$" 
    ck_password =  r"^[A-Za-z0-9!@#$%^&*()_]{6,20}$"
    ck_mob = r"^[0-9]{10}$"
    '''---------------------------------------------------------'''
    
    if (pageid == 4):  # Request_registration
            if not args['state']: #Check if State is not selected
                  args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOST").error_message)
                  error=1
            elif not args['institute']: #Check if Institute is not selected
                args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOINS").error_message)
                error = 1              
    elif (error == 0):
       # For Rest of the pages
         
         if not args['title']: #Check if Title is not selected
             args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOTL").error_message)
             error =1
    
    # -------------- Common fields -------------------- // 
    
    if (error == 0):
        error = 1
    
        if  not args['first_name']: #Check if First name is Blank
            	args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOFN").error_message)
        elif not re.match(ck_fname, args['first_name']):#check regex
            	 args['errors'].append(ErrorContent.objects.get(errorcode="RG_WRFN").error_message)
        elif not args['last_name']:
            
                if not re.match(ck_lname, args['last_name']): #check regex
                    args['errors'].append(ErrorContent.objects.get(errorcode="RG_WRLN").error_message)
                else :
            		error = 0;
              
        elif not args['email']: # Ckeck if email is blank
            args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOEM").error_message)
        elif not re.match(ck_email,args['email']):#check for regex validation
            args['errors'].append(ErrorContent.objects.get(errorcode="RG_WREM").error_message)
        else: # If no error 
            error = 0;
    
    # --------------------------------------------------//
    
    if (error == 0):
    
        if (pageid == 4): # Request_registration
        
            if not args['course']:
                args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOCS").error_message)
                error = 1
            
            # Role need not to be checked , coz it has been given a default , so user cannot unselect both  
    
    # ----------------  Password Fields ---------------------//
    if (( pageid == 1 or pageid == 2 ) and (error == 0)):
    
    
         error =1;
     
         if not args['password1'] :	#Check if Field is Blank
             args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOPW1").error_message)
         elif not re.match(ck_password,args['password1']) :
            	 args['errors'].append(ErrorContent.objects.get(errorcode="RG_WRPW1").error_message)
         elif args['password2'] : #Check if Field is Blank
             if args['password1'] != args['password2']:
                 args['errors'].append(ErrorContent.objects.get(errorcode="RG_WRPW2").error_message)  	
         else: #No error occured in this part
            error = 0; 
    
    # ----------------------------------------------------//
    
    
    
    # ----- Personal Information ------------//
    
    if ( (pageid != 4) and (error == 0) ):
    
        error=1;
    
        if not args['exp']:
             args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOEXP").error_message) 
        elif not args['gender']:
            args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOGN").error_message)     
        elif not args['qual']:
            args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOQL").error_message)
        elif not args['stream']:
            args['errors'].append(ErrorContent.objects.get(errorcode="RG_NODS").error_message)
        elif not args['phone1']:
            args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOP1").error_message)
        elif not re.match(ck_mob, args['phone1']): #check regex
            args['errors'].append(ErrorContent.objects.get(errorcode="RG_WRP1").error_message)
        elif args['phone2']:  # If office number filled
                if not re.match(ck_mob, args['phone2']): #check regex
                    args['errors'].append(ErrorContent.objects.get(errorcode="RG_WRP2").error_message)
                else:
                    error = 0
        else: # No error occured in this part
            error = 0
    
    # -----------------------------------------//
    
    # --------------- Common Fileds -------------//
    
    if ( (error==0) and not args['desg'] ): 
        
            if not args['desg']:
                args['errors'].append(ErrorContent.objects.get(errorcode="RG_NODG").error_message)
            error = 1;
    
    #--------------------------------------------//
    
    if ( (error == 0)  and (pageid != 3) ): # tos not for edit profile page
    
        if not args['tos-yes']:
                args['errors'].append(ErrorContent.objects.get(errorcode="RG_NOTOS").error_message)
                error = 1
      
    return args




######################################## End of Registration ###########################################################



### Login by Ketaki

## Retrieves error messages for invalid input
def retrieve_error_message(systype,name,errorcode):
    x = ErrorContent.objects.get(systype=systype,name=name,errorcode=errorcode)        
    error_message=x.error_message
    return error_message
"""    
def validate_login(request):
    
                    #logname = request.POST['email']
                    #pwd = request.POST['password']
                    loginlist=[]
                    
                    m=login_obj = Userlogin.objects.get(email=request.POST['email'])
                    if m.password==request.POST['password']:
                           
                            
		            person_obj = Personinformation.objects.get(email=login_obj.email)
                        
                            
                            
                          
		           # print "hello",person_obj.id
		           # insti_obj1 = Institutelevelusers.objects.filter(personid_id=person_obj.id)
                            #print insti_obj1 
                            print person_obj.id,"hello"
                            try:
		                 insti_obj1 = Institutelevelusers.objects.get(personid=person_obj.id)
                                 insti_obj2 = T10KT_Institute.objects.get(instituteid=insti_obj1.instituteid_id)
                                 print insti_obj1.roleid
                                 
                            except:
                                 print "dsfdgfd"
                                 insti_obj1 = Courselevelusers.objects.get(personid=person_obj.id)
                                 print insti_obj1,"sfdsgfdhbn"
                                 insti_obj2 = T10KT_Institute.objects.get(instituteid=insti_obj1.instituteid_id))
                                 print insti_obj1.roleid
                      
		            
		            
                    
                	
                            
                            request.session['person_id']=person_obj.id
			    
                            request.session['email_id']=login_obj.email
                            request.session['role_id']=insti_obj1.roleid
			    print request.session['email_id']
                        #request.session['institute_name'] = insti_obj3.institutename
                            request.session['institute_id'] = insti_obj2.instituteid
                        #request.session['first_name'] = name_obj.firstname
                        #request.session['last_name'] = name_obj.lastname
                        
                            loginlist.append(person_obj.id)
                            loginlist.append(insti_obj2.institutename)
                            loginlist.append(person_obj.firstname)
                            loginlist.append(person_obj.lastname)
                            login_obj.nooflogins +=1
                            login_obj.last_login=datetime.now()
			    login_obj.loginstatus='True'
                            login_obj.save()
                            return loginlist   
		   
            	    else:
			    return -1
   
"""
      
## This function validates the email id and password of the user
## Returns a list and updates userlogin table if valid email id
## Returns an integer value if invalid
def validate_login(request):
  try: 
    
## If email exists, returns a row containing details for that id           
    user_info = Userlogin.objects.get(email=request.POST['email'])
## Checks if the password entered by the user matches with the password in the userlogin table
    if check_password(request.POST['password'],user_info.password):
## Updates the userlogin table   
        if user_info.usertypeid == 0:
           
           request.session['email_id'] =user_info.email
           pson=Personinformation.objects.get(email=user_info.email)
           request.session['person_id']=pson.id
           print "hello"
           return  0
        elif user_info.usertypeid == 2:
           
           request.session['email_id'] =user_info.email
           pson=Personinformation.objects.get(email=user_info.email)
           request.session['person_id']=pson.id
           print "hello1#"
           return  2
        elif user_info.usertypeid == 3:
           
           request.session['email_id'] =user_info.email
           pson=Personinformation.objects.get(email=user_info.email)
           request.session['person_id']=pson.id
           print "hello1#"
           return  3
           
        print "asdsa"
        request.session['email_id'] =user_info.email
        user_info.nooflogins +=1
        user_info.last_login=datetime.now()
        user_info.status=1
        user_info.save()
        return 1   

    else:
## If password not valid, then returns -1
        return -1
        
  except:
## If email id does not exist, then returns -1
        return -1

def validate_email(email):
    try:
        email_obj = Personinformation.objects.get(email=email)
        if email_obj:
		
                return email_obj.id
                
        else:
                return -1
    except:
            return -1

def emailid_validate(request,args):
    module = 'Login'
    ck_email = r"^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$"
## Checks if email is blank
    if not args['email']: 
        args['error_message']=retrieve_error_message(module,'Email_empty','EML_EMPTY')
## Check for regex validation
    elif not re.match(ck_email,args['email']):
        args['error_message']=retrieve_error_message(module,'Email_invalid','INV_EML')
    return args
    
def pwd_field_empty(request,args,value):
    ck_password =  r"^[A-Za-z0-9!@#$%^&*()_]{6,20}$"	
    module = 'Login'
    if value == 'CH_PASS':
        if not args['old_password']:
            args['message']=retrieve_error_message(module,'Pwd_empty','PASS_EMPTY')
## Checks if Field is Blank
    if not args['password1'] :	
        args['message']=retrieve_error_message(module,'Pwd_empty','PASS_EMPTY')
    elif not re.match(ck_password,args['password1']):
        args['message']=retrieve_error_message(module,'Pwd_invalid','INV_PASS')
## Checks if Field is Blank
    elif not args['password2'] :	
        args['message']=retrieve_error_message(module,'Pwd_empty','PASS_EMPTY')

    return args
            
def logged_in(request):
    try:
        if request.session['email_id']:
            return True
        else:
            return False
    except:
        return False


   
def password_reset(emailid,password):
    pwd_obj = Personinformation.objects.get(id=emailid)
    pwd_obj2 = Userlogin.objects.get(email=pwd_obj.email)
    pwd_obj2.password = password
    pwd_obj2.save()
 
def password_change(oldpwd,personid):
        pwd_obj = Personinformation.objects.get(id=personid)
        pwd_obj2 = Userlogin.objects.get(email=pwd_obj.email)
        if check_password(oldpwd,pwd_obj2.password) :
            return 1
        return 0

def logoutt(request):
  try:
    user_info = Userlogin.objects.get(email=request.session['email_id'])
    user_info.loginstatus='False'
    user_info.save()
     
    del request.session['person_id']
    del request.session['email_id']
    del request.session['institute_id']
    del request.session['role_id']
  except:
    return HttpResponseRedirect('/')

### End Login by Ketaki

####  Apoorva Agrawal

def validateEmail(email):

	if len(email) > 4:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return 1
	return 0



### End Apoorva Code






######################################################## Course management ########################################################

def enrollformvalidation(input_list):                     #this validation is for validating entries of enrolling form

	#if corresponding_course_name is empty
	if not input_list['coursename']:
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_ECCN").error_message)

	#if corresponding_course_name starts with space or has no alphabet
	ccname=input_list['coursename']
	if ccname:
		if (ccname[0]==" "):
			input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_SCCN").error_message)
		if not (any(c.isalpha() for c in ccname)):
			input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_ACCN").error_message)

	#if startdate is empty
	if not input_list['startdate']:
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_STD").error_message)

	#if enddate is empty
	if not input_list['enddate']:
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_ED").error_message)

	#if startdate is earlier than end date
	if (input_list['startdate']>=input_list['enddate']):
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_IED").error_message)

	#if program is empty
	if (input_list['program']=="select"):
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_EP").error_message)

	#if year is empty
	if (input_list['year']=='0'):
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_EY").error_message)

	#if total_moocs_students is empty
	if not input_list['total_moocs_students']:
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_ETS").error_message)

	#if total_course_students is empty
	if not input_list['total_course_students']:
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_ETSP").error_message)

	#if total_moocs_students is greater than total_course_students
	if ((input_list['total_moocs_students'])>(input_list['total_course_students'])):
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_INS").error_message)

def unenrollvalidation(input_list):                      #this validation is for validating entries of unenrolling form
	#if reason of cancellation is empty
	if not input_list['reason']:
		input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_IRC").error_message)

	reason=input_list['reason']
	if reason:
		if (reason[0]==" "):
			input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_SR").error_message)
		if not (any(c.isalpha() for c in reason)):
			input_list['errors'].append(ErrorContent.objects.get(errorcode="CM_AR").error_message)
		


####################################################### End course management  ##############################################################


######################## Student management code #####################################

def is_error(request,rollnum,user,email,courseid,currentfile):


#--------------------------
#local variables
#--------------------------
    
    validemail = False
#--------------------------

    print "in is error",user       
    for row in IITBX_authuser.objects.raw('SELECT * FROM SIP_iitbx_authuser'):
        if row.email == email:
            validemail=True
	    obj = row	
            break

#if email not found

    if not validemail:
        return inv_email#check error code        
        
#if username not found
    
    if obj.username != user:
        return inv_user#check error code        

#if student has not yet enrolled      
    '''for row in studentDetails.objects.select_related():
        if row.userid.username == user and row.courseid_id != courseid:
            return"not_enroll"
        if row.userid.username== user and row.roll_no==rollnum:
            return "duplicate"'''
    try:
        obj=IITBX_studentcourseenrollment.objects.get(userid__username=user)
        print courseid,obj.courseid.courseid  
        if obj.courseid.courseid != courseid:
            return not_enroll
              
    except:
        
        return not_enroll 

    try:	   
    	obj=studentDetails.objects.get(userid__username=user)
    	if obj.roll_no == rollnum and obj.teacherid_id!=1 and obj.teacherid_id!=request.session['person_id']:
        	return diffteacher#update
    	if obj.roll_no == rollnum and obj.teacherid_id==request.session['person_id']:
        	return duplicate 
    
    	if obj.roll_no!="0" :
		return duplicate
    except:
	HttpResponse("studentdetails ")	   
    
#if no error
    return False 
                    
#--------------------------------------------------------------------------------------------------------



'''def is_error(rollnum,user,email,courseid,currentfile):


#--------------------------
#local variables
#--------------------------
    
    validemail = False
#--------------------------

        
    for row in IITBX_authuser.objects.raw('SELECT * FROM SIP_iitbx_authuser'):
        if row.email == email:
            validemail=True
	    obj = row	
            break

#if email not found

    if not validemail:
        return "inv_email"#check error code        
        
#if username not found
    
    if obj.username != user:
        return "inv_user"#check error code        

#if student has not yet enrolled      
    for row in studentDetails.objects.select_related():
        if row.userid.username == user and row.courseid_id != courseid:
            return"not_enroll"
        if row.userid.username== user and row.roll_no==rollnum:
            return "duplicate"
            
	   
    
#if no error
    return False '''
                    
#--------------------------------------------------------------------------------------------------------


#----------------------------------------------------#
#This function is used to validate the records-------#
#This function detects following errors--------------#
#1)invalid username----------------------------------#
#2)invalid email-id----------------------------------#
#3)student not enrolled for the course---------------#
#----------------------------------------------------#

def validate_file_extension(fname):
    if not fname.endswith('.csv'):
        return 0
    return 1

'''def is_valid_record(request,rollnum,user,email,recordno, currentfile,t_dropdwn):


#--------------------------
#local variables
#--------------------------
    validusername = False
    validemail = False
#--------------------------

        
    for row in IITBX_authuser.objects.raw('SELECT * FROM SIP_iitbx_authuser'):
        if row.email == email:
            validemail=True
        if row.username == user:
            validusername = True
        if validusername and validemail:
		break
    if not validusername:   
        message = ErrorContent.objects.get(errorcode = "invaliduse")#check error code        
        query =student_interface(fileid = currentfile ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message)
        query.save()
    elif not validemail:
        message = ErrorContent.objects.get(errorcode = "invalidema")#check error code        
        query =student_interface(fileid = currentfile  ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message)
        query.save()
    
    if validemail and validusername:
	print "kamal"
        x=Courselevelusers.objects.get(personid=request.session['person_id'])
        print x.courseid.courseid
	y = edxcourses.objects.get(courseid = x.courseid.courseid)
	course = y.courseid
	print course
	user_id=IITBX_authuser.objects.get(username=user).id
	print user_id
        row = studentDetails.objects.filter(userid=user_id,courseid=course)
        if not row:    
#if student has not yet enrolled
		message = ErrorContent.objects.get(errorcode = "notenrolle")#check error code        
		query =student_interface(fileid = currentfile ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message)
		query.save()

		return {'add':False,'valid':False}	

	#if student record already exists
	row = studentDetails.objects.filter(userid=user_id,roll_no=rollnum,courseid=course)
	if row:
		if t_dropdwn:
		    return {'add':True,'valid':True}
		return {'add':False,'valid':True}
                    

                    

        if t_dropdwn:
	    message = ErrorContent.objects.get(errorcode = "invalidrol")#check error code        
            query = student_interface(fileid = currentfile ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message) 
            query.save()	
            return {'add':False,'valid':False}
        return {'add':True,'valid':True}
                
# if email or user name is invalid         
    else:
        return {'add':False,'valid':False}
#-----------------------------------------------------#        
#-----------------------------------------------------#
#This function reads csv file line by line and handles following errors
#1)invalid record format
#2)blanckline in a file
#3)duplicate record
#----------------------------------------------------#
#This function also updates studentdetails table-----#
#----------------------------------------------------#

#-----------------
#new code
#----------------
        
def parse(request,t_session,t_dropdwn,fname):
    print "parse"
    currentfile = uploadedfiles.objects.get(filename = fname)
    fo=open(fname,'rb')    
    reader = csv.reader(fo)
    validcount = 0
    invalidcount = 0
    recordno= 0 
    personid=request.session['person_id']
    course=Courselevelusers.objects.get(personid=request.session['person_id']).courseid.courseid
    print personid,course  
    #student_interface.objects.all().delete()    #remove previous errors
    for line in reader:
        print line
        recordno+=1
        if line:
            if line[0] == "Roll no":
                recordno-=1
                continue
            print len(line) ,"length"
            if len(line)!= 3:
                message = ErrorContent.objects.get(errorcode = "invalidrec")#check error code        
                query = student_interface(fileid = currentfile ,recordno = recordno,roll_no = 0,email = "none" , username = "none" , errorcode = message)
                query.save()
                invalidcount+=1
                continue
            
            rollnum = line[0]
            print rollnum
            user = line[1]
            email = line[2]
	    user=user.replace(" ","")
	    email=email.replace(" ","")
	    rollnum=rollnum.replace(" ","")
            record = is_valid_record(request,rollnum,user,email,recordno,currentfile,t_dropdwn)
            print record
            if record['add']:
                validcount+=1

#---------------------------------------------------------------------------
#updating studentDetails table
#---------------------------------------------------------------------------
		
                if t_session:
			student=studentDetails.objects.filter(userid__username = user,courseid=course)
			student.update(roll_no = rollnum)
			student.update(teacherid=personid)
			student.update(last_updated_by=personid)
			student.update(last_update_on=date.today())
                elif t_dropdwn:
                      
                      studentDetails.objects.filter(userid__username = user).update(teacherid = t_dropdwn)#check from session or dropdown
            
#--------------------------------------------------------------------------
                message = ErrorContent.objects.get(errorcode = "noerror")#check error code        
                query = student_interface(fileid = currentfile ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message) 
                query.save()
            else:  
                
                invalidcount+=1
		if record['valid']:
                   
                 
                    
		        message = ErrorContent.objects.get(errorcode = "duplicate")#check error code        
		        query = student_interface(fileid = currentfile ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message) 
		        query.save()
            
                
                            
                                                      
                    
            
        else:
            message = ErrorContent.objects.get(errorcode = "blankline")#check error code        
            query = student_interface(fileid = currentfile ,recordno = recordno,roll_no = 0,email = "None" , username = "None" , errorcode = message) 
            
            query.save()
            invalidcount+=1
            
    
    context = {'validcount':validcount,'invalidcount':invalidcount,'totalrecords':validcount+invalidcount}            
    context.update({'filename':currentfile.filename})
    
    errorreport = student_interface.objects.filter(fileid = currentfile)#check file name
    
    context.update({'errorreport':errorreport})
   
#----------------------------------------------------
#updating 'uploaded files table'
#----------------------------------------------------

    if invalidcount:
	uploadedfiles.objects.filter(filename = currentfile.filename).update(errorocccur = True)
    uploadedfiles.objects.filter(filename = currentfile.filename).update(is_read = True)
#-----------------------------------------------------

    		
    return context'''
    

#This function also updates studentdetails table-----#
#----------------------------------------------------#

#-----------------
#new code
#----------------
                
def parse(request,courseid,fname):
    
#----local varialbles------

    validcount = 0
    invalidcount = 0
    recordno= 0    
    rollnum=0
    user=""
    email=""
#--------------------------


    currentfile = uploadedfiles.objects.get(filename = fname)
    fo=open(fname,'rb')    
    reader = csv.reader(fo)
    
    #student_interface.objects.all().delete()    #remove previous errors
    for line in reader:
        recordno+=1
		

#if empty line

        if not line:
		
			error_code= blankline#check error code        
        
#if first line contains headings

        elif line[0] == "Roll no":
		
            recordno-=1
            continue

#if file line doesn't contain 3 columns
        
        elif len(line)!= 3:
		
            error_code = inv_rec#check error code 
            
        else:
            
                    
		 rollnum = line[0].replace(" ","")
		 user = line[1].replace(" ","")
		 email = line[2].replace(" ","")
               
		 error_code = is_error(request,rollnum,user,email,courseid,currentfile)
        if error_code:
            invalidcount+=1
        else:
            validcount+=1
            error_code=noerror

#----------------store error---------------------------
        message = ErrorContent.objects.get(errorcode = error_code)#check error code        
        query = student_interface(fileid = currentfile ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message) 
        query.save()    
#-----------------------------------------------------



#----------------------------------------------------
#updating 'uploaded files table'
#----------------------------------------------------

    if invalidcount:
		uploadedfiles.objects.filter(filename = currentfile.filename).update(errorocccur = True)
    uploadedfiles.objects.filter(filename = currentfile.filename).update(is_read = True)
#-----------------------------------------------------
		    		
		        
    context = {'validcount':validcount,'invalidcount':invalidcount,'totalrecords':validcount+invalidcount}            
    context['filename']=currentfile.filename
    
    errorreport = student_interface.objects.filter(fileid = currentfile)#check file name
    context['errorreport']=errorreport

    		
    return context             

              
'''def parse(request,courseid,fname):
    
#----local varialbles------

    validcount = 0
    invalidcount = 0
    recordno= 0    
    rollnum=0
    user=""
    email=""
#--------------------------


    currentfile = uploadedfiles.objects.get(filename = fname)
    fo=open(fname,'rb')    
    reader = csv.reader(fo)
    
    #student_interface.objects.all().delete()    #remove previous errors
    for line in reader:
        recordno+=1
		

#if empty line

        if not line:
		
			error_code= "blankline"#check error code        
        
#if first line contains headings

        elif line[0] == "Roll no":
		
            recordno-=1
            continue

#if file line doesn't contain 3 columns
        
        elif len(line)!= 3:
		
            error_code = "inv_rec"#check error code 
            
        else:
            
                    
		 rollnum = line[0].replace(" ","")
		 user = line[1].replace(" ","")
		 email = line[2].replace(" ","")

		 error_code = is_error(rollnum,user,email,courseid,currentfile)
        if error_code:
            invalidcount+=1
        else:
            validcount+=1
            error_code="noerror"

#----------------store error---------------------------
        message = ErrorContent.objects.get(errorcode = error_code)#check error code        
        query = student_interface(fileid = currentfile ,recordno = recordno,roll_no = rollnum,email = email , username = user , errorcode = message) 
        query.save()    
#-----------------------------------------------------



#----------------------------------------------------
#updating 'uploaded files table'
#----------------------------------------------------

    if invalidcount:
		uploadedfiles.objects.filter(filename = currentfile.filename).update(errorocccur = True)
    uploadedfiles.objects.filter(filename = currentfile.filename).update(is_read = True)
#-----------------------------------------------------
		    		
		        
    context = {'validcount':validcount,'invalidcount':invalidcount,'totalrecords':validcount+invalidcount}            
    context['filename']=currentfile.filename
    
    errorreport = student_interface.objects.filter(fileid = currentfile)#check file name
    context['errorreport']=errorreport

    		
    return context             
'''
#-----------------------------------------------------#
#-----------------------------------------------------#
                

######################################## End of student management code ###########################################################


#--------------------------------------------------
#Function for send email
#--------------------------------------------------

def send_email(ec_id, req_id, per_id):
    #try:
	    ec_id = int(ec_id)
	    req_id = int(req_id)  
	    
	    per_id = int(per_id)
	    mail_obj = EmailContent.objects.filter(id=ec_id)
	    req_obj = RequestedUsers.objects.filter(id = req_id)
	    if req_obj:
		    fname = req_obj[0].firstname
		    lname = req_obj[0].lastname
		    email = req_obj[0].email
		    code = req_obj[0].roleid
		    role = Lookup.objects.filter( category = 'Role', code = code)
		    role = role[0].comment
		    if not ((role == 'Program Coordinator') or (role == 'Head of Institute')):
		    	cname = edxcourses.objects.filter(id = req_obj[0].courseid_id)
		    	cname= cname[0].coursename 
			iname = T10KT_Institute.objects.get(instituteid = req_obj[0].instituteid.instituteid).institutename 
		    link = ROOT_URL + mail_obj[0].name + '/%d' %req_id
	    if ec_id == 1: # Email verification -> user
		message = mail_obj[0].message %(fname, link, email)
	    elif ec_id == 2: # request for approval -> higher authorities
		message = mail_obj[0].message %(role, cname, email, fname)
	    elif ec_id ==3: # request submitted mail -> user
		message = mail_obj[0].message %(fname, role, cname)
	    elif ec_id == 4: # accepted, register link -> user
		message = mail_obj[0].message %(fname, role, cname, link)
	    elif ec_id == 5: # rejected by authorities mail to user
		message = mail_obj[0].message %(fname, role)
	    elif ec_id == 6: # request register to HOI's
		cname = edxcourses.objects.filter(id = req_obj[0].courseid_id)
		cname= cname[0].coursename
		message = mail_obj[0].message %(fname,cname,link)
	    elif ec_id == 8: # successful registration to user(CC AND TA)
		message = mail_obj[0].message %(fname,role,cname)
	    elif ec_id == 9: #Invite Program Coordinator /2 for the roles of PC, CC, TA
		link = ROOT_URL + mail_obj[0].name + '/%d/2' %req_id 
		message = mail_obj[0].message %(fname, role,link)
	    elif ec_id == 10: # Reset password of a user
		per_obj = Personinformation.objects.filter(id = per_id)
		fname = per_obj[0].firstname
		email = per_obj[0].email
		link = ROOT_URL + mail_obj[0].name + '/%d' %per_id
		message = mail_obj[0].message %(fname, link)
	    elif ec_id == 11: # Reset password of a user
		per_obj = Personinformation.objects.filter(id = per_id)
		fname = per_obj[0].firstname
		email = per_obj[0].email
		link = ROOT_URL + mail_obj[0].name + '/%d' %per_id
		message = mail_obj[0].message %(fname)
	    elif ec_id == 12: #Invite Program Coordinator /2 for the roles of PC, CC, TA
		linked = mail_obj[0].name.split(',')
		#per_obj = Personinformation.objects.filter(id = 9)
		#fname = per_obj[0].firstname
		link1 = ROOT_URL + linked[0] + '/%d' %req_id 
		link2 = ROOT_URL + linked[1] + '/%d' %req_id 
		print 'link1',link1
		print 'link2',link1
		print mail_obj[0].message
		message = mail_obj[0].message %(fname,role,link1,link2)
	    elif ec_id == 13: #Invite Program Coordinator /2 for the roles of PC, CC, TA
		link = ROOT_URL + mail_obj[0].name + '/%d/2' %req_id 
		cname = edxcourses.objects.filter(id = req_obj[0].courseid_id)
		cname= cname[0].coursename
		message = mail_obj[0].message %(fname, role,cname,link)
	    elif ec_id == 14: #Invite Program Coordinator /2 for the roles of PC, CC, TA
		cname = edxcourses.objects.filter(id = req_obj[0].courseid_id)
		cname= cname[0].coursename
		linked = mail_obj[0].name.split(',')
		link1 = ROOT_URL + linked[0] + '/%d' %req_id 
		link2 = ROOT_URL + linked[1] + '/%d' %req_id 
		message = mail_obj[0].message %(fname, role,cname,link1, link2)    
	    elif ec_id == 15: #Email to acknowledge approval 
		cname = edxcourses.objects.filter(id = req_obj[0].courseid_id)
		cname= cname[0].coursename 
		message = mail_obj[0].message %(fname, role,cname)    
	    elif ec_id == 16: #Email to acknowledge rejection
		cname = edxcourses.objects.filter(id = req_obj[0].courseid_id)
		cname= cname[0].coursename 
		message = mail_obj[0].message %(fname, role,cname)    
	    elif ec_id == 17: #Email to acknowledge cancellation
		message = mail_obj[0].message %(fname, role)  
	    elif ec_id == 19: #Email to inviter that his invite has been declined by invitee
		cname = edxcourses.objects.filter(id = req_obj[0].courseid_id)
		cname= cname[0].coursename 
		print per_id , "per_id"
		hname = Personinformation.objects.get(id = per_id).firstname
	#	hname = per_id.objects.get(id = per_id)
		message = mail_obj[0].message %(hname, role,cname, fname)    
	    elif ec_id == 23: #Email to acknowledge change of password
		message = mail_obj[0].message %(fname)    
	    send_mail(mail_obj[0].subject, message , EMAIL_HOST_USER ,[email], fail_silently=False)    
    #except:
		#print "email facility not working"


#--------------------------------------------------
#End of Function
#--------------------------------------------------



 
#### performance module ####
def validate(userid, user_name, emailid):
	valid = IITBX_authuser.objects.filter(id=userid,username=user_name,email=emailid)
	if valid:
		return True
	else:
		return False


#########################################blended mooc coordinator and admin  ##########################################################

def bmcvalidate(input_list):
	if input_list['institute_name']=='select':
		print "in bmcvalidate"
		input_list['errors'].append(ErrorContent.objects.get(errorcode="BMC_EI").error_message)

def bmcrolevalidate(input_list):
	if input_list['role']=="select":
		input_list['errors'].append(ErrorContent.objects.get(errorcode="BMC_ER").error_message)

def reportvalidate(input_list):
	if input_list['report_name']=="select":
		input_list['errors'].append(ErrorContent.objects.get(errorcode="ADM_ER").error_message)

###########################################   end blended mooc coordinator and admin ######################################################




#------------------------------------------------------------------------------
#   Validations for bulk email
#------------------------------------------------------------------------------

def validateFname(fname):
    if len(fname) > 1:
        if re.match("^[A-Z][\.\ ]?[a-zA-Z]+$", fname) != None:
            return 1
    return 0

def validateLname(lname):
    if len(lname) >= 1:
        if re.match("^[A-Z][a-zA-Z]*$", lname) != None:
            return 1
    return 0

def validateInstitute(institutename):
    try:
        insti_obj =T10KT_Institute.objects.filter(institutename = institutename)
        if insti_obj :
            return 1
        else : 
            return 0
    except:
        return 0
    
def validateRole(role):
    try:
        look_obj = Lookup.objects.filter(category = 'Role', comment = role)
        if look_obj :
            return 1
        else :
            return 0
    except:
        return 0

def validateCourse(course):
    try:
        edx_obj = edxcourses.objects.filter(course = course)
        if edx_obj :
            return 1
        else :
            return 0
    except:
        return 0
    
def validatePC(email, role):
    try:
        per_obj = Personinformation.objects.get(email = email)
        if per_obj:
            if Institutelevelusers.objects.get(personid = per_obj, roleid = role):
                return 0
            else :
                return 1
    except:
        return 1
        
        
def validateUser(email, role, course):
    try:
        per_obj = Personinformation.objects.get(email = email)
	if per_obj:
        	if Courselevelusers.objects.get(personid = per_obj, roleid = role, courseid = course):
	            return 0
        	else :
        	    return 1
    except:
        return 1


