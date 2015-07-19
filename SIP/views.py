from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core.mail import send_mail
from datetime import date,timedelta
from django.db import transaction
from django.contrib import auth
from django.template import Context
from django.core import signing
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.models import User
from SIP.models import Userlogin
from SIP.validations import retrieve_error_message,validate_login,validate_email
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import cache_control
from django.core.cache import cache
from .models import *
from .validations import *
from django.template.loader import get_template
from forms import UploadForms
from django.contrib import messages
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from django.conf.urls.static import static
from django.db.models import Q
from django.core.files import File
from SIP.models import *
import csv
import MySQLdb
from SIP.validations import *
from django.utils import timezone
import glob 
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
from globalss import *
from IITBOMBAYX_PARTNERS.settings import *
#############################end of import statements by student management#######################################
current=timezone.now
default_password="Welcome123"

########################views Starts from Here ###################################

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_multi_roles(request):    
    args={}
    try:
       person=Personinformation.objects.get(email=request.session['email_id'])
    except:
          args['message'] ="unique person for logged in  user does not exit"
          return render(request,'geterror.html',args)
    

    if request.POST:        
        
        institute_id = request.POST.get('institute_id')
        #print request.POST.get('institute_id')
        request.session['institute_id']=request.POST.get('institute_id')#institute id set
        rolelist,args= roleselect(request,institute_id,person,args)

        if len(rolelist)==1:
            return onerole(request,rolelist,args)
        args.update(csrf(request)) 
        return render(request,'rolepage1.html',args)
           
                 
    l=[]  
    request.session['person_id']=person.id#person id set   
   
    insti_obj=Institutelevelusers.objects.filter(personid=person.id).values("instituteid").distinct()
    
    
    for i in insti_obj:
        
        insti_x=T10KT_Institute.objects.filter(instituteid=i["instituteid"])
        x= insti_x[0].institutename
        l.append([i["instituteid"],x])

    insti_obj=Courselevelusers.objects.filter(personid=person.id).values("instituteid").distinct()
    
    for i in insti_obj:
        flag=True
        insti_x=T10KT_Institute.objects.filter(instituteid=i["instituteid"])
        x= insti_x[0].institutename
        for row in l:
                if row[0]==i["instituteid"]:
                        flag=False
        if flag:
                l.append([i["instituteid"],x])
  
    if len(l)==1:
       return oneinstitute(request,person)
    
        
    try:
       request.session['rcid']=T10KT_Approvedinstitute.objects.get(instituteid__instituteid=institute_id).remotecenterid.remotecenterid
    except:
       request.session['rcid']="   " 
    args={"l":l,'flag':True}
    args['firstname']=person.firstname
    args['lastname']=person.lastname
    args['email']=request.session['email_id'] 
    args['rcid']=request.session['rcid'] 
    args.update(csrf(request))
    
    return render(request,'rolepage1.html',args)    
        
##########return list of all roles of logged in peron in selected institute#####################
def roleselect(request,institute_id,person,args):
        rolelist=[]
        obj = Institutelevelusers.objects.filter(instituteid=institute_id).filter(personid=request.session['person_id']).values("roleid").distinct()
        for row in obj:
            obj=Lookup.objects.get(category='role', code=row['roleid'])
            
            rolelist.append([obj.comment,row['roleid'],0])

        cobj = Courselevelusers.objects.filter(instituteid__instituteid=institute_id).filter(personid=request.session['person_id'])
        for row in cobj:
            obj=Lookup.objects.get(category='role', code=row.roleid)
           # print row.courseid.id,row.roleid,obj.comment
            rolelist.append([obj.comment,row.roleid,row.courseid])       
        
        args['flag']=False
        args['rolelist']=rolelist  
        args['firstname']=person.firstname
        args['lastname']=person.lastname
        args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
        args['email']=request.session['email_id']
        
        return rolelist,args


###################Set institue directly in session if only one institute is present for logged in user#################
def oneinstitute(request,person):
    args={}
    if Institutelevelusers.objects.filter(personid=person.id).exists():
        institute_id=Institutelevelusers.objects.filter(personid=person.id)[0].instituteid.instituteid
    else:
        institute_id=Courselevelusers.objects.filter(personid=person.id)[0].instituteid.instituteid
    request.session['institute_id']=institute_id#institute id set
    try:
       request.session['rcid']=T10KT_Approvedinstitute.objects.get(instituteid__instituteid=institute_id).remotecenterid.remotecenterid
    
    except:
       request.session['rcid']="   "   
    #insti_x=T10KT_Institute.objects.filter(instituteid=institute_id)
    #x= insti_x[0].institutename
    args['rcid']=request.session['rcid']
    
    rolelist,args=roleselect(request,institute_id,person,args)
   
    if len(rolelist)==1:
            return onerole(request,rolelist,args)
    args.update(csrf(request)) 
    return render(request,'rolepage1.html',args)

############# set role directly in session if only one role is present for logged in user###################################
def onerole(request,rolelist,args):
    if rolelist[0][2]:
       args.update(csrf(request))
                    # print "role list",rolelist[0][2]
       return set_single_role(request,rolelist[0][1],rolelist[0][2].courseid,rolelist[0][2].id)        
    args.update(csrf(request))
    return set_single_role(request,rolelist[0][1],0,0)
    

######################set selected roles in session for logged in user###################################
def set_single_role(request,role,courseid,cid):
         
        request.session['role_id']=int(role)
        request.session['rolename']=Lookup.objects.get(category="Role",code=role).comment
        request.session['courseid']=courseid#role id set
        request.session['edxcourseid']=cid#role id set
        args=sessiondata(request)
        return ccourse(request)


#Return dictionary with default data of session institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid
def sessiondata(request):
    args = {}
    args.update(csrf(request))
    try:
       person=Personinformation.objects.get(email=request.session['email_id'])
       args['institute']=institute=T10KT_Institute.objects.get(instituteid=request.session['institute_id'])
       args['person']=person
    except:
          args['message'] ="Cannot fetch unique person or institute for this logged-in session "
          return render(request,'geterror.html',args)
    
    args['institutename']=institute.institutename
    args['firstname']=person.firstname
    args['lastname']=person.lastname
    args['email']=request.session['email_id']
    args['role_id']=int(request.session['role_id'])
    args['rolename']=request.session['rolename']
    args['rcid']=request.session['rcid']  
    args['courseid']= request.session['courseid']
    
    args['edxcourseid']=request.session['edxcourseid']
    return args             



###########On root url(home page) checking If session is active then redirect to institute  select page or blended admin home page based on usertypeid  Else redirect to login page ############################# 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sessionlogin(request):
            
    args = {}
    args.update(csrf(request)) 
    try:
            if request.session['email_id']:
               
               user = User.objects.get(email=request.session['email_id'])
               user_info=Userlogin.objects.get(user=user)
               
               if user_info.usertypeid==0:
                   
                   return HttpResponseRedirect("/blendedadmin_home/")
               else:
                   return HttpResponseRedirect("/get_multi_roles/")
            else:               
                return loginn(request)
    except:
                    
            return loginn(request)


###############checking credential of user and redirect to home page or login page ##########################
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def loginn(request):
    
    page = 'Login'
    module = 'Login'
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        args['email']= request.POST['email']
        args['error_message']=[]
        args = emailid_validate(request,args)
        if args['error_message']:
            return render_to_response('login/tologin.html',args)            
        loginlist = validate_login(request) 
## If the emailid exists, then call the page according to the role
        if (loginlist==1):      
            return HttpResponseRedirect("/get_multi_roles/")
## If the emailid does not exist,display error message
        elif (loginlist == 0):
             return HttpResponseRedirect("/blendedadmin_home/")
        elif (loginlist == 2):
             return HttpResponseRedirect("/bmchome")
        elif (loginlist == 3):
             return HttpResponseRedirect("/courseadminhome/")
        elif (loginlist == 4):
            error_message=retrieve_error_message(module,page,'LN_INV')##required to create error content message           
            args['error_message']=error_message
            return render_to_response('login/tologin.html',args)              

        else:
            error_message=retrieve_error_message(module,page,'LN_INV')            
            args['error_message']=error_message
            return render_to_response('login/tologin.html',args)            
    return render_to_response('login/tologin.html',args)
           
   
################### Send mail for generating link of new password on click of forget password ink ######################   
def forgot_pass(request):
    module = 'Login'
    page = 'Forgot_Pass'
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':        
        email = request.POST['email']
        per_id= validate_email(email)
## If valid email id, then a mail is sent to his email alongwith a link to reset his password 
        if per_id != -1:     
            args['message']= retrieve_error_message(module,page,'NO_ERR')
            try:
               ec_id = EmailContent.objects.get(systype='Login', name='resetpass').id
            except:
               args['message'] ="Email cannot send at this moment. "
               return render(request,'geterror.html',args)
           #print ec_id
            send_email(request,ec_id, per_id, per_id)
            return render_to_response('login/forgot_pass.html',args)      
                           
        else:
## If invalid email, displays an error message
            args['message']=retrieve_error_message(module,page,'EML_INV')
            return render_to_response('login/forgot_pass.html',args)        
    return render_to_response('login/forgot_pass.html',args)



#################### Check and Reset new password for user on request of forgot password ##########################
def resetpass(request,token):
    emailid = signer.unsign(token)
    per_id = emailid
     
    module = 'Login'
    page = 'Reset_Pass'
    args = {}
    args.update(csrf(request))

    if request.method == 'POST':

        args['password1']= password1=request.POST.get('new_password1','')
        args['password2']= password2=request.POST.get('new_password2','')
        args['message']=[]
        args = pwd_field_empty(request,args,'')
        if args['message']:
            return render_to_response('login/resetpass.html',args)

        if  len(password1)==0 or len(password2)==0 or password1 != password2:

            args['message']= retrieve_error_message(module,page,'NO_MTCH')
            return render_to_response('login/resetpass.html',args)
        else:
## If the two new passwords match, password is changed and a mail is sent to the user regarding the change
            try: 
                userid=Personinformation.objects.get(id=emailid)           
                user = User.objects.get(email=userid.email)
            except:
               args['message'] ="unique person for the user does not exist"
               return render(request,'geterror.html',args)
            user.set_password(password1)
            user.save()
            args['message']= retrieve_error_message(module,page,'PWD_SET')
            ec_id = EmailContent.objects.get(systype='Login', name='success').id
            send_email(request,ec_id, per_id, per_id)
            return render_to_response('login/change_pwdsuccess.html',args)            
  
    return render_to_response('login/resetpass.html',args)


#############Create password for user on registration by Python Registration scripts if status is 0 ########################

def createpass(request,personid):
    emailid = signer.unsign(personid)
    per_id = emailid
    module = 'Login'
    page = 'Reset_Pass'
    args = {}
    args.update(csrf(request))
    try:
       userid=Personinformation.objects.get(id=emailid)
       
       if Userlogin.objects.get(user=User.objects.get(email=userid.email)).status==False:   
		  

		     args['password1']=password1= request.POST.get('new_password1','')
		     args['password2']=password2= request.POST.get('new_password2','')
		     args['message']=[]
		     args = pwd_field_empty(request,args,'')
		     if args['message']:
		        return render_to_response('login/createpass.html',args)

		     if  len(password1)==0 or len(password2)==0 or password1 != password2:
		        args['message']= retrieve_error_message(module,page,'NO_MTCH')
		        return render_to_response('login/createpass.html',args)

		     else:  
	  ## If the two new passwords match, password is changed and a mail is sent to the user regarding the change 
		                 
		        userid=Personinformation.objects.get(id=emailid)           
		        user = User.objects.get(email=userid.email)           
		        user.set_password(password1)
		        user.save()
		        user_info=Userlogin.objects.get(user=user)
		        user_info.status=1
		        user_info.save()
		        args['message']= retrieve_error_message(module,page,'PWD_SET')
		        ec_id = EmailContent.objects.get(systype='Login', name='success').id
		        send_email(request,ec_id, per_id, per_id)
		        return render_to_response('login/create_pwdsuccess.html',args)            
	  
		  #return render_to_response('login/createpass.html',args)
       return  render_to_response('login/alreadycreated.html',args)

    except:
           args['message'] ="person  does not exist"
           return render(request,'geterror.html',args)



#################### Delete session and redirect to login page on logout click#######################################
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
    logout_obj = User.objects.get(email=request.session['email_id'])
   # logout_obj.loginstatus='False'
    logout_obj.save()
    try:
		del request.session['person_id']
		del request.session['email_id']
		del request.session['institute_id']
		request.session.flush()
		cache.clear()
		auth.logout(request)
		#return HttpResponseRedirect('/')
		response = redirect('/')
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		response.delete_cookie()
		return response
   
    except:
        return HttpResponseRedirect('/')



########################Set Home Page for different roles.For Head and Program Coordinator display list of courses enrolled by their

def ccourse(request):
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request)
    input_list={}
    
    input_list.update(args)
    input_list.update(csrf(request))
    input_list['roleid']=args['role_id']
        
    if input_list['roleid']==4:
		return HttpResponse('/coordinatorhome/')
    if input_list['roleid']==5:
		
		return HttpResponseRedirect('/teacher/')
    input_list['viewer'] = args['person'].id

    enrolled_courses=courseenrollment.objects.filter(status=1, instituteid__instituteid=request.session['institute_id'])

    edx_enrolled_courses=[]
    try:
       for index in enrolled_courses:
		  edx_enrolled_courses.append(edxcourses.objects.get(courseid=index.courseid.courseid))
    except:
           args['message'] ="cannot get unique entry for course"
           return render(request,'geterror.html',args)

    input_list['courselist'] = edx_enrolled_courses
    input_list['cid']=args['edxcourseid']
    return render(request,enrolled_course_, input_list)




################ Display list of Teacher's of  particular course and institute from Courselevelusers based on session #############################.

def teacherlist(request,courseid):
        # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
        args =sessiondata(request)
        args.update(csrf(request))
        teacherlist = []    
             
        users = Courselevelusers.objects.filter(instituteid__instituteid = request.session['institute_id'],roleid = 5).filter(courseid__courseid = courseid)
        for user in users:
                teacherlist.append(user)  
                args['coursename'] = user.courseid.coursename

        args['teacherlist'] = teacherlist
        args['courseid']=request.session['courseid'] = courseid
        args['course']=edxcourses.objects.get(courseid=courseid).course
        return render_to_response("student/teacher.html",args, context_instance=RequestContext(request))



def courselist(request):
    #args = {}
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request) 
    args.update(csrf(request))   
    obj = Courselevelusers.objects.filter(personid_id = request.session['person_id'],courseid__courseid = request.session['courseid'],instituteid__instituteid=request.session['institute_id'],roleid = request.session['role_id'])     
    args['courses'] = obj
    for i in obj:
        args['coursename'] = i.courseid.coursename        
    return render_to_response("student/coordinator_firstPage.html",args,context_instance=RequestContext(request))

    

  
###############Display details of student of logged-in teacher for selected institute for selected course from Student Tables#############

def studentdetails(request,courseid,pid):
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request)
    args.update(csrf(request))
    try:
       courseobj = edxcourses.objects.get(courseid = courseid)
       args['coursename']=courseobj.coursename
       args['course']=courseobj.course
    except:
           args['message'] ="cannot get entry for course"
           return render(request,'geterror.html',args)
    args['personid']=request.session['person_id']

    try:
        courselevelid=Courselevelusers.objects.get(personid__id=pid,courseid__courseid=courseid,startdate__lte=current,enddate__gte=current)
    except:
           args['message'] ="You are not valid Teacher for this course"
           return render(request,'geterror.html',args)
    students = studentDetails.objects.filter(teacherid__id=courselevelid.id,courseid=courseid)
    data=[]    
    for student in students:   
		try:

			data.append([student.edxuserid.pk,student.roll_no,student.edxuserid.username,student.edxuserid.email])
		except :
				continue
                
    data.sort()  
    args['info']=data
    args['id'] = pid
    return render_to_response("student/studentdetails.html",args,RequestContext(request))





def downloadcsv(request,course,id):
   
    args=sessiondata(request)
    name=args['person'].firstname+"_"+course+"  student_details"+'.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=" %s"'%(name)
    context=RequestContext(request)
    writer = csv.writer(response)
    writer.writerow(["Roll_No", "Username","Email-ID"])     
     
    try:
        courselevelid=Courselevelusers.objects.get(personid__id=id,courseid__courseid=course,startdate__lte=current,enddate__gte=current)
    except:
           args['error_message'] ="You are not valid Teacher for this course"
           return render(request,'geterror.html',args)
    students = studentDetails.objects.filter(teacherid__id=courselevelid.id,courseid=course)
    data=[]    
    for student in students:   
		try:

			writer.writerow([student.roll_no,student.edxuserid.username,student.edxuserid.email])
		except :
				continue
    return response






#########################Update student data(roll number) on edit of student details in studentDetails table #############################
def Update(request,pid,courseid,t_id):
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request)
    #args = {}
    args.update(csrf(request))
    args['course']=edxcourses.objects.get(courseid=courseid).course
    if request.method == 'POST':        
        studentDetails.objects.filter(edxuserid__username = request.POST['username']).update(roll_no = request.POST['roll_no'])        
        user = iitbx_auth_user.objects.get(edxuserid = pid)      
        return HttpResponseRedirect('/studentdetails/'+courseid+'/'+t_id)
    else:
        
        student = studentDetails.objects.get(edxuserid__edxuserid=pid)
       
        args.update(csrf(request))
        args['info']=student
        args['courseid']=courseid
        args['pid']=pid
        args['t_id'] = t_id
        return render_to_response("student/update.html",args)

     
##############Check that student data  uploaded  by teacher is present iitbx_auth_user table and store that data in student interface table with generating csv of valid and invalid students ################  
def upload(request,code,courseid):

   # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid and use args to add your  data and send  in html 
   args =sessiondata(request)

   args.update(csrf(request))
   person=Personinformation.objects.get(email=request.session['email_id'])   
   args['coursename']=edxcourses.objects.get(courseid=courseid).course
  
   if request.POST:
        form = UploadForms(request.POST, request.FILES)
        teacher_id = request.session['person_id'] 
        fname=request.FILES['filename'].name        
        if form.is_valid():
           
            a = form.save()
            for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles where uploadedby_id = 1 ORDER BY id DESC LIMIT 1 '):
                    changedfname = str(p.filename)
            args['fname']=fname
            uploadedfiles.objects.filter(filename = fname).update(uploadedby = teacher_id)
            extension = validate_file_extension(fname)
            if(extension):
                if code == "2":
                    context = validatefileinfo(request,courseid,changedfname,teacher_id)
                    context.update(args)
                    print context
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
     
   args['form'] = form
   args['courseid']=courseid
   return render_to_response('student/upload.html', args)

############ Create csv of valid and invalid reports if error_message is blank or not blank respectively in student_interface table  ############
def output_csv(request,code):
   
    for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles ORDER BY id DESC LIMIT 1 '):
        fname = str(p.filename)    
    personid = request.session['person_id']   
    timestr = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    response = HttpResponse(content_type='text/csv')
    courseid=request.session['courseid']

    if(int(code)==1):
        downloadfile = "%s_%s_%s_%s" % ("report","valid",courseid,timestr)#1
        downloadfile=downloadfile+".csv"
        response['Content-Disposition'] = 'attachment; filename="%s"'%(downloadfile)        
        writer = csv.writer(response)
        csvdata = student_interface.objects.filter(error_message = "",fileid__filename = fname)  
        

    elif(int(code)==2):
        downloadfile = "%s_%s_%s_%s" % ("report","invalid",courseid,timestr)#1
        downloadfile=downloadfile+".csv"
        response['Content-Disposition'] = 'attachment; filename="%s"'%(downloadfile)
        writer = csv.writer(response)
        csvdata = student_interface.objects.filter(~Q(error_message = ""),fileid__filename = fname)
 
    writer.writerow(["RollNo", "Username","Email","Message"])
    for row in csvdata:
            writer.writerow([row.roll_no, row.username, row.email,row.error_message])
        

    return response
           
            
############# Display homepage of logged-in teacher for selected institute contains list of courses and link of upload and student details ############  

def teacherhome(request):
     
# args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid and use args to add your  data and send  in html 
    args =sessiondata(request)
    current_date=date.today()
    args.update(csrf(request))
    person=Personinformation.objects.get(email=request.session['email_id'])
    args['pid']=request.session['person_id']
    
    a=[]
    #select courselevel object of the teacher who has login
    #person = Courselevelusers.objects.get(personid = request.session['person_id'],courseid=request.session['edxcourseid'],startdate__lte=current_date,enddate__gte=current_date,instituteid=request.session[)
    
    #select all the courses from edxcourses table
    course=edxcourses.objects.get(id=request.session['edxcourseid'])
    a.append(course)
    #Context = {'courses_list': a} #send the context to the html page to display the courses
    args['courses_list'] = a
    return render_to_response("student/teacherhome.html",args, context_instance=RequestContext(request))



############## unenroll student by updating teacher id to default teacherid =1 in studentDetails Teacher###############

def unenrollstudent(request,pid,courseid,t_id):
	# args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid and use args to add your  data and send  in html 
	args =sessiondata(request)  
	 
	studentDetails.objects.filter(edxuserid__edxuserid = pid).filter(courseid = courseid).update(teacherid = 1)
	try:
	    user = iitbx_auth_user.objects.get(edxuserid = pid)
	except:
           args['message'] ="user is not part of IITBombayX"
           return render(request,'geterror.html',args)

	return HttpResponseRedirect('/studentdetails/'+courseid+"/"+t_id)



########change password on confirmation of old password  and after change password delete logged-in session , logout and redirect to login page for login with new passwords     ##########################

def change_pass(request):
   
    module = 'Login'
    page = 'Reset_Pass'
    args={}
    args.update(csrf(request))
    if request.method == 'POST':
       args={}
       try: 
		   
		   args.update(csrf(request))
		   args['old_password']=oldpwd=request.POST.get('old_password','').strip()
		   user=User.objects.get(username=request.session['email_id'])
		   args['password1']=password1= request.POST.get('new_password1','').strip()
		   args['password2']=password2= request.POST.get('new_password2','').strip()
		   args['message']=[]
		   
		   per_id=Personinformation.objects.get(email=request.session['email_id']).id
		   if args['message']:
			  return render_to_response('login/changepass.html',args)
		   else: 
		       
		         if user.check_password(oldpwd):
			        
			        if  len(password1)==0 or len(password2)==0 or password1 != password2:
				        
				        args['message']= retrieve_error_message(module,page,'NO_MTCH')
				        return render_to_response('login/changepass.html',args)

			        else:  
		  ## If the two new passwords match, password is changed and a mail is sent to the user regarding the change 
				            
				        user.set_password(password1)
				        user.save()
                     
				        args['message']= retrieve_error_message(module,page,'PWD_SET')
				        ec_id = EmailContent.objects.get(systype='Login', name='success').id
				        send_email(request,ec_id, per_id, per_id)
                        
				        del request.session['person_id']
				        del request.session['email_id']
				        del request.session['institute_id']
				        request.session.flush()
				        cache.clear()
				        auth.logout(request)
		#return HttpResponseRedirect('/')
				        
				        #response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
				        #response.delete_cookie()
	
				        return render_to_response('login/change_pwdsuccess.html',args)            
		         args['message']= "old password incorrect"
		         return render_to_response('login/changepass.html',args)
       except:
               
               args['error_message']="you are not logged in.Please login to change your password"
               return render_to_response('login/tologin.html',args)
    return  render_to_response('login/changepass.html',args)

####################################Admin Report ######################################################################################


#showing reports to blended mooc reports admin
def blendedadmin_home(request):
    input_list={}

    report_name_list=[]
    report_list=Reports.objects.all()   #fetching all reports from database
    print report_list
    #for index in report_list:
       # report_name_list.append(index)     
    input_list['report_list']=report_list        #names of all reports to be displayed 
    return render(request,admin_home_,input_list)



def blendedadmin(request,report_id):
    if report_id !=4:
        print report_id
        input_list={}
        errors=[]
        input_list['errors']=errors
        report_obj=Reports.objects.get(reportid=report_id)
        input_list['report_name']=report_obj.report_title

        if not input_list['errors']:
          input_list['report_description']=report_obj.comments
          query=report_obj.sqlquery
          print query
          reports=Userlogin.objects.raw(query)
       
          print reports
          input_list['reports']=reports
          return render(request,display_report_,input_list)


    report_name_list=[]
    report_list=Reports.objects.all()

    for index in report_list:
         report_name_list.append(Reports.objects.get(reportid=index.reportid).report_title)
         input_list['report_name_list']=report_name_list
         return render(request,admin_home_,input_list)


#################################### End Admin Report ####################################################################################
