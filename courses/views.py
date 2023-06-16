from ntpath import join
from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import FileSystemStorage
#from numpy import average
from pkg_resources import EntryPoint
from .forms import UserRegisterForm
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random
from datetime import datetime
from django.forms.models import model_to_dict
import csv
from django.conf import settings

# from courses.models import Assignments, CreatedClasses, JoinedClasses,Submission

# Create your views here.


def signup(request):
    if request.method == 'POST':
        forms = UserRegisterForm(request.POST)
        if forms.is_valid():
            forms.save()
            # username = forms.cleaned_data.get('username')
            messages.success(
                request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        forms = UserRegisterForm()
    return render(request, 'courses/signup.html', {'forms': forms})


@login_required
def index(request):
    return render(request, 'courses/index.html', {'title': 'Peer2Peer-Grading: Home'})

def out_about(request):
    context = {
        'title': 'Peer2Peer-Grading: About',
    }
    return render(request, 'courses/about.html', context)
    

def about(request):
    
    current_user = request.user
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    if request.POST:
        if request.POST['del_class'] != '-1':
            del_class = request.POST['del_class']
            dobj = CreatedClasses.objects.get(pk=del_class)
            dobj.delete()
        else:
            cur_user = request.user
            data = request.POST
            classname = data['classname']
            description = data['desc']
            classcode = data['code']
            if CreatedClasses.objects.filter(class_code=classcode).first() is None:
                obj = CreatedClasses(
                    class_name=classname, class_description=description, class_code=classcode, teacher=cur_user)
                obj.save()
            else:
                pass
    context = {
        'classes': all_classes,
        'joined':joined_classes,
        'title': 'Peer2Peer-Grading: About',
    }
    return render(request, 'courses/about.html', context)


def contact(request):
    current_user = request.user
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    context = {
        'classes': all_classes,
        'joined':joined_classes,
        'title': 'Peer2Peer-Grading: Contact Us'
    }
    return render(request, 'courses/contact.html', context)


def courses(request):
    context = {}
    return render(request, 'courses/courses.html', context)


@login_required
def home(request):
    current_user = request.user
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    if request.POST:
        if request.POST['del_class'] != '-1':
            del_class = request.POST['del_class']
            dobj = CreatedClasses.objects.get(pk=del_class)
            dobj.delete()
        else:
            cur_user = request.user
            data = request.POST
            classname = data['classname']
            description = data['desc']
            classcode = data['code']
            if CreatedClasses.objects.filter(class_code=classcode).first() is None:
                obj = CreatedClasses(
                    class_name=classname, class_description=description, class_code=classcode, teacher=cur_user)
                obj.save()
            else:
                pass

    context = {
        'classes': all_classes,
        'joined': joined_classes,
        'google_client_id': settings.GOOGLE_CLIENT_ID,
        'google_client_secret': settings.GOOGLE_CLIENT_SECRET
    }
    return render(request, 'courses/home.html', context)


@login_required
def cur_class(request, class_id):
    
    current_user = request.user
    if CreatedClasses.objects.filter(pk=class_id).filter(teacher=request.user).first() is None:
        return render(request, 'courses/access_denied.html')
    else:
        if request.POST:
            if request.POST['nname'] == 'addstudent':
                username = request.POST['student_username']
                user_obj = User.objects.filter(username=username).first()
                if user_obj is None:
                    messages.success(request, "Student Not Found")

                elif JoinedClasses.objects.filter(student=user_obj).first() is not None:
                    messages.success(request, "Student is in the class")
                else:
                    created_class = CreatedClasses.objects.get(pk=class_id)
                    obj = JoinedClasses(
                        class_id=created_class, student=user_obj)
                    obj.save()
                    messages.success(request, "Student Added")
            if request.POST['nname'] == 'addteacher':
                teacher_username = request.POST['teacher_username']
                teacher_obj = User.objects.filter(
                    username=teacher_username).first()
                class_created = CreatedClasses.objects.filter(
                    pk=class_id).first()
                if teacher_obj is None:
                    messages.success(request, 'Teacher not Found')
                elif CreatedClasses.objects.filter(class_code=class_created.class_code).filter(teacher=teacher_obj).first() is not None:
                    messages.success(request, "Teacher is in the class")
                else:
                    obj = CreatedClasses(class_code=class_created.class_code, class_name=class_created.class_name,
                                         class_description=class_created.class_description, teacher=teacher_obj)
                    obj.save()
                    messages.success(request, "Teacher Added")
            if request.POST['nname'] == 'tga':
                data = request.POST
                a_name = data['aname']
                points = data['points']
                due = data['due']
                grading_type = True
                current = CreatedClasses.objects.get(pk=class_id)
                assignment = Assignments.objects.filter(
                    assignment_name=a_name).filter(class_id=current).first()
                if assignment is not None:
                    pass
                else:
                    # if data['teacher'] == 'peer':
                    #   grading_type = False
                    #   teacher_ratio = int(data['tratio'])
                    #   student_ratio = 100 - teacher_ratio
                    #   no_of_peers = int(data['no_of_peers'])
                    #   obj = Assignments(assignment_name=a_name, points=points, due_date=due, class_id=current, grading_type=grading_type, teacher_ratio=teacher_ratio, student_ratio=student_ratio, no_of_peers=no_of_peers)
                    #   obj.save()
                    # assign_peers(class_id, obj, no_of_peers)

                    obj = Assignments(assignment_name=a_name, points=points,
                                      due_date=due, class_id=current, grading_type=grading_type)
                    obj.save()
            if request.POST['nname'] == 'pga':
                data = request.POST
                a_name = data['aname']
                points = data['points']
                due = data['due']
                grading_type = False
                current = CreatedClasses.objects.get(pk=class_id)
                assignment = Assignments.objects.filter(
                    assignment_name=a_name).filter(class_id=current).first()
                if assignment is not None:
                    pass
                else:
                    teacher_ratio = int(data['tratio'])
                    student_ratio = 100 - teacher_ratio
                    no_of_peers = int(data['no_of_peers'])
                    obj = Assignments(assignment_name=a_name, points=points, due_date=due, class_id=current,
                                      grading_type=grading_type, teacher_ratio=teacher_ratio, student_ratio=student_ratio, no_of_peers=no_of_peers)
                    obj.save()

            # if request.POST['nname'] == 'notice':
            #     data = request.POST
            #     notice_name = data['aname']
            #     # notice_file = request.POST['document_link']
            #     notice_file = request.FILES.getlist('file')
            #     # current = CreatedClasses.objects.get(pk=class_id)
            #     # notice_instance = notices(
            #     #     notice_name=notice_name, class_id=current)
            #     # notice_instance.save()
            #     # notice_file_instance = noticeFile(
            #     #     document_link=notice_file, notice_id=notice_instance)
            #     # notice_file_instance.save()
            #     current = CreatedClasses.objects.get(pk=class_id)
            #     notice_instance = notices(
            #         notice_name=notice_name, class_id=current)
            #     notice_instance.save()
            #     for f in notice_file:
            #         notice_file_instance = noticeFile(
            #             files=f, notice_id=notice_instance)
            #         notice_file_instance.save()
            if request.POST['nname'] == 'notice':
                data = request.POST
                notice_name = data['aname']
                notice_file = request.FILES.getlist('file')
                current = CreatedClasses.objects.get(pk=class_id)
                notice_instance = notices(
                    notice_name=notice_name, class_id=current)
                notice_instance.save()
                for f in notice_file:
                    notice_file_instance = noticeFile(
                        files=f, notice_id=notice_instance)
                    notice_file_instance.save()

        # current = CreatedClasses.objects.get(pk=class_id)
        # print("In cur class")
        # print(current)
        # all_classes = CreatedClasses.objects.filter(
        #     class_code=current.class_code)
        # assignments = []
        # notice = []
        # for cl in all_classes:
        #     all_assignments = Assignments.objects.filter(class_id=cl)
        #     for a in all_assignments:
        #         assignments.append(a)
        #     all_notices = notices.objects.filter(class_id=cl)
        #     for n in all_notices:
        #         notice.append(n)
        # total_students = len(
        #     JoinedClasses.objects.filter(class_id=current)) - 1
        # # if Assignments.objects.filter(class_id=current).first().student_ratio is not None:
        # #     student_ratio=Assignments.objects.filter(class_id=current).first().student_ratio
        # students = JoinedClasses.objects.filter(
        #     class_id=current).values('student')
        # students_list = [User.objects.get(id=c['student'])
        #                  for i, c in enumerate(students)]
        # print(students_list)

        # teachers = [cl.teacher for cl in all_classes]

        # teachers_list = [User.objects.get(username=c)
        #                  for i, c in enumerate(teachers)]

        # context = {
        #     'students': students_list,
        #     'teachers': teachers_list,
        #     'total_students': total_students,
        #     'cur_class': current,
        #     'assignments': assignments,
        #     'class_id': class_id,
        #     'notice': notice,
        # }
        # return render(request, 'courses/cur_class.html', context)

        
        
        current_class = CreatedClasses.objects.get(pk=class_id)
        all_classes = CreatedClasses.objects.filter(
            class_code=current_class.class_code)
        assignments = []
        notice = []
        for cl in all_classes:
            all_assignments = Assignments.objects.filter(class_id=cl)
            for a in all_assignments:
                assignments.append(a)
            all_notices = notices.objects.filter(class_id=cl)
            for n in all_notices:
                notice.append(n)
        total_students = len(
            JoinedClasses.objects.filter(class_id=current_class)) - 1
        
        students = JoinedClasses.objects.filter(class_id=current_class).values('student')
        students_list = [User.objects.get(id=c['student'])
                         for i, c in enumerate(students)]
        #print(students_list)
        teachers = [cl.teacher for cl in all_classes]
        teachers_list = [User.objects.get(username=c)
                         for i, c in enumerate(teachers)]

        all_classes = CreatedClasses.objects.filter(teacher=current_user)
        joined_classes = JoinedClasses.objects.filter(student=current_user)

        context = {
            'students': students_list,
            'teachers': teachers_list,
            'total_students': total_students,
            'cur_class': current_class,
            'assignments': assignments,
            'class_id': class_id,
            'notice': notice,
            'classes': all_classes,
            'joined':joined_classes
        }
        return render(request, 'courses/cur_class.html', context)



def assign_peers(request, class_id, assignment_id):
    cur_user = request.user
    current_class = CreatedClasses.objects.get(pk=class_id)
    total_students = len(JoinedClasses.objects.filter(class_id=current_class))
    all_classes = CreatedClasses.objects.filter(teacher=cur_user)
    joined_classes = JoinedClasses.objects.filter(student=cur_user)
    if current_class.teacher != request.user:
        return render(request, 'courses/access_denied.html')
    peer = {}
    list1 = []
    cur_assignment = Assignments.objects.get(pk=assignment_id)
    created_class = CreatedClasses.objects.get(pk=class_id)
    joined_students = JoinedClasses.objects.filter(class_id=created_class)
    # print(len(joined_students))
    no_of_peers = cur_assignment.no_of_peers

    obj = AssignedPeers.objects.filter(assignment=cur_assignment).first()
    print(obj)

    if (obj is None and total_students != 0 and no_of_peers < total_students):
        student_list = []
        for s in joined_students:
            print(s)
            cur_s = s.student
            student_list.append(cur_s)
        students = random.sample(student_list, len(student_list))
        i = 0
        while True:
            cur_student = students[i]
            for j in range(1, no_of_peers+1):
                AssignedPeers(
                    peer=students[i-j], teacher=cur_student, assignment=cur_assignment).save()
            i += 1
            if i == len(students):
                break
        obj1 = AssignedPeers.objects.filter(assignment=cur_assignment)
        context = {
            'peers': obj1,
            'cur_assignment': cur_assignment,
        }
    else:
        obj = AssignedPeers.objects.filter(assignment=cur_assignment)
        context = {
            'peers': obj,
            'cur_assignment': cur_assignment,
            'classes':all_classes,
            'joined':joined_classes
        }
    return render(request, 'courses/assign_peers.html', context)


def nav(request):
    current_user = request.user
    if request.POST:
        if request.POST['del_class'] != '-1':
            del_class = request.POST['del_class']
            dobj = CreatedClasses.objects.get(pk=del_class)
            dobj.delete()
        else:
            cur_user = request.user
            data = request.POST
            classname = data['classname']
            description = data['desc']
            classcode = data['code']
            if CreatedClasses.objects.filter(class_code=classcode).first() is None:
                obj = CreatedClasses(
                    class_name=classname, class_description=description, class_code=classcode, teacher=cur_user)
                obj.save()
            else:
                pass
    
    all_classes = JoinedClasses.objects.filter(student=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    context = {
        'classes': all_classes,
        'joined':joined_classes,
    }
    return render(request, 'courses/nav.html',context)
    


@login_required
def joinclass(request):
    current_user = request.user
    
    #class_id = request.POST.get('class_id')
    #current_class = CreatedClasses.objects.get(pk=class_id)
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    

    if request.POST:
        if request.POST['l_class'] != "-1":
            current_class = CreatedClasses.objects.get(
                pk=request.POST['l_class'])
            obj = JoinedClasses.objects.filter(
                class_id=current_class).filter(student=current_user).first()
            obj.delete()
        else:
            cur_user = request.user
            join_id = request.POST['joincode']
            c_class = CreatedClasses.objects.filter(class_code=join_id).first()
            if c_class.teacher == request.user:
                messages.success(request, f'You are the teacher of this class')
            else:
                temp = JoinedClasses.objects.filter(
                    student=current_user).filter(class_id=c_class).first()
                if temp is not None:
                    messages.success(request, f'Already Joined the class')
                elif c_class is not None:
                    j_class = JoinedClasses(class_id=c_class, student=cur_user)
                    j_class.save()
                else:
                    messages.success(
                        request, f'Class not found/Class code is incorrect!')
    
    
    
    context = {
        'classes': all_classes,
        'joined':joined_classes
    }
    return render(request, 'courses/joinclasses.html',context)


@login_required
def join_cur_class(request, class_id):
    current_user = request.user
    current_class = CreatedClasses.objects.get(pk=class_id)
    if JoinedClasses.objects.filter(class_id=current_class).filter(student=request.user).first() is not None:
        # created_class = CreatedClasses.objects.filter(class_code=current_class.class_code)
        all_classes = CreatedClasses.objects.filter(
            class_code=current_class.class_code)
        # joined_classes = JoinedClasses.objects.filter(class_code=current_class.class_code)
        assignments = []
        notice = []
        classes = []
        for cl in all_classes:
            all_assignments = Assignments.objects.filter(class_id=cl)
            for a in all_assignments:
                assignments.append(a)
            all_notices = notices.objects.filter(class_id=cl)
            for n in all_notices:
                notice.append(n)
        # for cl in joined_classes:
        #     all_joined_classes = JoinedClasses.filter(class_id=cl)
        #     for a in all_joined_classes:
        #         classes.append(a)
        total_students = len(
            JoinedClasses.objects.filter(class_id=current_class)) - 1
        
        students = JoinedClasses.objects.filter(class_id=current_class).values('student')
        students_list = [User.objects.get(id=c['student'])
                         for i, c in enumerate(students)]
        #print(students_list)
        teachers = [cl.teacher for cl in all_classes]
        teachers_list = [User.objects.get(username=c)
                         for i, c in enumerate(teachers)]
        all_classes = CreatedClasses.objects.filter(teacher=current_user)
        joined_classes = JoinedClasses.objects.filter(student=current_user)
        context = {
            'cur_class': current_class,
            'assignments': assignments,
            'class_id': class_id,
            "notice": notice,
            'classes': all_classes,
            'joined':joined_classes,
            'students':students_list,
            'teachers':teachers_list,
            'total_students':total_students
            
            # "joined":classes
        }
        return render(request, 'courses/join_cur_class.html', context)
    else:
        return render(request, 'courses/access_denied.html')
# def join_cur_class(request, class_id):
#     current_class = CreatedClasses.objects.get(pk=class_id)
#     if JoinedClasses.objects.filter(class_id=current_class).filter(student=request.user).first() is not None:
#         # created_class = CreatedClasses.objects.filter(class_code=current_class.class_code)
#         all_classes = CreatedClasses.objects.filter(
#             class_code=current_class.class_code)
#         joined_classes = JoinedClasses.objects.filter(student=current_user)
#         print(all_classes)
#         assignments = []
#         notice = []

#         for cl in all_classes:
#             all_assignments = Assignments.objects.filter(class_id=cl)
#             for a in all_assignments:
#                 assignments.append(a)
#             all_notices = notices.objects.filter(class_id=cl)
#             for n in all_notices:
#                 notice.append(n)
#             #for n in join_cur_class

        
#         context = {
#             'cur_class': current_class,
#             'assignments': assignments,
#             'class_id': class_id,
#             "notice": notice,
#             "joined": joined_classes
#         }

        

#         return render(request, 'courses/join_cur_class.html', context)
#     else:
#         return render(request, 'courses/access_denied.html')


@login_required
def cur_assignment_join(request, assignment_id):
    current_user = request.user
    context = {}
    embed_url = ""
    embd_url = ""
    edit = False
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    if request.POST:
        # if request.POST.get('youtube_link', False):
        #     values = request.POST['youtube_link']
        #     context['youtube_link'] = values
        #     if(len(values.split("/")) > 1):
        #         if values.find("watch") != -1:
        #             embed_url = "https://youtube.com/embed/" + \
        #                 values.split("watch?v=")[-1]
        #         else:
        #             embed_url = "https://youtube.com/embed/" + \
        #                 values.split("/")[-1]
        #         context['youtube_link'] = embed_url
        #     return render(request, 'courses/cur_assignment_join.html', context)
        if request.POST['del_sub'] != '-1' and request.POST['del_sub'] != '0':
            del_file = request.POST['del_sub']
            dobj = SubmittedFiles.objects.get(sub=del_file)
            dobj.delete()
        elif request.POST['del_sub'] == '-1' and (request.POST.get('youtube_link', False) or request.POST.get('doc_link', False)):
            values = request.POST['youtube_link']
            embd_url = request.POST['doc_link']
            if(len(values.split("/")) > 1):
                if values.find("watch") != -1:
                    embed_url = "https://youtube.com/embed/" + \
                        values.split("watch?v=")[-1]
                else:
                    embed_url = "https://youtube.com/embed/" + \
                        values.split("/")[-1]
            current_user = request.user
            cur_assignment = Assignments.objects.get(pk=assignment_id)
            data = request.POST
            files = request.FILES.getlist('uploaded_file')
            obj = Submission.objects.filter(assignment_id=cur_assignment).filter(
                student=current_user).first()
            if obj is None:
                obj1 = Submission(assignment_id=cur_assignment,
                                  student=current_user)
                obj1.save()
                if obj1.sub_date > cur_assignment.due_date:
                    obj1.remark = "Late Submission"
                    obj1.save()
                for file in files:
                    temp = SubmittedFiles(sub=file, submission_id=obj1)
                    temp.save()
                if embed_url != "" or embd_url != "":
                    link = SubmittedLink(
                        youtube_link=embed_url, doc_link=embd_url, submission_id=obj1)
                    link.save()
            else:
                for file in files:
                    obj.sub_date = timezone.now()
                    if obj.sub_date > cur_assignment.due_date:
                        obj.remark = "Late Submission"
                        obj.save()
                    obj.save()
                    temp = SubmittedFiles(sub=file, submission_id=obj)
                    temp.save()
                if embed_url != "" or embd_url != "":
                    link = SubmittedLink(
                        youtube_link=embed_url, doc_link=embd_url, submission_id=obj)
                    link.save()
        elif request.POST['del_sub'] == '-1' and not (request.POST.get('youtube_link', False) or request.POST.get('doc_link', False)):
            current_user = request.user
            cur_assignment = Assignments.objects.get(pk=assignment_id)
            data = request.POST
            files = request.FILES.getlist('uploaded_file')
            obj = Submission.objects.filter(assignment_id=cur_assignment).filter(
                student=current_user).first()
            if obj is None:
                obj1 = Submission(assignment_id=cur_assignment,
                                  student=current_user)
                obj1.save()
                if obj1.sub_date > cur_assignment.due_date:
                    obj1.remark = "Late Submission"
                    obj1.save()
                for file in files:
                    temp = SubmittedFiles(sub=file, submission_id=obj1)
                    temp.save()

            else:
                for file in files:
                    obj.sub_date = timezone.now()
                    if obj.sub_date > cur_assignment.due_date:
                        obj.remark = "Late Submission"
                        obj.save()
                    obj.save()
                    temp = SubmittedFiles(sub=file, submission_id=obj)
                    temp.save()

        elif request.POST['act'] == '2':
            comment = request.POST['comment']
            cur_user = request.user
            curr_assignment = Assignments.objects.get(pk=assignment_id)
            submi = Submission.objects.filter(student=cur_user).filter(
                assignment_id=curr_assignment).first()
            cur_comment = Comments(
                text=comment, comment_user=cur_user, submission=submi)
            cur_comment.save()
    current_assignment = Assignments.objects.get(pk=assignment_id)
    sub = Submission.objects.filter(student=request.user).filter(
        assignment_id=current_assignment).first()

    comments = Comments.objects.filter(submission=sub)

    if current_assignment is not None:
        created_class_code = current_assignment.class_id.class_code
        created_class = CreatedClasses.objects.filter(
            class_code=created_class_code).first()
        if JoinedClasses.objects.filter(student=request.user).filter(class_id=created_class).first() is not None:
            no_peers = current_assignment.no_of_peers
            sub = Submission.objects.filter(student=request.user).filter(
                assignment_id=current_assignment).first()
            sub_files = SubmittedFiles.objects.filter(submission_id=sub)
            if SubmittedLink.objects.filter(submission_id=sub) != None:
                embed_url = SubmittedLink.objects.filter(submission_id=sub)
                temp = ""
                tmp = ""
                # print(embed_url.doc_link)
                for link in embed_url:
                    temp = link.youtube_link
                    print(link.doc_link)
                    tmp = link.doc_link
                embed_url = temp
                embd_url = tmp
            s_ratio = current_assignment.student_ratio
            t_ratio = current_assignment.teacher_ratio
            t_points = current_assignment.points
            if(len(embed_url) != 0) or (len(embd_url) != 0):
                edit = True

            if current_assignment.grading_type is False:
                peer_marks = []

                marks = 0
                total_marks = None

                peer = AssignedPeers.objects.filter(
                    assignment=current_assignment).filter(peer=request.user)
                if len(peer) == 0:
                    peer = peer.first()

                if peer is not None:
                    for p in peer:
                        temp = p.student_marks
                        peer_marks.append(temp)
                    teacher_marks = None
                    if sub is not None:
                        if sub.marks is not None:
                            teacher_marks = sub.marks
                            # teacher_marks = teacher_marks*(t_ratio/100)
                    if len(peer_marks) != 0:
                        count = 0
                        for i in peer_marks:
                            if i is not None:
                                count += 1
                        if count != 0 and count == no_peers:
                            for i in peer_marks:
                                marks = marks+i
                            marks = float(marks)/count
                            marks = marks*(s_ratio/100)
                            if teacher_marks is not None:
                                total_marks = teacher_marks+marks
                        ts_marks = round(t_points*(s_ratio/100), 1)
                        tt_marks = round(t_points*(t_ratio/100), 1)
                    # peers=AssignedPeers.objects.filter(assignment=current_assignment).filter(peer=request.user)
                    flag = True
                    if teacher_marks is not None:
                        teacher_marks = round(teacher_marks, 1)
                    if total_marks is not None:
                        total_marks = round(total_marks, 1)
                    if marks is not None:
                        marks = marks*100/s_ratio

                    context = {
                        'a': current_assignment,
                        'sub': sub,
                        'files': sub_files,
                        'youtube_link': embed_url,
                        'doc_link': embd_url,
                        # 'marks': round(marks, 1)
                        'marks': round(marks, 1),
                        'ts_marks': ts_marks,
                        'tt_marks': tt_marks,
                        # 'teacher_marks': teacher_marks,
                        'teacher_marks': teacher_marks,
                        'total_marks': total_marks,
                        't_points': t_points,
                        'comments': comments,
                        'flag': flag,
                        # 'peers': peers,
                        'count': count,
                        'no_peers': no_peers,
                        'edit': edit,
                                
                        'classes': all_classes,
                        'joined':joined_classes
                    }
                else:
                    teacher_marks = None
                    if sub is not None:
                        if sub.marks is not None:
                            teacher_marks = sub.marks
                    marks = "No peers assigned"
                    context = {
                        'a': current_assignment,
                        'sub': sub,
                        'files': sub_files,
                        'youtube_link': embed_url,
                        'doc_link': embd_url,
                        'marks': marks,
                        'teacher_marks': teacher_marks,
                        'tt_marks': current_assignment.points,
                        'comments': comments,
                        'edit': edit,
                                
                        'classes': all_classes,
                        'joined':joined_classes
                    }
            else:
                marks = "No peergrading"
                context = {
                    'a': current_assignment,
                    'sub': sub,
                    'files': sub_files,
                    'youtube_link': embed_url,
                    'doc_link': embd_url,
                    'marks': marks,
                    'comments': comments,
                    'edit': edit,
                    'classes': all_classes,
                    'joined':joined_classes
                }
            
            return render(request, 'courses/cur_assignment_join.html', context)
        else:
            return render(request, 'courses/access_denied.html')


# @login_required
# def cur_assignment_join(request, assignment_id):
#     context = {}
#     embed_url = ""
#     if request.POST:
#         # if request.POST.get('youtube_link', False):
#         #     values = request.POST['youtube_link']
#         #     context['youtube_link'] = values
#         #     if(len(values.split("/")) > 1):
#         #         if values.find("watch") != -1:
#         #             embed_url = "https://youtube.com/embed/" + \
#         #                 values.split("watch?v=")[-1]
#         #         else:
#         #             embed_url = "https://youtube.com/embed/" + \
#         #                 values.split("/")[-1]
#         #         context['youtube_link'] = embed_url
#         #     return render(request, 'courses/cur_assignment_join.html', context)
#         if request.POST['del_sub'] != '-1' and request.POST['del_sub'] != '0':
#             del_file = request.POST['del_sub']
#             dobj = SubmittedFiles.objects.get(sub=del_file)
#             dobj.delete()
#         elif request.POST['del_sub'] == '-1' and request.POST.get('youtube_link', False):
#             values = request.POST['youtube_link']
#             if(len(values.split("/")) > 1):
#                 if values.find("watch") != -1:
#                     embed_url = "https://youtube.com/embed/" + \
#                         values.split("watch?v=")[-1]
#                 else:
#                     embed_url = "https://youtube.com/embed/" + \
#                         values.split("/")[-1]
#             current_user = request.user
#             cur_assignment = Assignments.objects.get(pk=assignment_id)
#             data = request.POST
#             files = request.FILES.getlist('uploaded_file')
#             obj = Submission.objects.filter(assignment_id=cur_assignment).filter(
#                 student=current_user).first()
#             if obj is None:
#                 obj1 = Submission(assignment_id=cur_assignment,
#                                   student=current_user)
#                 obj1.save()
#                 if obj1.sub_date > cur_assignment.due_date:
#                     obj1.remark = "Late Submission"
#                     obj1.save()
#                 for file in files:
#                     temp = SubmittedFiles(sub=file, submission_id=obj1)
#                     temp.save()
#                 if embed_url != "":
#                     link = SubmittedLink(
#                         youtube_link=embed_url, submission_id=obj1)
#                     link.save()
#             else:
#                 for file in files:
#                     obj.sub_date = timezone.now()
#                     if obj.sub_date > cur_assignment.due_date:
#                         obj.remark = "Late Submission"
#                         obj.save()
#                     obj.save()
#                     temp = SubmittedFiles(sub=file, submission_id=obj)
#                     temp.save()
#                 if embed_url != "":
#                     link = SubmittedLink(
#                         youtube_link=embed_url, submission_id=obj)
#                     link.save()
#         elif request.POST['del_sub'] == '-1' and not request.POST.get('youtube_link', False):
#             current_user = request.user
#             cur_assignment = Assignments.objects.get(pk=assignment_id)
#             data = request.POST
#             files = request.FILES.getlist('uploaded_file')
#             obj = Submission.objects.filter(assignment_id=cur_assignment).filter(
#                 student=current_user).first()
#             if obj is None:
#                 obj1 = Submission(assignment_id=cur_assignment,
#                                   student=current_user)
#                 obj1.save()
#                 if obj1.sub_date > cur_assignment.due_date:
#                     obj1.remark = "Late Submission"
#                     obj1.save()
#                 for file in files:
#                     temp = SubmittedFiles(sub=file, submission_id=obj1)
#                     temp.save()

#             else:
#                 for file in files:
#                     obj.sub_date = timezone.now()
#                     if obj.sub_date > cur_assignment.due_date:
#                         obj.remark = "Late Submission"
#                         obj.save()
#                     obj.save()
#                     temp = SubmittedFiles(sub=file, submission_id=obj)
#                     temp.save()

#         elif request.POST['act'] == '2':
#             comment = request.POST['comment']
#             cur_user = request.user
#             curr_assignment = Assignments.objects.get(pk=assignment_id)
#             submi = Submission.objects.filter(student=cur_user).filter(
#                 assignment_id=curr_assignment).first()
#             cur_comment = Comments(
#                 text=comment, comment_user=cur_user, submission=submi)
#             cur_comment.save()
#     current_assignment = Assignments.objects.get(pk=assignment_id)
#     sub = Submission.objects.filter(student=request.user).filter(
#         assignment_id=current_assignment).first()

#     comments = Comments.objects.filter(submission=sub)

#     if current_assignment is not None:
#         created_class_code = current_assignment.class_id.class_code
#         created_class = CreatedClasses.objects.filter(
#             class_code=created_class_code).first()
#         if JoinedClasses.objects.filter(student=request.user).filter(class_id=created_class).first() is not None:
#             no_peers = current_assignment.no_of_peers
#             sub = Submission.objects.filter(student=request.user).filter(
#                 assignment_id=current_assignment).first()
#             sub_files = SubmittedFiles.objects.filter(submission_id=sub)
#             if SubmittedLink.objects.filter(submission_id=sub) != None:
#                 embed_url = SubmittedLink.objects.filter(submission_id=sub)
#                 temp = ""
#                 for link in embed_url:
#                     temp = link.youtube_link
#                 embed_url = temp
#             s_ratio = current_assignment.student_ratio
#             t_ratio = current_assignment.teacher_ratio
#             t_points = current_assignment.points

#             if current_assignment.grading_type is False:
#                 peer_marks = []

#                 marks = 0
#                 total_marks = None

#                 peer = AssignedPeers.objects.filter(
#                     assignment=current_assignment).filter(peer=request.user)
#                 if len(peer) == 0:
#                     peer = peer.first()
#                 if peer is not None:
#                     for p in peer:
#                         temp = p.student_marks
#                         peer_marks.append(temp)
#                     teacher_marks = None
#                     if sub is not None:
#                         if sub.marks is not None:
#                             teacher_marks = sub.marks
#                             teacher_marks = teacher_marks*(t_ratio/100)
#                     if len(peer_marks) != 0:
#                         count = 0
#                         for i in peer_marks:
#                             if i is not None:
#                                 count += 1
#                         if count != 0 and count == no_peers:
#                             for i in peer_marks:
#                                 marks = marks+i
#                             marks = float(marks)/count
#                             marks = marks*(s_ratio/100)
#                             if teacher_marks is not None:
#                                 total_marks = teacher_marks+marks
#                         ts_marks = round(t_points*(s_ratio/100), 1)
#                         tt_marks = round(t_points*(t_ratio/100), 1)
#                     # peers=AssignedPeers.objects.filter(assignment=current_assignment).filter(peer=request.user)
#                     flag = True
#                     if teacher_marks is not None:
#                         teacher_marks = round(teacher_marks, 1)
#                     if total_marks is not None:
#                         total_marks = round(total_marks, 1)
#                     context = {
#                         'a': current_assignment,
#                         'sub': sub,
#                         'files': sub_files,
#                         'youtube_link': embed_url,
#                         'marks': round(marks, 1),
#                         'ts_marks': ts_marks,
#                         'tt_marks': tt_marks,
#                         'teacher_marks': teacher_marks,
#                         'total_marks': total_marks,
#                         't_points': t_points,
#                         'comments': comments,
#                         'flag': flag,
#                         # 'peers': peers,
#                         'count': count,
#                         'no_peers': no_peers,
#                     }
#                 else:
#                     teacher_marks = None
#                     if sub is not None:
#                         if sub.marks is not None:
#                             teacher_marks = sub.marks
#                     marks = "No peers assigned"
#                     context = {
#                         'a': current_assignment,
#                         'sub': sub,
#                         'files': sub_files,
#                         'youtube_link': embed_url,
#                         'marks': marks,
#                         'teacher_marks': teacher_marks,
#                         'tt_marks': current_assignment.points,
#                         'comments': comments,
#                     }
#             else:
#                 marks = "No peergrading"
#                 context = {
#                     'a': current_assignment,
#                     'sub': sub,
#                     'files': sub_files,
#                     'youtube_link': embed_url,
#                     'marks': marks,
#                     'comments': comments,

#                 }
#             return render(request, 'courses/cur_assignment_join.html', context)
#         else:
#             return render(request, 'courses/access_denied.html')


@login_required
def view_feedback(request, assignment_id):
    current_assignment = Assignments.objects.get(pk=assignment_id)
    created_class = CreatedClasses.objects.get(
        pk=current_assignment.class_id.pk)
    joined_class = JoinedClasses.objects.filter(
        class_id=created_class).filter(student=request.user).first()
    if joined_class is None:
        return render(request, 'courses/access_denied.html')
    else:
        peers = AssignedPeers.objects.filter(
            assignment=current_assignment).filter(peer=request.user)
        context = {
            'peers': peers,
        }
        return render(request, 'courses/view_feedback.html', context)


@login_required
def cur_assignment_gradesheet(request, assignment_id):
    current_user = request.user
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    #joined_classes = JoinedClasses.objects.filter(student=current_user)
    

    current_assignment = Assignments.objects.get(pk=assignment_id)
    created_class = CreatedClasses.objects.filter(
        pk=current_assignment.class_id.pk).first()
    all_class = CreatedClasses.objects.filter(
        class_code=created_class.class_code)
    flag = 0
    for c in all_class:
        if c.teacher.username == request.user.username:
            flag = 1
            break

    if(flag == 1):
        current = None
        for c in all_class:
            current = c
        students = JoinedClasses.objects.filter(
            class_id=current).values('student')
        students_list = [User.objects.get(id=c['student'])
                         for i, c in enumerate(students)]
        entry = []

        for i, student in enumerate(students_list):
            try:
                current_sub = Submission.objects.get(
                    assignment_id=current_assignment, student=student)
                # print("Before Current Sub")
                # print(current_sub)
            except Submission.DoesNotExist:
                current_sub = None

            if(not current_sub):
                # print(current_sub)
                context = {
                    "username": student.username,
                    "email": student.email,
                }
                entry.append(context)

            else:
                samp_class = CreatedClasses.objects.filter(
                    pk=current_sub.assignment_id.class_id.pk).first()

                all_classes = CreatedClasses.objects.filter(
                    class_code=samp_class.class_code)

                flag = 0
                for c in all_classes:
                    if c.teacher.username == request.user.username:
                        flag = 1
                        break
                if flag == 0:
                    return render(request, 'courses/access_denied.html')

                student_name = current_sub.student.username
                cur_student = User.objects.get(username=student_name)
                cur_assignment = current_sub.assignment_id.pk
                current_assignment = Assignments.objects.get(
                    pk=cur_assignment)
                no_peers = current_assignment.no_of_peers
                sub = Submission.objects.filter(student=cur_student).filter(
                    assignment_id=current_assignment).first()
                # print("Above Sub")
                # print(Submission.objects.filter(student=cur_student).filter(
                #     assignment_id=current_assignment)[0])

                s_ratio = current_assignment.student_ratio
                t_ratio = current_assignment.teacher_ratio

                if current_assignment.grading_type is False:
                    peer_marks = []
                    marks = 0
                    total_marks = None

                    context = None
                    peer = AssignedPeers.objects.filter(
                        assignment=current_assignment).filter(peer=cur_student)
                    if len(peer) == 0:
                        peer = peer.first()
                    if peer is not None:
                        for p in peer:
                            temp = p.student_marks
                            peer_marks.append(temp)
                        teacher_marks = None
                        if sub is not None:
                            if sub.marks is not None:
                                teacher_marks = sub.marks

                        avg_marks = None
                        if len(peer_marks) != 0:
                            count = 0
                            for i in peer_marks:
                                if i is not None:
                                    count += 1
                            # if count != 0 and count == no_peers:
                            if count != 0:

                                for i in peer_marks:
                                    if(i is not None):
                                        marks = marks+i
                                    # print(marks)
                                marks = float(marks)/count
                                avg_marks = marks
                                marks = marks*(s_ratio/100)
                                if teacher_marks is not None:
                                    total_marks = (
                                        teacher_marks*(t_ratio/100))+marks

                        if teacher_marks is not None:
                            teacher_marks = round(teacher_marks, 1)
                        if total_marks is not None:
                            total_marks = round(total_marks, 1)

                        # print("Count "+str(count))
                        # print("Teacher Marks "+str(teacher_marks))
                        # print("Total Marks "+str(total_marks))
                        # print("Average Marks "+str(avg_marks))
                        if(avg_marks != None):
                            avg_peer_marks = round(avg_marks, 1)
                        else:
                            avg_peer_marks = None
                        # isNone = False

                        # for marks in peer_marks:
                        #     if marks is None:
                        #         isNone = True
                        #         break

                        # if isNone:
                        #     avg_peer_marks = None
                        # else:
                        #     avg_peer_marks = round(average(peer_marks), 1)

                        context = {
                            'classes':all_classes,
                            'joined':joined_classes,
                            'username': student.username,
                            'email': student.email,
                            # 'name': student.name,
                            # 'current_sub': current_sub,
                            'marks': round(marks, 1) if marks is not None else None,
                            # 'teacher_marks': teacher_marks,
                            'teacher_marks': teacher_marks,
                            'total_marks': total_marks,
                            'peer_marks': peer_marks,
                            'avg_peer_marks': avg_peer_marks,
                            "iterator": range(1, no_peers+1),
                            # 'classes': all_classes,
                            # 'joined':joined_classes,
                        }

                        entry.append(context)

                        # print(context)

                        # print(teacher_marks)
                    else:
                        if sub is not None:
                            if sub.marks is not None:
                                teacher_marks = sub.marks
                        marks = "No peers Assigned"
                        context = {
                            'username': student.username,
                            'email': student.email,

                            # 'current_sub': current_sub,
                            'marks': marks,
                            'teacher_marks': teacher_marks,
                            # 'total_marks': current_assignment.points,

                            # 'count': count,
                            # 'no_peers': no_peers,
                            # 'classes': all_classes,
                            # 'joined':joined_classes,
                        }

                        # print(context)
                        entry.append(context)

                else:
                    marks = "No peergrading"
                    context = {
                        'username': student.username,
                        'email': student.email,
                        # 'current_sub': current_sub,
                        'marks': marks,
                        # 'count': count,
                        # 'no_peers': no_peers,
                        # 'classes': all_classes,
                        # 'joined':joined_classes,
                    }
                    # print(context)
                    entry.append(context)

        finalContext = {
            
            "class": current,
            "assignment": current_assignment,
            "t_points": current_assignment.points,
            "no_peers": current_assignment.no_of_peers,
            "iterator": range(1, current_assignment.no_of_peers+1) if current_assignment.no_of_peers is not None else None,
            "entries": entry,
            'classes': all_classes,
            'joined':joined_classes,
        }
        return render(request, 'courses/gradesheet.html', finalContext)
    else:
        return render(request, "courses/access_denied.html")
    

    
# @login_required
# def cur_assignment_gradesheet(request, assignment_id):
#     current_user = request.user
#     current_assignment = Assignments.objects.get(pk=assignment_id)
#     created_class = CreatedClasses.objects.filter(
#         pk=current_assignment.class_id.pk).first()
#     all_class = CreatedClasses.objects.filter(
#         class_code=created_class.class_code)
#     flag = 0
#     for c in all_class:
#         if c.teacher.username == request.user.username:
#             flag = 1
#             break

#     if(flag == 1):
#         current = None
#         for c in all_class:
#             current = c
#         students = JoinedClasses.objects.filter(
#             class_id=current).values('student')
#         students_list = [User.objects.get(id=c['student'])
#                          for i, c in enumerate(students)]
#         entry = []

#         for i, student in enumerate(students_list):
#             try:
#                 current_sub = Submission.objects.get(
#                     assignment_id=current_assignment, student=student)
#                 # print("Before Current Sub")
#                 # print(current_sub)
#             except Submission.DoesNotExist:
#                 current_sub = None

#             if(not current_sub):
#                 # print(current_sub)
#                 context = {
#                     "username": student.username,
#                     "email": student.email,
#                 }
#                 entry.append(context)

#             else:
#                 samp_class = CreatedClasses.objects.filter(
#                     pk=current_sub.assignment_id.class_id.pk).first()

#                 all_classes = CreatedClasses.objects.filter(
#                     class_code=samp_class.class_code)

#                 flag = 0
#                 for c in all_classes:
#                     if c.teacher.username == request.user.username:
#                         flag = 1
#                         break
#                 if flag == 0:
#                     return render(request, 'courses/access_denied.html')

#                 student_name = current_sub.student.username
#                 cur_student = User.objects.get(username=student_name)
#                 cur_assignment = current_sub.assignment_id.pk
#                 current_assignment = Assignments.objects.get(
#                     pk=cur_assignment)
#                 no_peers = current_assignment.no_of_peers
#                 sub = Submission.objects.filter(student=cur_student).filter(
#                     assignment_id=current_assignment).first()
#                 # print("Above Sub")
#                 # print(Submission.objects.filter(student=cur_student).filter(
#                 #     assignment_id=current_assignment)[0])

#                 s_ratio = current_assignment.student_ratio
#                 t_ratio = current_assignment.teacher_ratio

#                 if current_assignment.grading_type is False:
#                     peer_marks = []
#                     marks = 0
#                     total_marks = None

#                     context = None
#                     peer = AssignedPeers.objects.filter(
#                         assignment=current_assignment).filter(peer=cur_student)
#                     if len(peer) == 0:
#                         peer = peer.first()
#                     if peer is not None:
#                         for p in peer:
#                             temp = p.student_marks
#                             peer_marks.append(temp)
#                         teacher_marks = None
#                         if sub is not None:
#                             if sub.marks is not None:
#                                 teacher_marks = sub.marks

#                         avg_marks = None
#                         if len(peer_marks) != 0:
#                             count = 0
#                             for i in peer_marks:
#                                 if i is not None:
#                                     count += 1
#                             # if count != 0 and count == no_peers:
#                             if count != 0:

#                                 for i in peer_marks:
#                                     if(i is not None):
#                                         marks = marks+i
#                                     # print(marks)
#                                 marks = float(marks)/count
#                                 avg_marks = marks
#                                 marks = marks*(s_ratio/100)
#                                 if teacher_marks is not None:
#                                     total_marks = (
#                                         teacher_marks*(t_ratio/100))+marks

#                         if teacher_marks is not None:
#                             teacher_marks = round(teacher_marks, 1)
#                         if total_marks is not None:
#                             total_marks = round(total_marks, 1)

#                         # print("Count "+str(count))
#                         # print("Teacher Marks "+str(teacher_marks))
#                         # print("Total Marks "+str(total_marks))
#                         # print("Average Marks "+str(avg_marks))
#                         if(avg_marks != None):
#                             avg_peer_marks = round(avg_marks, 1)
#                         else:
#                             avg_peer_marks = None
#                         # isNone = False

#                         # for marks in peer_marks:
#                         #     if marks is None:
#                         #         isNone = True
#                         #         break

#                         # if isNone:
#                         #     avg_peer_marks = None
#                         # else:
#                         #     avg_peer_marks = round(average(peer_marks), 1)

#                         context = {
#                             'username': student.username,
#                             'email': student.email,
#                             'name': student.name,
#                             'current_sub': current_sub,
#                             'marks': round(marks, 1) if marks is not None else None,
#                             'teacher_marks': teacher_marks,
#                             'teacher_marks': teacher_marks,
#                             'total_marks': total_marks,
#                             'peer_marks': peer_marks,
#                             'avg_peer_marks': avg_peer_marks,
#                             "iterator": range(1, no_peers+1),
#                         }

#                         entry.append(context)

#                         # print(context)

#                         # print(teacher_marks)
#                     else:
#                         if sub is not None:
#                             if sub.marks is not None:
#                                 teacher_marks = sub.marks
#                         marks = "No peers Assigned"
#                         context = {
#                             'username': student.username,
#                             'email': student.email,

#                             # 'current_sub': current_sub,
#                             'marks': marks,
#                             'teacher_marks': teacher_marks,
#                             # 'total_marks': current_assignment.points,

#                             # 'count': count,
#                             # 'no_peers': no_peers,
#                         }

#                         # print(context)
#                         entry.append(context)

#                 else:
#                     marks = "No peergrading"
#                     context = {
#                         'username': student.username,
#                         'email': student.email,
#                         # 'current_sub': current_sub,
#                         'marks': marks,
#                         # 'count': count,
#                         # 'no_peers': no_peers,
#                     }
#                     # print(context)
#                     entry.append(context)

#         all_classes = CreatedClasses.objects.filter(teacher=current_user)
#         joined_classes = JoinedClasses.objects.filter(student=current_user)
#         finalContext = {
#             "class": current,
#             "assignment": current_assignment,
#             "t_points": current_assignment.points,
#             "no_peers": current_assignment.no_of_peers,
#             "iterator": range(1, current_assignment.no_of_peers+1) if current_assignment.no_of_peers is not None else None,
#             "entries": entry,
#             'classes': all_classes,
#             'joined':joined_classes,
#         }
#         return render(request, 'courses/gradesheet.html', finalContext)
#     else:
#         return render(request, "courses/access_denied.html")

@login_required
def nav(request):
    current_user=request.user
    all_classes = JoinedClasses.objects.filter(student=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    context = {
        'classes': all_classes,
        'joined':joined_classes
    }
    return render(request, 'courses/nav.html', context)


@login_required
def cur_assignment_create(request, assignment_id):
    current_user = request.user
    current_assignment = Assignments.objects.get(pk=assignment_id)
    created_class = CreatedClasses.objects.filter(
        pk=current_assignment.class_id.pk).first()
    all_class = CreatedClasses.objects.filter(
        class_code=created_class.class_code)
    teacher_ratio = current_assignment.teacher_ratio
    flag = 0
    if(request.POST):
        print("Here")
        print(request.POST['marks'])
        current_sub = Submission.objects.get(pk=request.POST['cur_sub'])
        student_name = current_sub.student.username
        print(student_name)
        cur_student = User.objects.get(username=student_name)
        print(cur_student)
        obj = Submission.objects.filter(student=cur_student).filter(
            assignment_id=current_assignment).first()
        obj.marks = request.POST['marks']
        obj.save()

    for c in all_class:
        if c.teacher.username == request.user.username:
            flag = 1
            break

    if flag == 1:
        submission_list = Submission.objects.filter(
            assignment_id=current_assignment)
        print("In create assignment")
        current = None
        for c in all_class:
            current = c
        all_classes = CreatedClasses.objects.filter(teacher=current_user)
        joined_classes = JoinedClasses.objects.filter(student=current_user)
        context = {
            'assignment' : current_assignment,
            'submissions' : submission_list,
            'assignment_id' : assignment_id,
            'teacher_ratio' : teacher_ratio,
            'classes' : all_classes,
            'joined' : joined_classes
        }
        return render(request, 'courses/create_cur_assignment.html', context)
    else:
        return render(request, 'courses/access_denied.html')


@login_required
def cur_student_submission(request, submission_id):
    current_user = request.user
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    current_sub = Submission.objects.get(pk=submission_id)
    print(current_sub)
    samp_class = CreatedClasses.objects.filter(
        pk=current_sub.assignment_id.class_id.pk).first()
    all_classes = CreatedClasses.objects.filter(
        class_code=samp_class.class_code)
    flag = 0
    for c in all_classes:
        if c.teacher.username == request.user.username:
            flag = 1
            break
    if flag == 0:
        return render(request, 'courses/access_denied.html')

    submitted_files = SubmittedFiles.objects.filter(
        submission_id=submission_id)
    submitted_link = ""
    submitted_doc_link = ""
    if SubmittedLink.objects.filter(submission_id=submission_id) != None:
        embed_url = SubmittedLink.objects.filter(submission_id=submission_id)
        temp = ""
        tmp = ""
        for link in embed_url:
            temp = link.youtube_link
            tmp = link.doc_link
        submitted_link = temp
        submitted_doc_link = tmp

    student_name = current_sub.student.username
    cur_student = User.objects.get(username=student_name)
    cur_assignment = current_sub.assignment_id.pk
    current_assignment = Assignments.objects.get(pk=cur_assignment)
    no_peers = current_assignment.no_of_peers
    sub = Submission.objects.filter(student=cur_student).filter(
        assignment_id=current_assignment).first()
    s_ratio = current_assignment.student_ratio
    t_ratio = current_assignment.teacher_ratio
    t_points = current_assignment.points
    comments = Comments.objects.filter(submission=current_sub)
    if request.POST:
        comment = request.POST['comment']

        cur_user = request.user
        temp = Comments(submission=current_sub,
                        text=comment, comment_user=cur_user)
        temp.save()

    if current_assignment.grading_type is False:
        peer_marks = []
        # avg_peer_marks=None

        marks = 0
        total_marks = None
        ts_marks = None
        tt_marks = None
        context = None
        peer = AssignedPeers.objects.filter(
            assignment=current_assignment).filter(peer=cur_student)
        if len(peer) == 0:
            peer = peer.first()
        if peer is not None:
            for p in peer:
                temp = p.student_marks
                peer_marks.append(temp)
            teacher_marks = None
            if sub is not None:
                if sub.marks is not None:
                    teacher_marks = sub.marks
            avg_marks = None
            if len(peer_marks) != 0:
                count = 0
                for i in peer_marks:
                    if i is not None:
                        count += 1
                if count != 0:

                    for i in peer_marks:
                        if(i is not None):
                            marks = marks+i
                        print(marks)
                    marks = float(marks)/count
                    avg_marks = marks
                    marks = marks*(s_ratio/100)
                    if teacher_marks is not None:
                        total_marks = teacher_marks*(t_ratio/100)+marks
                ts_marks = round(t_points*(s_ratio/100), 1)
                tt_marks = round(t_points*(t_ratio/100), 1)
            if teacher_marks is not None:
                teacher_marks = round(teacher_marks, 1)
            if total_marks is not None:
                total_marks = round(total_marks, 1)

            # isNone = False
            # print(peer_marks)
            # for marks in peer_marks:
            #     if marks is None:
            #         isNone = True
            #         break

            # if isNone:
            #     avg_peer_marks = None
            # else:
            #     avg_peer_marks = round(average(peer_marks), 1)
            if(avg_marks != None):
                avg_peer_marks = round(avg_marks, 1)
            else:
                avg_peer_marks = None

            context = {
                'current_sub': current_sub,
                'files': submitted_files,
                'submitted_link': submitted_link,
                'submitted_doc_link': submitted_doc_link,
                'marks': round(marks, 1) if marks is not None else None,
                'ts_marks': ts_marks,
                'tt_marks': tt_marks,
                # 'teacher_marks': teacher_marks,
                'teacher_marks': teacher_marks,
                'total_marks': total_marks,
                't_points': t_points,
                'comments': comments,
                'count': count,
                'no_peers': no_peers,
                'peer_marks': peer_marks,
                'avg_peer_marks': avg_peer_marks,
                'classes' : all_classes,
                'joined' : joined_classes
            }
            # print(teacher_marks)
        else:
            if sub is not None:
                if sub.marks is not None:
                    teacher_marks = sub.marks
            marks = "No peers Assigned"
            context = {
                'current_sub': current_sub,
                'files': submitted_files,
                'submitted_link': submitted_link,
                'submitted_doc_link': submitted_doc_link,
                'marks': marks,
                'teacher_marks': teacher_marks,
                'tt_marks': current_assignment.points,
                'comments': comments,
                't_points': t_points,
                # 'count': count,
                # 'no_peers': no_peers,
                'classes' : all_classes,
                'joined' : joined_classes
            }
            # print(teacher_marks)
    else:
        marks = "No peergrading"
        context = {
            'current_sub': current_sub,
            'files': submitted_files,
            'submitted_link': submitted_link,
            'submitted_doc_link': submitted_doc_link,
            'marks': marks,
            'comments': comments,
            't_points': t_points,
            # 'count': count,
            # 'no_peers': no_peers,
            'classes' : all_classes,
            'joined' : joined_classes
        }

    return render(request, 'courses/cur_student_submission.html', context)


def cur_peer_submission(request, submission_id):
    cur_user = request.user
    current_sub = Submission.objects.get(pk=submission_id)
    student = current_sub.student
    if AssignedPeers.objects.filter(peer=student).filter(teacher=request.user).first() == None:
        return render(request, 'courses/access_denied.html')

    submitted_files = SubmittedFiles.objects.filter(submission_id=current_sub)
    embed_url = ""
    if SubmittedLink.objects.filter(submission_id=current_sub) != None:
        embed_url = SubmittedLink.objects.filter(submission_id=current_sub)
        temp = ""
        tmp = ""
        for link in embed_url:
            temp = link.youtube_link
            tmp = link.doc_link
        embed_url = temp
        embd_url = tmp
    all_classes = CreatedClasses.objects.filter(teacher=cur_user)
    joined_classes = JoinedClasses.objects.filter(student=cur_user)

    context = {
        'current_sub': current_sub,
        'files': submitted_files,
        'submitted_link': embed_url,
        'submitted_doc_link': embd_url,
        'classes':all_classes,
        'joined':joined_classes
    }
    return render(request, 'courses/cur_peer_submission.html', context)


def peers_assigned(request, assignment_id):

    cur_user = request.user
    all_classes = CreatedClasses.objects.filter(teacher=cur_user)
    joined_classes = JoinedClasses.objects.filter(student=cur_user)
    current_assignment = Assignments.objects.get(pk=assignment_id)

    print(current_assignment)

    created_class = current_assignment.class_id
    print(created_class)

    if JoinedClasses.objects.filter(student=cur_user).filter(class_id=created_class).first() == None:
        return render(request, 'courses/access_denied.html')
    if request.POST:
        print(request.POST)
        obj = AssignedPeers.objects.filter(peer=request.POST['cur_peer']).filter(
            assignment=current_assignment).filter(teacher=cur_user).first()
        print(obj)
        obj.student_marks = request.POST['marks']
        obj.question1 = request.POST['question1']
        obj.question2 = request.POST['question2']
        obj.question3 = request.POST['question3']
        obj.save()
    assign_peer = AssignedPeers.objects.filter(
        assignment=current_assignment).filter(teacher=cur_user)
    peer_sub = []
    for p in assign_peer:
        peer_user = p.peer
        obj = Submission.objects.filter(
            assignment_id=current_assignment).filter(student=peer_user).first()
        temp = [obj, p.student_marks]
        peer_sub.append(temp)
    context = {
        'assignment': current_assignment,
        'submissions': peer_sub,
        'classes':all_classes,
        'joined':joined_classes
    }
    #print(context)
    return render(request, 'courses/peers_assigned.html', context)


def cur_notice(request, notice_id):
    
    current_user = request.user
    # notice = notices.objects.get(pk=notice_id)

    # file = noticeFile.objects.filter(notice_id=notice)
    # document_link = ""
    # for link in file:
    #     document_link = link.document_link
    # context = {
    #     'document_link': document_link,
    #     'notice': notice,
    # }

    # return render(request, 'courses/cur_notice.html', context)
    all_classes = CreatedClasses.objects.filter(teacher=current_user)
    joined_classes = JoinedClasses.objects.filter(student=current_user)
    notice = notices.objects.get(pk=notice_id)
    files = noticeFile.objects.filter(notice_id=notice)
    context = {
        'files': files,
        'notices': notice,
        'classes': all_classes,
        'joined':joined_classes
    }

    return render(request, 'courses/cur_notice.html', context)
# Marksheet


def marksheet(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=marksheet.csv'

    # Create a csv writer
    writer = csv.writer(response)
    variable = []
    for i in range(1, Assignments.no_of_peers):
        variable.append("Peer "+str(i))
    # Designate the Model
    assignment = Assignments.objects.all()
    students = JoinedClasses.objects.all()
    # Add column headings to the csv file
    writer.writerow(['Student Email']+variable +
                    ['Teacher Marks', 'Average Marks'])

    # Loop Thu and output
    for st in students:
        writer.writerow([students.email, students.peer, ])

    return response


'''
@login_required
def cur_assignment_join(request, assignment_id):
    if request.POST:
        if request.POST['del_sub'] != '-1' and request.POST['del_sub'] != '0':
            del_file = request.POST['del_sub']
            dobj = SubmittedFiles.objects.get(sub=del_file)
            dobj.delete()
        elif request.POST['del_sub'] == '-1':
            current_user = request.user
            cur_assignment = Assignments.objects.get(pk=assignment_id)
            data = request.POST
            files = request.FILES.getlist('uploaded_file')
            obj = Submission.objects.filter(assignment_id=cur_assignment).filter(student=current_user).first()
            if obj is None:
                obj1 = Submission(assignment_id=cur_assignment, student=current_user)
                obj1.save()
                if obj1.sub_date > cur_assignment.due_date:
                    obj1.remark = "Late Submission"
                    obj1.save()
                for file in files:
                    temp = SubmittedFiles(sub=file, submission_id=obj1)
                    temp.save()
            else:
                for file in files:
                    obj.sub_date = timezone.now()
                    if obj.sub_date > cur_assignment.due_date:
                        obj.remark = "Late Submission"
                        obj.save()
                    obj.save()
                    temp = SubmittedFiles(sub=file, submission_id=obj)
                    temp.save()
        elif request.POST['act'] == '2':
            comment = request.POST['comment']
            cur_user = request.user
            curr_assignment = Assignments.objects.get(pk=assignment_id)
            submi = Submission.objects.filter(student=cur_user).filter(assignment_id=curr_assignment).first()
            cur_comment = Comments(text=comment, comment_user=cur_user, submission=submi)
            cur_comment.save()
    current_assignment = Assignments.objects.get(pk=assignment_id)
    no_peers = current_assignment.no_of_peers
    sub = Submission.objects.filter(student=request.user).filter(assignment_id=current_assignment).first()
    sub_files = SubmittedFiles.objects.filter(submission_id=sub)
    peers = AssignedPeers.objects.filter(peer=request.user).filter(assignment=current_assignment)
    comments = Comments.objects.filter(submission=sub)
    context = {
        'a': current_assignment,
        'sub': sub,
        'files': sub_files,
        'peers': peers,
        'comments': comments,
    }

    return render(request, 'courses/cur_assignment_join.html', context)'''
'''
@login_required
def cur_student_submission(request, submission_id):
    current_sub = Submission.objects.get(pk=submission_id)
    submitted_files = SubmittedFiles.objects.filter(submission_id=submission_id)
    comments = Comments.objects.filter(submission=current_sub)
    if request.POST:
        comment = request.POST['comment']
        cur_user = request.user
        temp = Comments(submission=current_sub, text=comment, comment_user=cur_user)
        temp.save()


    context = {
        'current_sub': current_sub,
        'files': submitted_files,
        'comments': comments,
    }
    return render(request, 'courses/cur_student_submission.html', context)
'''
