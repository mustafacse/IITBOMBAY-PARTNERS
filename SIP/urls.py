#url(r'^mutiir', views.multinstrole, name = 'mutiir'),
# REGISTRATION (Dhiraj)
#url(r'^rolepage1/', 'SIP.views.rolepage1',name='rolepage1'),
#url(r'^rolepage2/(?P<role>[0-9])/', 'SIP.views.rolepage2',name='rolepage2'),
'''	
    url(r'^request_registration/$', 'SIP.views.requestregister'),
    #url(r'^register/(?P<reqid>\d+)/$', 'SIP.views.register'), #(?P<password>[0-9]+)/(?P<email>[a-zA-Z0-9@_.]+)
    #url(r'^auth_register/(?P<appinsid>\d+)/$', 'SIP.views.auth_register'),
    url(r'^request_verification_success/(?P<reqid>\d+)/$', 'SIP.views.request_verification_success'),
    url(r'^resend_verification_mail/(?P<ec_id>[0-9]+)/(?P<pk>[0-9]+)/$','SIP.views.resend_verification_mail'),

	
    url(r'^register/(?P<userid>[0-9]+)/(?P<pageid>[0-9]+)/$', 'SIP.views.register'), #(?P<password>[0-9]+)/(?P<email>[a-zA-Z0-9@_.]+)
    url(r'^edit_profile/(?P<userid>[0-9]+)/(?P<pageid>[0-9]+)/$', 'SIP.views.register'),

#Apoorva Agrawal
    url(r'^head/pc/', views.pc, name='pc'),	
    url(r'^dash/', views.dash, name = 'dash'),
    url(r'^invite/', views.invite, name = 'invite'),
    url(r'^approve/(?P<req_pid>[0-9]+)/', views.approve, name = 'approve'),
    url(r'^reject/(?P<req_pid>[0-9]+)/', views.reject, name = 'reject'),
    url(r'^consent/(?P<req_pid>[0-9]+)/', views.consent, name = 'consent'),
    url(r'^dissent/(?P<req_pid>[0-9]+)/', views.dissent, name = 'dissent'),
    url(r'^cancel/(?P<req_pid>[0-9]+)/', views.cancel, name = 'cancel'),
    url(r'^remove/(?P<clu_pid>[0-9]+)/', views.removeCLU, name = 'remove'),
      
	#Course management
    url(r'^enrollfinal/IITBombayX/(?P<course>[a-zA-Z0-9.]+)/(?P<years>[0-9-]+)/$', views.enrollfinal, name = 'enrollfinal'),
    url(r'^unenroll/(?P<course>[a-zA-Z0-9.]+)/(?P<year>[0-9-]+)/$', views.unenroll, name='unenroll'),
    url(r'^enrolled/(?P<course>[a-zA-Z0-9.]+)/$', views.enrolled, name='enrolled'),
    url(r'^updated/(?P<course>[a-zA-Z0-9.]+)/$', views.updated, name='updated'),
    url(r'^unenrolled/(?P<args>[a-zA-Z0-9.]+)/$', views.unenrolled, name='unenrolled'),
    url(r'^ccourses/',views.ccourse, name='ccourses'),
    url(r'^allcourses/',views.allcourses, name='allcourses'),
    url(r'^update/IITBombayX/(?P<course>[a-zA-Z0-9.]+)/(?P<years>[0-9-]+)/$',views.updatecourses, name='update'),
    url(r'^IITBombayX/(?P<course>[a-zA-Z0-9.]+)/(?P<year>[0-9-]+)/$',views.course, name='course'),
	 # end of course management 

    url(r'^teacherlist/(?P<course>[a-zA-Z0-9./-]+)/$','SIP.views.teacherlist'),       
    url(r'^coordinatorhome/$','SIP.views.courselist'),
    #url(r'^parse/(?P<course>[\w{}\.\-\/]{1,40})$','SIP.views.studentdetails'),

        #url(r'^print/(?P<row>[\w{}.-]{1,40})/$','SIP.views.Print'),
    #url(r'^updatestudent/(?P<pid>[0-9]+)/(?P<course>[a-zA-Z0-9./-]+)/$','SIP.views.Update'),
#url(r'^downloadcsv1/(?P<course>[a-zA-Z0-9]+)/$','SIP.views.downloadcsv',name='downloadcsv'),
    #url(r'^print$','SIP.views.Print'),
 #performance
    url(r'^gradeupload/$','SIP.views.gradeupload'),
    #url(r'^report/$','SIP.views.report'),
    url(r'^report/(?P<option>[a-z]+)/(?P<course>[\w{}\.\-\/]{1,40})/$','SIP.views.report'),
    url(r'^reportinst/(?P<option>[a-z]+)/(?P<courseid>[a-zA-Z0-9\.]+)/$','SIP.views.reportinst'),
    url(r'^reportinstcmp/(?P<option>[a-z]+)/(?P<courseid>[a-zA-Z0-9\.]+)/$','SIP.views.reportinstcmp'),
    url(r'^courseadminhome/$','SIP.views.courseadmin'),
   
'''

from django.conf.urls import url

from . import views

urlpatterns = [
     url(r'^$', 'SIP.views.sessionlogin',name='course'),
     url(r'^get_multi_roles/', 'SIP.views.get_multi_roles',name='get_multi_roles'),
     url(r'^set_single_role/(?P<role>[0-9])/(?P<courseid>[\w{}\.\-\/]{1,40})/(?P<cid>[0-9]{1,40})$', 'SIP.views.set_single_role',name='set_single_role'),	
    url(r'^teacher/$','SIP.views.teacherhome'),
    url(r'^studentdetails/(?P<courseid>[\w{}\.\-\/]{1,40})/(?P<pid>[0-9]+)/$','SIP.views.studentdetails'),
	#url(r'^studentdetails/(?P<course>[a-zA-Z0-9./-]+)/(?P<pid>[0-9]+)/$','SIP.views.studentdetails'),
    #url(r'^updatestudent/(?P<pid>[0-9]+)/(?P<coursei>[a-zA-Z0-9./-]+)/(?P<t_id>[0-9]+)/$','SIP.views.Update'),
	url(r'^updatestudent/(?P<pid>[0-9]+)/(?P<courseid>[\w{}\.\-\/]{1,40})/(?P<t_id>[0-9]+)/$','SIP.views.Update'),
    url(r'^movestudents$','SIP.views.movestudents'),
    url(r'^downloadcsv1/(?P<course>[a-zA-Z0-9./-]+)/(?P<id>[0-9]+)/$','SIP.views.downloadcsv',name='downloadcsv'),
    url(r'^upload/(?P<code>[0-9])/(?P<courseid>[\w{}\.\-\/]{1,40})/$', 'SIP.views.upload'),
    url(r'^upload/uploaded/', 'SIP.views.uploaded'),
    url(r'^downloadcsv/(?P<code>[0-9])/$', 'SIP.views.output_csv'),
    #url(r'^unenroll/(?P<pid>[0-9-]+)/(?P<course>[a-zA-Z0-9./-]+)/(?P<t_id>[0-9]+)/$','SIP.views.unenrollstudent'),
	url(r'^unenroll/(?P<pid>[0-9-]+)/(?P<courseid>[\w{}\.\-\/]{1,40})/(?P<t_id>[0-9]+)/$','SIP.views.unenrollstudent'),
	url(r'^report/(?P<option>[a-z]+)/(?P<course>[\w{}\.\-\/]{1,40})/$','SIP.views.report'),
    url(r'^substituteteacher/$','SIP.views.substituteteacher'),
    url(r'^completepage/$','SIP.views.complete'),
    url(r'^addstudent/(?P<pid>[0-9-]+)/$','SIP.views.addstudent'),
    url(r'^massunenrollment/$','SIP.views.massunenroll'),
    #url(r'^teacherlist/(?P<course>[a-zA-Z0-9./-]+)/$','SIP.views.teacherlist'),
	url(r'^teacherlist/(?P<courseid>[\w{}\.\-\/]{1,40})/$','SIP.views.teacherlist'),
    url(r'^ccourses/',views.ccourse, name='ccourses'),
	#blended mooc coordinator and admin
    url(r'^bmchome','SIP.views.bmchome'),
    url(r'^blendedadmin_home/','SIP.views.blendedadmin_home',name='blendedadmin_home'),
    url(r'^blendedadmin/(?P<report_id>[0-9./-]+)/$','SIP.views.blendedadmin',name='blendedadmin'),
    url(r'^bmcintermediate/(?P<institute_id>[0-9]+)','SIP.views.bmcintermediate'),
    url(r'^form1','SIP.views.form1'),
    url(r'^selectcourse$','SIP.views.selectcourse',name='selectcourse'),

]
