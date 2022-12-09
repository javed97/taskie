from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Profile
import os, sys, logging
import random
from .publisher import Publisher
from loglibrary_x21171581.log_record import LogRecord 
from loglibrary_x21171581.logger import Logger
from loglibrary_x21171581.level import Level

logger = Logger.create()
logger.level = Level.ALL
def log_listener(record):
    print(record)
    sys.stdout.flush()

logger.on_record.listen(log_listener)

def log_listener_file(log_record: LogRecord):
    log_file_name = f'log-{log_record.time.strftime("%Y-%m-%d-%H")}.txt'
    with open(log_file_name, 'a+') as f:
        msg = f'{log_record.time} [{log_record.level.name}] {log_record.logger_name}: {log_record.message}'
        f.write(msg)
        f.write('\n')

logger.on_record.listen(log_listener_file)


publishermsg = Publisher()

def index(request):
    if request.user.is_authenticated:
        return redirect('boards')
    else:
        return redirect('signIn')


class SignIn(View):
    def get(self, request):
        if request.user.is_authenticated:
            logger.info("User Signed in")
            print("Logger test")
            return redirect('boards')
        else:
            return render(request, 'auth.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            publishermsg.send_SMS_message("+353892456469", "User authentication successfull !")
            return redirect('boards')

        else:
            response = JsonResponse({"error": "Invalid Credential"})
            response.status_code = 403
            return response


class SignUp(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('boards')
        else:
            return redirect('signIn')

    def post(self, request):
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            # Store profile photo on S3 bucket
            # photo = request.file['image'].name
            # print(photo);
            # upload_file("21171581taskmanager",photo);
            
            user = User.objects.create_user(username, email, password)
            user.save()

            login(request, user)
            
            # Send an SMS using SNS
            publishermsg.send_SMS_message("+353892456469", "Congratulations ! You have successfully signed up on Task Manager !")

            n = random.randint(16, 45)
            pf_url = f'/media/users/{n}.jpg'
            pf = Profile(user=user, profile_photo=pf_url)
            pf.save()

            return redirect('boards')

        except:
            response = JsonResponse({"error": "Duplicate User or Server error"})
            response.status_code = 403
            return response
            
# Fucntion to upload files on S3

# def upload_file(file_name, bucket, object_key=None):
#     """Upload a file to an S3 bucket

#     :param file_name: File to upload
#     :param bucket: Bucket to upload to
#     :param key: S3 object key. If not specified then file_name is used
#     :return: True if file was uploaded, else False
#     """

#     # If S3 key was not specified, use file_name
#     if object_key is None:
#         object_key = file_name

#     # Upload the file
#     s3_client = boto3.client('s3')
#     try:
#         response = s3_client.upload_file(file_name, bucket, object_key)
#         '''
#         # an example of using the ExtraArgs optional parameter to set the ACL (access control list) value 'public-read' to the S3 object
#         response = s3_client.upload_file(file_name, bucket, key, 
#             ExtraArgs={'ACL': 'public-read'})
#         '''
        
#     except ClientError as e:
#         logging.error(e)
#         return False
#     return True
    
class SignOut(View):
    def get(self, request):
        logout(request)
        return redirect('signIn')
