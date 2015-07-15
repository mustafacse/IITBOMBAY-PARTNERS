from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core.mail import send_mail
import datetime
from datetime import date,timedelta
from django.db import transaction
from django.contrib import auth
from django.template import Context
##ketaki
#from django.contrib.auth.decorators import login_required
#from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.models import User
from SIP.models import Userlogin
from SIP.validations import retrieve_error_message,validate_login,validate_email,password_reset
from django.core.mail import send_mail

#importing the PersonInformation Class from models.py
from .models import *


#importing the validations from validations.py
from .validations import *
############## student management:import statements ##########################
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from forms import UploadForms
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib import messages
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError
from django.conf.urls.static import static
from django.db.models import Q
import glob 
from django.core.files import File
from SIP.models import *
import csv
import MySQLdb


#------------------------------------------
from SIP.validations import *
#------------------------------------------
#------------------------------------------
# Create your views here.

# Create your views here.
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.utils import timezone
from django.conf import settings
from forms import UploadForms
from django.template import RequestContext
from django.contrib import messages
from django.shortcuts import render_to_response, render
import glob 
from django.core.files import File
from django.utils.datastructures import MultiValueDictKeyError
#from easygui import *
import csv
from bs4 import *
from urllib2 import urlopen
import sys
import cStringIO as StringIO
from django.template.loader import get_template
from django.template import Context
from cgi import escape
import urllib2,cookielib
from django.db import connection, transaction
import json

ROOT_URL = 'http://10.105.22.21:9005'
EMAIL_HOST_USER = 'tushars@cse.iitb.ac.in'
#############################end of import statements by student management#######################################






def sessionlogin(request):
    args = {}
    args.update(csrf(request)) 
    try:
	    if request.session['email_id']:
	       return ccourse(request)
	    else:               
		return loginn(request)
    except:
            return loginn(request)





######################## Registration  #####################################


@csrf_protect
def register(request,reqid):
   
    if request.method == 'POST':
        #fetch all data from html page
        email = request.POST['email']
        institute = request.POST.get('Institute','')
        title = request.POST.get('title','')
        first_name = request.POST.get('fname','')
        last_name = request.POST.get('lname','')
        password1 = request.POST.get('password1','')
        password2 = request.POST.get('password2','')
        exp = request.POST.get('experience','')
        gender = request.POST.get('gender','')
        desg = request.POST.get('Desg','')
        qual = request.POST.get('Qual','')
        stream = request.POST.get('stream','')
        phone_per = request.POST.get('phone1','')
        phone_office = request.POST.get('phone2','')
        tos= request.POST.get('terms_of_service','')
        
        # Validations : 
        #Two password fields : Both fields should be Same
        #tos filed should be checked : Kindly Agree to the Terms and Conditions
    
        #fetch institute id : 
        #interface = RequestedUsers.objects.filter(id=reqid)
        
        reqobj = RequestedUsers.objects.filter(id=reqid)
        reqobj1 = reqobj[0]
        
        insid=reqobj1.instituteid_id
        courseid = reqobj1.courseid_id
        roleid = reqobj1.roleid
        email = reqobj1.email
        
        #tid=sid=did=0
        
        lookobj = Lookup.objects.filter(description=title)
        #if lookobj:
        tid=lookobj[0].code
        lookobj = Lookup.objects.filter(description=stream)
        #if lookobj:
        sid=lookobj[0].code
        lookobj = Lookup.objects.filter(description=desg)
        #if lookobj:
        did=lookobj[0].code
    	
        interface_obj = Personinformation(titleid=tid,designation=did,streamid=sid,instituteid_id=insid,email=email,firstname=first_name,lastname=last_name,experience=exp,gender=gender,qualification=qual) #telephone1=phone_per,telephone2=phone_office
        interface_obj.save()
        
        obj2 = Userlogin ( usertypeid=1,email=email,password=password1) # 1 means IITBOMBAYX Partner system
        obj2.save()
        
        per = Personinformation.objects.filter(email=email)
        personid=per[0].id
        
        interface = RequestedUsers.objects.filter(id=reqid)  
        roleid = interface[0].roleid        
        courseid = interface[0].courseid_id
        
        #After Successfull Registeration , Status in Requestedusers table is changed to Registered
        RequestedUsers.objects.filter(id=reqid).update(status="Registered")
        
        if roleid==4 or roleid==5 or roleid == 3:  #If Register page Filled By Course_Level_User
            obj4=Courselevelusers(courseid_id=courseid,roleid=roleid,personid_id=personid,instituteid_id=insid,startdate=date.today(),enddate="4712-12-31")
            obj4.save()
            send_email(8,reqid,reqid)
        else:   #If Register page Filled By Institute_Level_User ( i.e for PC)
            obj4=Institutelevelusers(instituteid_id=insid,roleid=roleid,personid_id=personid,startdate=date.today())
            obj4.save()
            role="Program Co-ordinator"
            message = mail_obj[0].message %(first_name,role)
            send_mail(mail_obj[0].subject, message , EMAIL_HOST_USER ,[email], fail_silently=False)
       
        
        # Send mail to the person about successful registration
    
        
        
        head_message = "You have successfully completed registration on IITBX- Partner System.<br>Your account has been created.<a href='/'>Click here<a> to login"
        Context={'head_message':head_message}
        return render_to_response('home.html',Context,context_instance=RequestContext(request))
    
    
    ''' FIRST CHECK FOR VALID USER '''
    req_obj = RequestedUsers.objects.get(id = reqid)
    course = edxcourses.objects.get(id = req_obj.courseid_id).course
    institute =T10KT_Institute.objects.get(instituteid= req_obj.instituteid_id).institutename
    role = Lookup.objects.get(category='role', code=req_obj.roleid).description
    
    Context = Validate_user_existence(req_obj.email, institute, course, role,"Registration")    
    
    if Context:
        return render_to_response('home.html',Context,context_instance=RequestContext(request))
   
    reqobj = RequestedUsers.objects.filter(id=reqid)
    reqobj1=reqobj[0]
    insid=reqobj1.instituteid_id
    insobj=T10KT_Institute.objects.filter(instituteid=insid)
    institute=insobj[0].institutename
    
    desgid=reqobj1.designation
    fname=reqobj1.firstname
    lname=reqobj1.lastname    
    emailid=reqobj1.email
    
    desig =Lookup.objects.values('description','category','code')
    designations=[]
    qual_list=[]
    title_list=[]
    stream_list=[]
    
    for row in desig:
        if(row['category']=="Designation"):
            designations.append(row['description'])  # i['is_active'] gives me value coreesponding to description key
            if row['code']==desgid:
                desg=row['description']
        if(row['category']=="Qualification"):
            qual_list.append(row['description'])
        if row['category']=="ParticipantTitle":
            title_list.append(row['description'])
        if row['category']=="Stream":
            stream_list.append(row['description'])
            
    Context = {'fname':fname,'lname':lname,'desg' : desg ,'emailid' : emailid,'institute' : institute, 'desg_list': designations,'qual_list' : qual_list,'title_list' : title_list,'stream_list' : stream_list}  
    args = {}
    args.update(csrf(request))
    return render_to_response(
    'registration/Registeration.html',Context, context_instance=RequestContext(request))
 

def auth_register(request,appinsid):
   
    if request.method == 'POST':
	email = request.POST['email']
        perobj=Personinformation.objects.filter(email=email)
    
        if perobj: 
            head_message="Email id already registered <br><br> Your email id is already registered. <a href='/'>Click here</a> to login."
            Context={'head_message':head_message}
            return render_to_response('home.html',Context,context_instance=RequestContext(request))
            
        #fetch all data from html page
        
        institute = request.POST.get('Institute','')
        title = request.POST.get('title','')
        first_name = request.POST.get('fname','')
        last_name = request.POST.get('lname','')
        password1 = request.POST.get('password1','')
        password2 = request.POST.get('password2','')
        exp = request.POST.get('experience','')
        gender = request.POST.get('gender','')
        desg = request.POST.get('Desg','')
        qual = request.POST.get('Qual','')
        stream = request.POST.get('stream','')
        phone_per = request.POST.get('phone1','')
        phone_office = request.POST.get('phone2','')
        tos= request.POST.get('terms_of_service','')
       
        ''' fetch ids from lookup table ( code ) '''
        lookobj = Lookup.objects.filter(description=title)
        tid=lookobj[0].code
        lookobj = Lookup.objects.filter(description=stream)
        sid=lookobj[0].code
        lookobj = Lookup.objects.filter(description=desg)
        did=lookobj[0].code
    	
        insobj = T10KT_Institute.objects.filter(institutename=institute)
        insid=insobj[0].instituteid
   	
        ''' Fill all details in tables '''
        interface_obj = Personinformation(titleid=tid,designation=did,streamid=sid,instituteid_id=insid,email=email,firstname=first_name,lastname=last_name,experience=exp,gender=gender,telephone1=phone_per,telephone2=phone_office,qualification=qual)
        interface_obj.save()
        
        obj2 = Userlogin ( usertypeid=1,email=email,password=password1) # 1 means IITBOMBAYX Partner system
        obj2.save()
        
        per = Personinformation.objects.filter(email=email)
        personid=per[0].id
        
        rcobj=T10KT_Remotecenter.objects.filter(instituteid=insid)
        rcid=rcobj[0].remotecenterid
        
        #After Successfull Registeration , update approvedinstitute table columns
        T10KT_Approvedinstitute.objects.filter(id=appinsid).update(remotecenterid=rcid,instituteid=insid)
        print "approved filled"
        obj4=Institutelevelusers(instituteid_id=insid,roleid=2,personid_id=personid,startdate=date.today(),enddate=date.today() + timedelta(days=7)) #roleid is hardcoded with value=2 as this is only for HOI
        obj4.save()
        
        #TODO - verify his email first
        print "Instituelevel filled"
        #  Send mail to the person about successful registration
        role="Head of Institute"
	mail_obj = EmailContent.objects.filter(id=7)
        message = mail_obj[0].message %(first_name,role)
        send_mail(mail_obj[0].subject, message , EMAIL_HOST_USER ,[email], fail_silently=False)
       
        head_message = "You have successfully completed registration on IITBX- Partner System.<br>Your account has been created.<a href='/'>Click here<a> to login"
        Context={'head_message':head_message}
        return render_to_response('home.html',Context,context_instance=RequestContext(request))
    

    #fetch email from table using appinsid in url
    appinsobj = T10KT_Approvedinstitute.objects.filter(id=appinsid)
    appins1=appinsobj[0]
    email=appins1.heademail
     
    # validate user existence
    perobj=Personinformation.objects.filter(email=email)
    
    if perobj: 
        	 head_message="Email id already registered <br><br> Your email id is already registered. <a href='/'>Click here</a> to login."
        	 Context={'head_message':head_message}
        	 return render_to_response('home.html',Context,context_instance=RequestContext(request))
    else:
	    #get all state list
	    stateobj = T10KT_State.objects.values('state')
	    states=[]
	    for row in stateobj:
		states.append(row['state'])
	    
	    institute_list = []
	    insobj=T10KT_Institute.objects.all()
	    for row in insobj:
		institute_list.append(row.institutename)     
	    institute_list.sort()
	   
	    ''' get all dropdowns '''
	    desig =Lookup.objects.values('description','category','code')
	    designations=[]
	    qual_list=[]
	    title_list=[]
	    stream_list=[]
	    
	    for row in desig:
		if(row['category']=="Designation"):
		    designations.append(row['description'])  # i['is_active'] gives me value coreesponding to description key
		if(row['category']=="Qualification"):
		    qual_list.append(row['description'])
		if row['category']=="ParticipantTitle":
		    title_list.append(row['description'])
		if row['category']=="Stream":
		    stream_list.append(row['description'])
		    
	    Context = {'state_list':states,'emailid' : email , 'institute_list':institute_list , 'desg_list': designations,'qual_list' : qual_list,'title_list' : title_list,'stream_list' : stream_list}  
	    args = {}
	    args.update(csrf(request))
	    return render_to_response(
	    'registration/auth_register.html',Context, context_instance=RequestContext(request))
	   

def emailto_higherauthorities(reqid):
    rcobj = RequestedUsers.objects.filter(id=reqid)
    print rcobj,"asfdsdf"
    rcobj1=rcobj[0]
    print rcobj1,"ssdf"

    #fetch institute id and roleid
    insid=rcobj1.instituteid.instituteid
    print insid
    roleid=rcobj1.roleid
    courseid = rcobj1.roleid
    
    #fetch all authorities above this person and send them email regarding request 
    inslevelobj=Institutelevelusers.objects.filter(instituteid=insid)
    if inslevelobj : #only if we get any object proceed
        for row in inslevelobj:
            if row.roleid < roleid :# take only higher authorities and send them a mail
		print row.personid.id,"123",type(row.personid.id)
                send_email(2,reqid,row.personid.id)
    
    if roleid <= 5: # only if user is teacher fetch all coure-co-od's from this table 
        courselevelobj=Courselevelusers.objects.filter(instituteid=insid,courseid=courseid)    
        for row in courselevelobj:
            if row.roleid < roleid and row.courseid == courseid  :# to respective course course-co-od 
                send_email(2,reqid,row.personid)
   
    return 1 
   
   
def request_verification_success(request,reqid):
	reqid = int(reqid)	
	requserobj = RequestedUsers.objects.get(id=reqid)
	role = Lookup.objects.get(category='role', code=requserobj.roleid).description
        
     #Validate user 
	Context =  Validate_user_existence(requserobj.email,requserobj.instituteid.institutename,requserobj.courseid.course,role,"veri_success")
     # If user already exists in requested users table
	#if Context:
            #return render_to_response('home.html',Context,context_instance=RequestContext(request))
        
     #Update status to requested
	reqobj = RequestedUsers.objects.get(id=reqid)
        print "hello",reqobj.status
	if reqobj.status == 'Pending':
		print "verification"
		RequestedUsers.objects.filter(id=reqid).update(status="Requested")
		fname = reqobj.firstname
		     # send mail to him regarding his request
		send_email(3,reqid,reqid)
		     #Send email its higher authorities.
		print reqid, "request"
		emailto_higherauthorities(reqid)
     	
		head_message = "<h>Registration Initiated</h><br><br> Dear %s <br><br> You have initiated registration on IIT Bombayx Partners Portal <br><br> Please verify your email address by clicking the VERIFICATION LINK mailed to you. If you don't get the verification email <a href='resend_verification_mail/%d/%d/>CLICK HERE.</a> <br><br> After verification, an approval email will be sent to your institute registered Program Coordinator.!"% (fname,1,reqid)
            
        	Context={'head_message':head_message}
	return render_to_response('home.html',Context,context_instance=RequestContext(request))
 

   
def requestregister(request):
    if request.method == 'POST':
        email = request.POST.get('email','')
	#if user has already sent a request but not yet registered. i.e pending state
        
        state = request.POST.get('state','')
        institute = request.POST.get('Institute','')
        rcid = request.POST.get('rcid','')
        first_name = request.POST.get('fname','')
        last_name = request.POST.get('lname','')
        email = request.POST.get('email','')
        course = request.POST.get('Course','')
        role = request.POST.get('role','')
        desg = request.POST.get('Desg','')
    
	Context = Validate_user_existence(email, institute, course, role,"Request")
        
        if Context:
	    print Context
            return render_to_response('home.html',Context,context_instance=RequestContext(request))
        
        #else enter data into database
	
        insobj=T10KT_Institute.objects.filter(institutename=institute)
        instituteid = insobj[0].instituteid

        rcobj = T10KT_Remotecenter.objects.filter(instituteid_id=instituteid)
        rcid = rcobj[0].remotecenterid
        
        stateobj = T10KT_State.objects.filter(state=state)
        stid = stateobj[0].id
        
        courseobj = edxcourses.objects.filter(course=course)
        courseid = courseobj[0].id
             
        lookupobj = Lookup.objects.filter(description=desg) 
        desigid = lookupobj[0].code
                
        lookobj = Lookup.objects.filter(description=role)
        roleid=lookobj[0].code
       
        interface_obj = RequestedUsers(createdon="0001-01-01",updatedon="0001-01-01",roleid=roleid,state=state,instituteid_id=instituteid,remotecenterid_id=rcid,firstname=first_name,lastname=last_name,email=email,courseid_id=courseid,designation=desigid,status="Pending") 
        interface_obj.save()
       	
        # Fetch RequestedUsers ID from the table
        requserobj = RequestedUsers.objects.filter(email=email)
        reqid=requserobj[0].id
      
        #RequestedUsers.objects.filter(id=reqid).update(status="Verification Pending")
               
        args = {}
        args.update(csrf(request))
  
        #"send him to verification page"
        head_message="Title: Registration Initiated!<br><br> Dear %s , <br><br> You have initiated registration on IIT Bombayx Partners Portal <br><br>Please verify your email address by clicking the VERIFICATION LINK mailed to you. If you don't get the verification email <a href="">CLICK HERE<a> <br><br>After verification, an approval email will be sent to your institute registered Program Coordinator.!!!</html>" % first_name
        #This link will be of a request_success page
        #From click here one more email will go similarly
        	
        Context={'head_message':head_message}
        
        # Send the user verification email
        send_email(1,reqid,reqid)
        return render_to_response('home.html',Context,context_instance=RequestContext(request))
        
                
    ''' GET METHOD '''
    #ALl states in list
    
    stateobj = T10KT_State.objects.values('state')
    states=[]
    for row in stateobj:
        states.append(row['state'])
    
 
    #All approved institute names in list 
    institute_list=[]
    appinsobj=T10KT_Approvedinstitute.objects.all()
    
    for row in appinsobj:
	if row.instituteid_id :# if institute has approved then only fetch its institutes name
        	institute_list.append(row.instituteid.institutename)     
    institute_list.sort()
     

    #All courses from edxcourses in list      
    courseobj = edxcourses.objects.values('course')
    courses=[]
    for row in courseobj:
        courses.append(row['course'])
    

    # Designations list
    designations=[]
    lookupobj=Lookup.objects.filter(category="Designation")
    for row in lookupobj:
        designations.append(row.description)        
    

    Context = {'state_list' : states  , 'institute_list':institute_list , 'course_list' :courses , 'desg_list' : designations}

    args = {}
    args.update(csrf(request))
    return render_to_response("registration/requestregistration.html",Context, context_instance=RequestContext(request))


def resend_verification_mail(request,ec_id,pk):
    ec_id = int(ec_id)
    pk = int(pk)        
    send_email(ec_id, pk,pk)
    args = {}
    args.update(csrf(request))
    fname = RequestedUsers.objects.get(id = pk).firstname
    #"send him to verification page"
    head_message="Title: Verification Email Resend!<br/><br/><br/><br/> Dear %s ,<br/><br/>An Email has been send to you.<br/><br/>Please verify your email address by clicking the VERIFICATION LINK mailed to you. <br/>If you don't get the verification email <a href='/resend_verification_mail/%d/%d'>CLICK HERE</a> <br/><br/>After verification, an approval email will be send to your institute registered Program Coordinator.!!!" % (fname,ec_id,pk)
	#This link will be of a request_success page
	#From click here one more email will go similarly
    Context={'head_message':head_message}

    ''' email content table id to be fetched '''
    #emailcontentid = fetch id from content table where systype="Registration",page="Request_registration"

    return render_to_response('home.html',Context,context_instance=RequestContext(request))    
        




###########################################################################################################

######################################## End of Registration ###########################################################




############## Login by Ketaki###################################

@csrf_protect

def loginn(request):
    
    page = 'Login'
    module = 'Registration'
    args = {}
    args.update(csrf(request))

    if request.method == 'POST':
        
	
        loginlist = validate_login(request)
        
        if (loginlist!=-1):      
            args['email']=loginlist[0]
            args['institutename']=loginlist[1]            
            args['firstname']=loginlist[2]
            
            args['lastname']=loginlist[3]

            return ccourse(request)
        else:
            error_message=retrieve_error_message(module,page,'LN_INV')
            args = {}
            args.update(csrf(request))
            args['error_message']=error_message
            return render_to_response('login/tologin.html',args)            

            #return HttpResponseRedirect('/login_success/')
           
    return render_to_response('login/tologin.html',args)
           
   
def forgot_pass(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        email = request.POST['email']
        per_id= validate_email(email)
        print "forgot ", per_id
        ## If valid email id, then a mail is sent to his email alongwith a link to reset his password

	if per_id != -1:
		args['message']= "We've mailed you the instructions"
		ec_id = EmailContent.objects.get(systype='Login', name='resetpass').id	
		send_email(ec_id, per_id, per_id)
		return render_to_response('login/forgot_pass.html',args)                
            #return HttpResponseRedirect('/homepage/')
        else:
            args['message']="Unregistered email"
            return render_to_response('login/forgot_pass.html',args)                
    return render_to_response('login/forgot_pass.html',args)
    


def login_success(request):
    #context = RequestContext(request)
     args = {}
     args.update(csrf(request)) 
     insti_obj = T10KT_Institute.objects.get(instituteid=request.session['institute_id'])
     args['insti_obj'] = insti_obj
     person_obj = Personinformation.objects.get(id=request.session['person_id'])	
     args['person_obj'] = person_obj
    #args['fname'] = request.session['fname']
    #args['lname'] = request.session['lname']
     return render_to_response('login/login_success.html',args)

def change_pass(request):
    if request.method == 'POST':
        oldpwd = request.POST.get('old_password','')
        pwd1 = request.POST.get('new_password1','')
        pwd2 = request.POST.get('new_password2','')
        flag = password_change(oldpwd,request.session['person_id'])
        if flag == 0:
            args = {}
            args.update(csrf(request))
            args['message']= "Your old password didn't match. Please enter again!!"
            return render_to_response('login/changepass.html',args)
        if pwd1!=pwd2:
            args = {}
            args.update(csrf(request))
            args['message']= "Password didn't match. Please enter again!!"
            return render_to_response('login/changepass.html',args)
        else:
            password_reset(request.session['person_id'],pwd1)
            args = {}
            args.update(csrf(request))
            return render_to_response('login/change_pwdsuccess.html',args)
            
    args = {}
    args.update(csrf(request))
    return render_to_response('login/changepass.html',args)
        
    
def home(request):
    args = {}
    args.update(csrf(request))
   # a=courseenrollment.objects.filter(status='1', instituteid=request.session['institute_id'])
    #p=[]
    #for i in a:
#	p.append(edxcourses.objects.get(courseid=i.courseid))
 #   args['courselist'] = p
  #  x=Personinformation.objects.get(email=request.session['email_id'])
   # args['firstname']=x.firstname
    #args['lastname']=x.lastname
    #args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    #args['roleid']=Institutelevelusers.objects.get(personid=request.session['person_id']).roleid
    return ccourse(request)
    #return render_to_response('login/home.html',args)


def resetpass(request,emailid):
    per_id = emailid

    if request.method == 'POST':
        args = {}
        args.update(csrf(request))
        pwd1 = request.POST.get('new_password1','')
        pwd2 = request.POST.get('new_password2','')
        if pwd1!=pwd2:
            args = {}
            args.update(csrf(request))
            args['message']= "Password didn't match. Please enter again!!"
            return render_to_response('login/resetpass.html',args)
        else:
            password_reset(emailid,pwd1)
            args = {}
            args.update(csrf(request))
            args['message']= "Password changed successfully!!!"
	    ec_id = EmailContent.objects.get(systype='Login', name='success').id
	    send_email(ec_id, per_id, per_id)
            return render_to_response('login/home.html',args)            
    args = {}
    args.update(csrf(request))
    return render_to_response('login/resetpass.html',args)
    

    
def logout(request):
    logout_obj = Userlogin.objects.get(email=request.session['email_id'])
    logout_obj.loginstatus='False'
    logout_obj.save()
    del request.session['person_id']
    del request.session['role_id']
    del request.session['email_id']
    del request.session['institute_id']
    
    args = {}
    args.update(csrf(request))
    return HttpResponseRedirect('/')





####################End Ketaki module############################
###############################################################################################################


"""def multinstrole(request):
    args = {}
    args.update(csrf(request))
    mperson=Institutelevelusers.objects.filter(personid__id=request.session['person_id'])
    for i in mperson:
        print i.roleid
        muin.append([i.instituteid.id,i.instituteid.institute.institutename])
    return render_to_response('muitrole.html',args)"""

#################	Apoorva		Agrawal		########################################################
################################################################################################################


#################	Apoorva		Agrawal		########################################################
################################################################################################################

### Cancel Function ###

def cancel(request, req_pid):
	
	try:
		req_user = RequestedUsers.objects.get(id = req_pid)

		if req_user.status == 'Invited':
			req_user.status='Cancelled'
			req_user.save()

			print "The invitation has been caneled : %s" % req_user

		return redirect('dash')
	except:
		return HttpResponse('Invalid Request')


### Remove Course Level Users from Dashboard ###

def removeCLU(request, clu_pid):
	try :
		print "Inside the remove function"
		clu = Courselevelusers.objects.get(id = clu_pid)
		print "Found the CLU object"
		clu.enddate = date.today()
		print "The End"
		clu.save()
		print "The Person purged from the db permanently"

		return redirect('dash')
	except:
		return HttpResponse('Invalid Request')



### Approve Function ###

def approve(request, req_pid):
	
	try:
		req_user = RequestedUsers.objects.get(id = req_pid)

		if req_user.status == 'Requested':
			req_user.status='Approved'
			req_user.save()

			link = '/register/%s' % req_pid
			print link ,"sent"

		return redirect('dash')
	except:
		return HttpResponse('Invalid Request')


### Reject Function ###

def reject(request, req_id):
	try:
		req_user = RequestedUsers.objects.get(id = req_pid)

		if req_user.status == 'Requested':
			req_user.status='Rejected'
			req_user.save()

			link = '/register/%s' % req_pid
			print link ,"sent"

		return redirect('dash')
	except:
		return HttpResponse('Invalid Request')

### Dissent Function ###
	
def dissent(request, req_id):
	try:
		req_user = RequestedUsers.objects.get(id = req_pid)

		if req_user.status == 'Pending Consent':
			req_user.status='Declined'
			req_user.save()

			link = '/register/%s' % req_pid
			print link ,"sent"

		return redirect('dash')
	except:
		return HttpResponse('Invalid Request')


### Consent Function ###

def consent(request, req_pid):
       
		req_user = RequestedUsers.objects.get(id = req_pid)

		print req_user.id
		print req_user.status

		if req_user.status == 'Pending Consent':
			print "Hello"			
			print req_user.email
			person = Personinformation.objects.get(email = req_user.email)

			print person
			print req_user.roleid

			if req_user.roleid == 3:
				ilu = Institutelevelusers(instituteid_instituteid = req_user.instituteid, personid = person, roleid = req_user.roleid, startdate = date.today(), enddate="4712-12-31")
				ilu.save()
				req_user.delete()
			else:
				print req_user
		
				clu = Courselevelusers(instituteid = req_user.instituteid, personid = person, courseid = req_user.courseid, roleid = req_user.roleid, startdate = date.today(), enddate="4712-12-31")
				
				print clu
				clu.save()
				print clu
				
				print "User Inserted"
				req_user.delete()
		

		return redirect('dash')
	
	

def pendingConsent(requser):
	print "The consent link has been sent to the concerned person"
	return 0


### Dashboard Function ###


def dash(request):
	viewer_pid = request.session['person_id']
	viewer_obj = Personinformation.objects.get(id = viewer_pid)
	role_id = int(request.session['role_id'])
	
	viewer_inst = T10KT_Institute.objects.get(instituteid=request.session['institute_id'])
	
	args = {}

	try:
		consent = RequestedUsers.objects.filter(instituteid = viewer_inst, email = viewer_obj.email, status = 'Pending Consent')
		args['consent'] = consent
		error = []
	except:
		error = []

	if role_id <= 3:
		data = RequestedUsers.objects.filter(instituteid = viewer_inst).exclude(status='Requested').exclude(roleid=3).order_by('roleid')
		pend_req = RequestedUsers.objects.filter(instituteid = viewer_inst, status='Requested').order_by('roleid')
		
		teammembersclu = Courselevelusers.objects.filter(instituteid = viewer_inst, enddate__gt = date.today()).order_by('courseid')
		clu_past = Courselevelusers.objects.filter(instituteid = viewer_inst, enddate__lte = date.today())
	else:
		team_viewer = Courselevelusers.objects.get(instituteid = viewer_inst, personid = viewer_obj, roleid = role_id)
		teammembersclu = Courselevelusers.objects.filter(instituteid = viewer_inst, courseid=team_viewer.courseid, enddate__gt = date.today()).order_by('courseid')
		data = RequestedUsers.objects.filter(instituteid = viewer_inst, courseid = team_viewer.courseid).exclude(status='Requested', roleid=4)
		pend_req = RequestedUsers.objects.filter(instituteid = viewer_inst, status='Requested', courseid = team_viewer.courseid, roleid=4)
		clu_past = Courselevelusers.objects.filter(instituteid = viewer_inst, courseid = team_viewer.courseid, enddate__lte = date.today())


	if pend_req.count() == 0:
		args['requests'] = '0'
	else:
		args['requests'] = '1'

	
	
	try:
		pc = Institutelevelusers.objects.get(instituteid = viewer_inst, roleid=3, enddate__gt = date.today())
		args['pc_ilu'] = pc
		args['pc'] = '1'
	except:
		try:
			args['pc_ilu'] = RequestedUsers.objects.get(instituteid = viewer_inst, roleid=3, status='Invited')
			args['pc_msg'] = 'You Have Invited the above person to be your Program Coordinator. However he has yet to fill the form for the same'
			args['pc'] = '2'
		except:
			args['pc_msg'] = 'You Institute has not chosen a Program Coordinator yet'
			args['pc'] = '0'
	
	hoi = Institutelevelusers.objects.get(instituteid = viewer_inst, roleid=2, enddate__gt = date.today())

	args['viewer'] = viewer_obj
	args['role_id'] = role_id
	args['team'] = teammembersclu
	args['hoi_ilu'] = hoi
	args['requser'] = data
	args['pend_req'] = pend_req
	args['institutename'] = viewer_inst.institutename
	args['clu_past'] = clu_past

	args.update(csrf(request))

	return render_to_response('team/dash.html', args)


###################################################################################################################


#The Invite Function 



def invite(request):
	hoi_pid = request.session['person_id']
	hoi_obj = Personinformation.objects.get(id = hoi_pid)
	
	hoi_inst = T10KT_Institute.objects.get(instituteid=request.session['institute_id'])
	role_id = int(request.session['role_id'])
				
	error = []
	if request.method == 'POST':
		getrole = int(request.POST.get('role',''))
		getemail = request.POST.get('email', '')
		getfirstname = request.POST.get('firstname', '')
		getlastname = request.POST.get('lastname', '')
		getcourse = request.POST.get('edxcourse', '')
		secret = request.POST.get('secret', '')
		
		
		args = {'error_message': error,'firstname': getfirstname, 'lastname' : getlastname, 'email' : getemail, 'hoi_pid' : hoi_pid, 'hoi':hoi_obj, 'role_id':role_id, 'institutename': hoi_inst.institutename, 'courses' :edxcourses.objects.all() } 

		args.update(csrf(request))
		
		
		if not getrole:
			error.append(ErrorContent.objects.get(errorcode = 'role').error_message)
			return render_to_response('team/invite.html', args)
	
		if not getcourse:
			error.append('Select Appropriate Course')
			return render_to_response('team/invite.html', args)


		if not validateEmail(getemail):
			args['email'] = ''
			error.append(ErrorContent.objects.get(errorcode = 'email').error_message)
			return render_to_response('team/invite.html', args)

		if not getfirstname:
			error.append(ErrorContent.objects.get(errorcode = 'firstname').error_message)
			return render_to_response('team/invite.html', args)
	
		if not getlastname:
			error.append(ErrorContent.objects.get(errorcode = 'lastname').error_message)
			return render_to_response('team/invite.html', args)
				
		rc_obj = T10KT_Remotecenter.objects.get(instituteid = hoi_inst)
		course_obj = edxcourses.objects.get(courseid=getcourse)

		obj=Personinformation.objects.get(email=hoi_obj.email)

		if getrole == 4:
			try:	
					
				Courselevelusers.objects.get(instituteid=hoi_inst, courseid = course_obj, roleid = getrole, enddate__gt = date.today())
					
				error.append("The Course Coordinator for the Selected Subject is Still Active. If you wish to appoint another kindly deactivate him / her from your dashboard")
					
				return render_to_response('team/invite.html', args)
			except:
				pass

		if not secret:
			try:
				person = Personinformation.objects.get(email = getemail)
				
				try:
					ilu = Institutelevelusers.objects.filter(personid=person, instituteid=hoi_inst)#, enddate__gt = date.today())
					args['ilu'] = ilu
					
					try:
						clu = Courselevelusers.objects.filter(personid=person, instituteid=hoi_inst)#, enddate__gt = date.today())
						args['clu'] = clu
						return render_to_response('team/invite.html', args)
					except:
						return render_to_response('team/invite.html', args)
				except:
					try:
						clu = Courselevelusers.objects.filter(personid=person, instituteid=hoi_inst)#, enddate__gt = date.today())
						args['clu'] = clu
		
						return render_to_response('team/invite.html', args)
					except:
						error.append(ErrorContent.objects.get(errorcode = 'regemail').error_message)
						return render_to_response('team/invite.html', args)
			except:
				
				requser = RequestedUsers(courseid=course_obj, state=rc_obj.state, instituteid = hoi_inst, remotecenterid=rc_obj, firstname=getfirstname, lastname=getlastname, email=getemail, roleid=getrole, designation=2, status='Invited', createdon=date.today(), createdby=obj, updatedon=date.today(), updatedby=obj)

				requser.save()

				return redirect('dash')
		else:
		
			requser = RequestedUsers(courseid=course_obj, state=rc_obj.state, instituteid = hoi_inst, remotecenterid=rc_obj, firstname=getfirstname, lastname=getlastname, email=getemail, roleid=getrole, designation=2, status='Pending Consent', createdon=date.today(), createdby=obj, updatedon=date.today(), updatedby=obj)

			requser.save()

			pendingConsent(requser)

			return redirect('dash')

	args = {}
	args['role_id'] = role_id
	args['hoi'] = hoi_obj
	args['institutename'] = hoi_inst.institutename
	args['courses'] = edxcourses.objects.all()
	args.update(csrf(request))
	return render_to_response('team/invite.html', args)
#########################################################################################################################################################
###############		Program Coordinator Delegation Page 	#########################################################################

@transaction.atomic
def pc(request):				
	hoi_pid = request.session['person_id']
	hoi_obj = Personinformation.objects.get(id = hoi_pid)
	
	hoi_inst = T10KT_Institute.objects.get(instituteid=request.session['institute_id'])
	
	#ilu_obj = Institutelevelusers.objects.get(personid = hoi_obj, enddate__gt = date.today())
	role_id = int(request.session['role_id'])
	
	error = []
	if request.method == 'POST':
		getemail = request.POST.get('email', '')
		getfirstname = request.POST.get('firstname', '')
		getlastname = request.POST.get('lastname', '')
		secret = request.POST.get('secret', '')
		
		args = {'error_message': error,'firstname': getfirstname, 'lastname' : getlastname, 'email' : getemail, 'hoi_pid' : hoi_pid, 'hoi':hoi_obj, 'role_id':role_id, 'institutename':hoi_inst.institutename } 

		args.update(csrf(request))
		
		
		if not validateEmail(getemail):
			args['email'] = ''
			error.append(ErrorContent.objects.get(errorcode = 'email').error_message)
			return render_to_response('team/programcoordinator.html', args)

		if not getfirstname:
			error.append(ErrorContent.objects.get(errorcode = 'firstname').error_message)
			return render_to_response('team/programcoordinator.html', args)
	
		if not getlastname:
			error.append(ErrorContent.objects.get(errorcode = 'lastname').error_message)
			return render_to_response('team/programcoordinator.html', args)

		try:
			del_req = RequestedUsers.objects.get(instituteid = hoi_inst, roleid = 3)
			del_req.delete()
		
			pc = Institutelevelusers.objects.get(instituteid = hoi_inst, roleid=3, enddate__gt = date.today())
			pc.enddate = date.today()
			pc.save()

			rc_obj = T10KT_Remotecenter.objects.get(instituteid = hoi_inst)
		except:
			try:
				pc = Institutelevelusers.objects.get(instituteid = hoi_inst, roleid=3, enddate__gt = date.today())
				pc.enddate = date.today()
				pc.save()
				
				rc_obj = T10KT_Remotecenter.objects.get(instituteid = hoi_inst)
			except:
				rc_obj = T10KT_Remotecenter.objects.get(instituteid = hoi_inst)

		if not secret:
			try:
				person = Personinformation.objects.get(email = getemail)
				print "Got the person information"
				
				try:
					ilu = Institutelevelusers.objects.filter(personid=person, instituteid=hoi_inst)#, enddate__gt = date.today())
					args['ilu'] = ilu
					
					try:
						clu = Courselevelusers.objects.filter(personid=person, instituteid=hoi_inst)#, enddate__gt = date.today())
						args['clu'] = clu
						return render_to_response('team/programcoordinator.html', args)
					except:
						return render_to_response('team/programcoordinator.html', args)
				except:
					try:
						clu = Courselevelusers.objects.filter(personid=person, instituteid=hoi_inst)#, enddate__gt = date.today())
						args['clu'] = clu
						return render_to_response('team/programcoordinator.html', args)
					except:
						error.append(ErrorContent.objects.get(errorcode = 'regemail').error_message)
						return render_to_response('team/programcoordinator.html', args)
			except:

				requser = RequestedUsers(state=rc_obj.state, instituteid = hoi_inst, remotecenterid=rc_obj, firstname=getfirstname, lastname=getlastname, email=getemail, roleid=3, designation=2, status='Invited', createdon=date.today(), createdby=hoi_obj, updatedon=date.today(), updatedby=hoi_obj)

				requser.save()
				ec_id = EmailContent.objects.get(systype='TM_MGMT', name='register').id
				req_id = RequestedUsers.objects.get(email = getemail).id
				send_email(ec_id, req_id, req_id)
				args = {}
				args.update(csrf(request))

				return redirect('dash')
		else:
			requser = RequestedUsers(state=rc_obj.state, instituteid = hoi_inst, remotecenterid=rc_obj, firstname=getfirstname, lastname=getlastname, email=getemail, roleid=3, designation=2, status='Pending Consent', createdon=date.today(), createdby=hoi_obj, updatedon=date.today(), updatedby=hoi_obj)

			requser.save()
			
			pendingConsent(requser)				# function to send a consent mail 		

			args = {}
			args.update(csrf(request))

			return redirect('dash')



	args = {}
	args['role_id'] = role_id
	args['hoi'] = hoi_obj
	args['institutename'] = hoi_inst.institutename
	args.update(csrf(request))
	return render_to_response('team/programcoordinator.html', args)

##################################################################################################################################################################
###################################### Apoorva Code End #####################################################################







########################################### Course management ######################################################################

#for enrollment for a course
def enrollfinal(request,course,years):
	errors = []	
	if request.method=='POST':
		args = {}
		args.update(csrf(request))
		args['errors'] = errors
		args['coursename'] = request.POST.get('coursename','')
		args['startdate'] = request.POST.get('startdate','')
		args['enddate'] = request.POST.get('enddate','')
		if request.POST.get('total_moocs_students'):
			args['total_moocs_students'] = int(request.POST.get('total_moocs_students',''))
		else:
			args['total_moocs_students'] =request.POST.get('total_moocs_students','')
		if request.POST.get('total_course_students'):
			args['total_course_students'] = int(request.POST.get('total_course_students',''))
		else:
			args['total_course_students'] =request.POST.get('total_course_students','')
		args['program'] = request.POST.get('program','')
		args['year'] = request.POST.get('year','')
		args['comments'] = request.POST.get('comments','')
		enrollformvalidation(args)		
		if not args['errors']:
			ccname=args['coursename']
			start=args['startdate']
			end=args['enddate']
			prog=args['program']
			year=args['year']
			total_moocs_students=args['total_moocs_students']
			total_course_students=args['total_course_students']
			comment=args['comments']
			enroll_course=courseenrollment(corresponding_course_name=ccname, start_date=start, end_date=end, program=prog, year=year, total_moocs_students=total_moocs_students, total_course_students=total_course_students, status="1", comments=comment,  courseid_id="IITBombayX/"+course+"/"+years, instituteid_id = request.session['institute_id'],enrolledby_id=request.session['person_id'],enrollment_date=date.today())
                        enroll_course.save()
                        args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
			args['coursename']=edxcourses.objects.get(courseid="IITBombayX/"+course+"/"+years).coursename
			args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
	                return enrolled(request,course)
		else:
			return render(request,'course/enrollfinal2.html', args)
	args = {}
	args.update(csrf(request))
	args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
	args['course']=course
	args['coursename']=edxcourses.objects.get(courseid="IITBombayX/"+course+"/"+years).coursename
	args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
	return render(request,'course/enrollfinal2.html', args)

##############################################################################################################################################

#for cancelling a course
def unenroll(request,course,year):
	errors=[]
	args = {}
	args.update(csrf(request))
	args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
        args['course']=course
	args['coursename']=edxcourses.objects.get(courseid="IITBombayX/"+course+"/"+year).coursename
	args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
	if request.method=='POST':
		args['reason']=request.POST.get('reason','')
		args['errors'] = errors
		unenrollvalidation(args)
		if not args['errors']:
			enrolled_course=courseenrollment.objects.get(courseid_id="IITBombayX/"+course+"/"+year,status=1,instituteid_id=request.session['institute_id'])
			enrolled_course.reason_of_cancellation=args['reason']
			enrolled_course.status=0
			enrolled_course.cancelled_date=date.today()
			enrolled_course.cancelledby_id=request.session['person_id']
                        enrolled_course.save()
			return unenrolled(request,args)
		else:
			return render(request,'course/unenroll.html', args)
				
	return render(request,'course/unenroll.html', args)

#when a course is enrolled
def enrolled(request,course):
	args = {}
	args.update(csrf(request))
        
	args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
	args['coursename']=course
        
	args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
        
	return render(request,'course/enrolled.html', args)

#when a course is unenrolled
def unenrolled(request,args):
	return render(request,'course/unenrolled.html', args)

#current enrolled courses
def ccourse(request):
	args = {}
	args.update(csrf(request))
        viewer_obj=Personinformation.objects.get(id = request.session['person_id'])
        args['roleid']=request.session['role_id']
	if args['roleid']==4:
		return HttpResponseRedirect('/coordinatorhome/')
	if args['roleid']==5:
		return HttpResponseRedirect('/teacherhome/')
        args['viewer'] = viewer_obj.id
	enrolled_courses=courseenrollment.objects.filter(status=1, instituteid=request.session['institute_id'])
	edx_enrolled_courses=[]
	for index in enrolled_courses:
		edx_enrolled_courses.append(edxcourses.objects.get(courseid=index.courseid.courseid))
	args['courselist'] = edx_enrolled_courses
	person=Personinformation.objects.get(email=request.session['email_id'])
	args['firstname']=person.firstname
	args['lastname']=person.lastname
	args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
	return render(request,'course/enrolledcoursesfinal.html', args)

#show all available courses
def allcourses(request):
	args = {}
	args.update(csrf(request))
	args['allcourses'] = edxcourses.objects.all()
	args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
	return render(request,'course/allcourses.html',args)

#update course information
def updatecourses(request,course,years):
	errors = []	
	if request.method=='POST':
		args = {}
		args.update(csrf(request))
		args['errors'] = errors
		args['coursename'] = request.POST.get('coursename','')
		args['startdate'] = request.POST.get('startdate','')
		args['enddate'] = request.POST.get('enddate','')
		args['total_moocs_students'] = request.POST.get('total_moocs_students','')
		args['total_course_students'] = request.POST.get('total_course_students','')
		args['program'] = request.POST.get('program','')
		args['year'] = request.POST.get('year','')
		args['comments'] = request.POST.get('comments','')
		enrollformvalidation(args)		
		if not args['errors']:
			ccname=args['coursename']
			start=args['startdate']
			end=args['enddate']
			prog=args['program']
			year=args['year']
			total_moocs_students=args['total_moocs_students']
			total_course_students=args['total_course_students']
			comment=args['comments']
			x=courseenrollment.objects.get(courseid__courseid="IITBombayX/"+course+"/"+years,instituteid__instituteid=request.session['institute_id'],status=1)
                        x.corresponding_course_name=ccname
			x.start_date=start
			x.end_date=end
			x.program=prog
			x.year=year
			x.total_moocs_students=total_moocs_students
			x.total_course_students=total_course_students
			x.enrolledby_id=request.session['person_id']
			x.comments=comment
			x.save()
			return updated(request,course,years)
		else:
			return render(request,'course/updatefinal.html', args)
	args = {}
	args.update(csrf(request))
	x=courseenrollment.objects.get(courseid_id="IITBombayX/"+course+"/"+years,instituteid=request.session['institute_id'],status=1)
	args['coursename'] = x.corresponding_course_name
	args['startdate'] = x.start_date
	args['enddate'] = x.end_date
	args['total_moocs_students'] = x.total_moocs_students
	args['total_course_students'] = x.total_course_students
	args['program'] = x.program
	args['year'] = x.year
	args['comments'] = x.comments
	args['coursename']=edxcourses.objects.get(courseid="IITBombayX/"+course+"/"+years).coursename
	args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
	return render(request,'course/updatefinal.html', args)

#when course information is updated
def updated(request,course,years):
	args={}
	args.update(csrf(request))
	args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
	courseid="IITBombayX/"+course+"/"+years
	course=courseenrollment.objects.get(courseid_id=courseid,instituteid=request.session['institute_id'],status=1)
	args['course']=course
	args['coursename']=edxcourses.objects.get(courseid=courseid).coursename
	args['ccourse']=edxcourses.objects.get(courseid=courseid).course
	args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
	return render(request,'course/updated.html',args)

#page for a particular page
def course(request,course,year):
	args = {}
	args.update(csrf(request))
	ccourseid="IITBombayX/"+course+"/"+year
	args['course']=edxcourses.objects.get(courseid=ccourseid)
	args['gradelist']=gradescriteria.objects.filter(courseid=ccourseid)
	for i in args['gradelist']:
		i.cutoffs*=100
	args['typelist']=gradepolicy.objects.filter(courseid=ccourseid)
	args['courseid']=ccourseid
	args['roleid']=int(Institutelevelusers.objects.get(personid=request.session['person_id']).roleid)
	args['enrolled']=args['closed']=args['open']=0
	eend=edxcourses.objects.get(courseid=ccourseid).enrollend
	today=datetime.now()
	eend=str(eend).split('+')[0]
	today=str(today).split('.')[0]
	print eend,"hello",today
	if eend < today:
		args['closed']=1
	courses=courseenrollment.objects.filter(courseid=ccourseid,instituteid=request.session['institute_id'])
	for i in courses:
		if i.status==1:
			args['enrolled']=1
			break
	if eend >= today and args['enrolled']==0:
		args['open']=1
	return render(request,'course/enrollmentcourse.html', args)


##########################   course management End #######################################################









########################### Student management code ###################################################




#Function to show the teacher list of a particular course and institute.

def teacherlist(request):
	list = []
        for user in Personinformation.objects.raw("select distinct * from SIP_personinformation AS p JOIN SIP_courselevelusers as c WHERE c.courseid_id='CS101' AND c.instituteid_id = '%s'"%(request.session['institute_id'])+"AND c.personid_id='%s'"%(request.session['person_id'])):#update course id from button
		list.append(user.firstname)
        Context = {'list' :  list}
        return render_to_response("student/teacher.html",Context, context_instance=RequestContext(request))

#---------------------------------------#



#Function to show all the courses taken by a institute

def courselist(request):
    a=[]
    for obj in edxcourses.objects.raw("select * from SIP_edxcourses,SIP_courselevelusers where SIP_edxcourses.courseid = SIP_courselevelusers.courseid_id and SIP_courselevelusers.personid_id = '%s'"%(request.session['person_id'])):#from session
        a.append(obj.coursename)
    
    Context = {'courses_list' : a}
    

    return render_to_response("student/courses.html",Context,context_instance=RequestContext(request))
    
#------------------------------------#
    
 

#Function to display details all student for a particular institute, teacher and course


def studentdetails(request,course):
    #print course
    personid=request.session['person_id']
    students = studentDetails.objects.filter(teacherid=personid,courseid=course)
    data=[]
    for i in students:
	   print i.roll_no
           data.append([i.roll_no,i.userid.username,i.userid.email,i.id])
                #print data
    #a=course.split("/")[1] 
    data.sort()
    courseargs=course.split("/")[1]
    print courseargs
    context = {'info':data,'course':course,'courseargs':courseargs}
    #print data
    return render_to_response("student/test.html",context,RequestContext(request))

#-----------------------------------------#

#-----------------------------------------#

#Function to parse the sql query and return all the data in a list

def sql_select(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    list = []
    i = 0
    for row in results:
        dict = {} 
        field = 0
        while True:
           try:
                dict[cursor.description[field][0]] = str(results[i][field])
                field = field +1
           except IndexError as e:
                break
        i = i + 1
        list.append(dict) 
    return list  

#-------------------------------------------#


#Function to parse the html and make a download file in csv format

def downloadcsv(request,course):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_details.csv"'
    context=RequestContext(request)
    print "hwsafc"
    soup = BeautifulSoup(urlopen('http://10.105.22.21:9005/parse/'+course))
    print course
    division = soup.findAll('div',{ "class" : None })
    for d in division:
        table = d.findAll('table')
        for t in table:
            headers =[]
            headers.append([header.text.encode('utf8') for header in t.findAll('th')])
            rows = []
            for row in t.findAll('tr'):
                rows.append([val.text.encode('utf8') for val in row.findAll('td')])
                with open('student_details.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerows(headers)
                    writer.writerows(row for row in rows if row)
        writer = csv.writer(response)
        with open('/home/tushar/Desktop/student_details.csv', 'rb') as csvfile:#update path to save csv file
            filereader = csv.reader(csvfile, delimiter=',')
            for row in filereader:
                writer.writerow(row)
        return response

    return HttpResponse('')
    #return response


#---------------------------------#


#Function to provide facility to change roll_no of student

def Update(request,pid,course):
    print course
    
    #args = {}
    #args.update(csrf(request))
    if request.method == 'POST':
        
        studentDetails.objects.filter(userid__username = request.POST['username']).update(roll_no = request.POST['roll_no'])
        return HttpResponseRedirect('/parse/'+'IITBombayX/'+course+"/2015-16")
    else:
        
        student = studentDetails.objects.get(id=pid)
        args = {}
        args.update(csrf(request))
        args['info']=student
        args['course']=course
        args['pid']=pid
        args['a']=pid
        return render_to_response("student/update.html",args)
    

#---------------------------------# 
         

#Function for bulk move of students from one teacher to another  (For higher authority accept teacher)
def movestudents(request):
    args = {}
    args.update(csrf(request))
    form = UploadForms()
    args['form'] = formlist1
    teacherlist = Courselevelusers.objects.filter(instituteid = request.session['institute_id']).filter(roleid = 5)#give one more filter for course
    args['info'] = teacherlist
   
    return render_to_response('student/bulkremovefirstpage.html',args)

#-------------------------------------#

        
#-------------------------------------------#
#this function is used to output a csv file #
#-------------------------------------------#
#-------------------------------------------#
     

def upload(request,code):
    
    if request.POST:
        form = UploadForms(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles where uploadedby_id = 1 ORDER BY id DESC LIMIT 1 '):
                #print "file"
                fname = str(p.filename)
	    uploadedfiles.objects.filter(filename = fname).update(uploadedby = request.session['person_id'])	
            extension = validate_file_extension(fname)
            if(extension):
		#print request.POST['teacher_id']
                if int(request.session['role_id'])==4:
                    context = parse(request,False,request.POST['teacher_id'],fname)     # 'parse' function is defined in validations.py
                    return render(request, 'student/uploaded.html', context)
                elif int(request.session['role_id'])==5:
                    #print "inelif"
                    context = parse(request,True,False,fname)     # 'parse' function is defined in validations.py                
                    return render(request, 'student/uploaded.html', context)
            else:
                message = " !!! Please Upload .csv File!!!"
                form = UploadForms()
                args = {}
                args.update(csrf(request))
    
                args['form'] = form
                args['message'] = message
                return render_to_response('student/upload.html', args)
           
    else:
        form = UploadForms()
        
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('student/upload.html', args)
        
#---------------------------------------------------------
def output_csv(request,code):
   
    for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles ORDER BY id DESC LIMIT 1 '):
        fname = str(p.filename)    
    	
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
#---------------------
    if(code=="1"):
        response['Content-Disposition'] = 'attachment; filename="valid_records.csv"'

        #print filename
        writer = csv.writer(response)
        csvdata = student_interface.objects.filter(errorcode__errorcode = "noerror",fileid__filename = fname)  
        #csvdata = Errorincsv.objects.all()	
        writer.writerow(["Record No","Roll No", "Username","Email-ID"])
        for row in csvdata:
            writer.writerow([row.recordno,row.roll_no, row.username, row.email])
#---------------------
    elif(code=="2"):
        response['Content-Disposition'] = 'attachment; filename="invalid_records.csv"'
        print code
        #print filename
        writer = csv.writer(response)
        csvdata = student_interface.objects.filter(~Q(errorcode__errorcode = "noerror"),fileid__filename = fname)  
        #csvdata = Errorincsv.objects.all()	
        writer.writerow(["Record No","Roll No", "Username","Email-ID","Message"])
        for row in csvdata:
            writer.writerow([row.recordno,row.roll_no, row.username, row.email,row.errorcode.error_message])
        

    return response
	   
    	

#-------------------------------------------#
#-------------------------------------------#

 
    
def uploaded(request):
    t = get_template('student/uploaded.html')
    html = t.render(Context({}))
    return HttpResponse(html)


def Course_template(request):
    
    #courses = edxcourses.objects.values('courseid').distinct()
    a=[]
    #role_id=request.session['role_id']
    person = Courselevelusers.objects.filter(personid = request.session['person_id'])
    courses =  edxcourses.objects.all()
    for i in person:
         for course in courses:
             #print course.courseid,"hello",i.courseid.courseid
             if course.courseid == i.courseid.courseid:
                 a.append(course.courseid)
                 #print a
    Context = {'courses_list': a}
    return render_to_response("student/dasboard.html",Context, context_instance=RequestContext(request))


# Function to provide facility for unenrollment

def unenrollstudent(request,pid,courseid):
    print pid,courseid
    studentDetails.objects.filter(id = pid).filter(courseid = courseid).update(teacherid = 1)
    return HttpResponseRedirect('/parse/'+courseid)

#..........................................#
"""
def Print(request,row):
    #print row
    db = MySQLdb.connect("localhost","root","root","SIP_DATA")
    cursor = connection.cursor()
    sql="select SIP_iitbx_authuser.username,SIP_iitbx_authuser.email,SIP_studentdetails.roll_no from SIP_iitbx_authuser,SIP_studentdetails where SIP_studentdetails.userid_id = SIP_iitbx_authuser.id and SIP_iitbx_authuser.username = '%s'"%(row)
    
    data = sql_select(sql)
    db.close()
    context = {'info':data}
    print context
    return render_to_response("student/update.html",context,RequestContext(request))
"""    
################################################## End of student management module ########################################################



#######    performance module    #######
'''def warning(flag):
      if flag:
	  return True
      else:
	  args = {}
          args.update(csrf(request))
          args['form'] = form
          return render_to_response('performance/popup.html', args)'''

def storegrade(fname,course):
	fo=open(fname,'rb')    
    	reader = csv.reader(fo)
	count = 0
	for record in reader:
		if count:
			query = performance_interface(courseid=course,userid=record[0],email=record[1],username=record[2],grade=record[3])
			query.save()			
			lenq = len(record)
			while lenq > 4:
				quiz = "quiz"+str(lenq-4)
				marks = record[lenq-1]
				user_id = record[0]
				performance_interface.objects.filter(courseid=course,userid=user_id).update(**{quiz:marks})
				lenq = lenq - 1
		count = count + 1

def gradeupload(request):
    
    if request.POST:
        form = UploadForms(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles where uploadedby_id = 1 ORDER BY id DESC LIMIT 1 '):
                fname = str(p.filename)
            extension = validate_file_extension(fname)
            if(extension):
		course = request.POST['course']
		filetype = request.POST['filetype']
		if filetype=="performance":
			invalid = 0;
			fo=open(fname,'rb')    
    			reader = csv.reader(fo)
			count = 0;
			for record in reader:
				if count:
					userid = record[0]
					email = record[1]
					username = record[2]
					isvalid = validate(userid,username,email)
					if not isvalid:	
						invalid = invalid + 1
				count = count + 1 
			if invalid:
				message = "!!! "+str(invalid)+" Invalid Records Found !!!\n\t\t!!! Please Upload the correct Records !!!"
				form = UploadForms()
				args = {}
				args.update(csrf(request))
				args['form'] = form
				args['message'] = message
				return render_to_response('performance/gradeupload.html', args)
			else:
				'''obj = performance_interface.objects.filter(courseid=course)
				if obj:
					flag = warning(False)
				else:
					flag = True
				if flag:'''
				performance_interface.objects.filter(courseid=course).delete()
				storegrade(fname,course)
				result = "!!! GRADES UPLOADED !!!"
				form = UploadForms()
				args = {}
				args.update(csrf(request))
				args['form'] = form
				args['result'] = result
				return render_to_response('performance/gradeupload.html', args)
            else:
                message = " !!! Please Upload .csv File!!!"
                form = UploadForms()
                args = {}
                args.update(csrf(request))
    
                args['form'] = form
                args['message'] = message
                return render_to_response('performance/gradeupload.html', args)
           
    else:
        form = UploadForms()
        
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('performance/gradeupload.html', args)
##########
'''global cnx
cnx = MySQLdb.connect(user='root',passwd='root',host='10.105.22.21',db='SIP_DATA')
global x
x = cnx.cursor()'''

'''def report(request):
	personid = request.session['person_id']
	course=Courselevelusers.objects.get(personid=request.session['person_id']).courseid.courseid
        query = ("select * from SIP_performance_interface where userid in(select userid_id from SIP_studentdetails where teacherid_id=%d and courseid_id="%s",%(personid,course)) INTO OUTFILE '/tmp/cancel6.csv' FIELDS TERMINATED BY ';' ENCLOSED BY '"'LINES TERMINATED BY '\n';")
        x.execute(query)
        cnx.commit()'''

'''def downloadreport(request):
	person_id=1#request.session("person_id")
	course = "IITBombayX/CS101.1x/2015-16"#courselevelusers.objects.get(personid=person_id).courseid.courseid
	data = []
	for row in studentDetails.objects.filter(courseid=course,teacherid=person_id):
		data.append(performance_interface.objects.get(userid=row.userid_id))
	print data
	out = open('/home/kamal/Desktop/out.csv', 'w')
	for row in data:
		for key, value in row.__dict__.items():
			if value and (not key.startswith("__")):
				out.write('%s,' % value)		
		out.write('\n')
	out.close()'''
