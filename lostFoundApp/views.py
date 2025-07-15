from django.shortcuts import redirect, render
from lostFoundApp.models import Payment, ClaimOwner, PostModel, ResetPwdTokens, UserContact, UserFeedback, UserModel
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.db import connection
import time
import uuid
from Lost_Found_Main.mail_service import send_claim_acception_mail, send_claim_rejection_mail, send_forget_password_mail, send_point_purchase_mail, send_point_success_mail
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.http import HttpResponse

from django.template.loader import get_template

from xhtml2pdf import pisa
# Create your views here.

# generate pdf


def pdf_generated(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])
        try:
            claimer = ClaimOwner.objects.raw(
                'SELECT * FROM claim_owner WHERE claimerEmail = %s and STATUS = %s;', [user.email, 'Accepted'])[0]
            showUser = UserModel.objects.get(email=claimer.postPublisherEmail)
            post = PostModel.objects.get(id=claimer.postId)

            template_path = 'pdf_generated.html'
            context = {'user': user, 'showUser': showUser, 'post': post}
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="lost-and-found.pdf"' # for download
            response['Content-Disposition'] = 'filename="lost-and-found.pdf"'
            template = get_template(template_path)
            html = template.render(context)
            # create a pdf
            pisa_status = pisa.CreatePDF(
                html, dest=response)
            # if error then show some funy view
            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
            return response
        except:
            messages.error(request, 'You have no pdf to show.')
            return redirect('/')
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# home function


def home(request):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM user_posts ORDER BY id DESC;')
    allPosts = cursor.fetchall()
    cursor.close()
    search = "All"
    try:
        user = UserModel.objects.get(email=request.session['email'])
        if request.method == 'POST':
            search = request.POST.get('locatn')
            if search:
                print(search)
                if search == "All":
                    cursor = connection.cursor()
                    cursor.execute(
                        'SELECT * FROM user_posts ORDER BY id DESC;')
                    posts = cursor.fetchall()
                    cursor.close()
                    locations = []
                    for post in allPosts:
                        locations.append(post[5])
                    locations = list(dict.fromkeys(locations))
                    locations.sort()
                    return render(request, 'home.html', {'posts': posts, 'locations': locations, 'user': user, 'search': search})
                else:
                    cursor = connection.cursor()
                    cursor.execute(
                        'SELECT * FROM user_posts WHERE location = %s ORDER BY id DESC;', [search])
                    posts = cursor.fetchall()
                    cursor.close()
                    locations = []
                    for post in allPosts:
                        locations.append(post[5])
                    locations = list(dict.fromkeys(locations))
                    locations.sort()
                    return render(request, 'home.html', {'posts': posts, 'locations': locations, 'user': user, 'search': search})
            else:
                cursor = connection.cursor()
                cursor.execute(
                    'SELECT * FROM user_posts ORDER BY id DESC;')
                posts = cursor.fetchall()
                cursor.close()
                locations = []
                for post in allPosts:
                    locations.append(post[5])
                locations = list(dict.fromkeys(locations))
                locations.sort()
                return render(request, 'home.html', {'posts': posts, 'locations': locations, 'user': user, 'search': search})
        else:
            cursor = connection.cursor()
            cursor.execute(
                'SELECT * FROM user_posts ORDER BY id DESC;')
            posts = cursor.fetchall()
            cursor.close()
            locations = []
            for post in allPosts:
                locations.append(post[5])
            locations = list(dict.fromkeys(locations))
            locations.sort()
            return render(request, 'home.html', {'posts': posts, 'locations': locations, 'user': user, 'search': search})
    except:
        if request.method == 'POST':
            search = request.POST.get('locatn')#there may me changes occured
            if search:
                print(search)
                if search == "All":
                    cursor = connection.cursor()
                    cursor.execute(
                        'SELECT * FROM user_posts ORDER BY id DESC;')
                    posts = cursor.fetchall()
                    cursor.close()
                    locations = []
                    for post in allPosts:
                        locations.append(post[5])
                    locations = list(dict.fromkeys(locations))
                    locations.sort()
                    return render(request, 'home.html', {'posts': posts, 'locations': locations, 'search': search})
                else:
                    cursor = connection.cursor()
                    cursor.execute(
                        'SELECT * FROM user_posts WHERE location = %s ORDER BY id DESC;', [request.POST.get('locatn')])
                    posts = cursor.fetchall()
                    cursor.close()
                    locations = []
                    for post in allPosts:
                        locations.append(post[5])
                    locations = list(dict.fromkeys(locations))
                    locations.sort()
                    return render(request, 'home.html', {'posts': posts, 'locations': locations, 'search': search})
            else:
                cursor = connection.cursor()
                cursor.execute(
                    'SELECT * FROM user_posts ORDER BY id DESC;')
                posts = cursor.fetchall()
                cursor.close()
                locations = []
                for post in allPosts:
                    locations.append(post[5])
                locations = list(dict.fromkeys(locations))
                locations.sort()
                return render(request, 'home.html', {'posts': posts, 'locations': locations, 'search': search})
        else:
            cursor = connection.cursor()
            cursor.execute(
                'SELECT * FROM user_posts ORDER BY id DESC;')
            posts = cursor.fetchall()
            cursor.close()
            locations = []
            for post in allPosts:
                locations.append(post[5])
            locations = list(dict.fromkeys(locations))
            locations.sort()
            return render(request, 'home.html', {'posts': posts, 'locations': locations, 'search': search})


# authentication function

def authenticate(request):
    return render(request, 'authenticate.html')


# admin login function

def admin_login(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])
        if request.method == 'POST':
            if request.POST.get('adminUsername') and request.POST.get('adminPass'):
                username = request.POST.get('adminUsername')
                password = request.POST.get('adminPass')
                if username == 'pandya' and password == 'Pandya@123':
                    return redirect('admin-panel')
                else:
                    messages.error(request, 'Password incorrect...!')
                    return render(request, 'admin_login.html', {'user': user})
        return render(request, 'admin_login.html', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# admin panel function


def admin_panel(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])

        if user.email == 'rajsumitpandya@gmail.com':
            pendings = Payment.objects.raw(
                'SELECT * FROM payment WHERE STATUS = %s', ['Pending'])
            users = UserModel.objects.raw(
                'SELECT * FROM app_users WHERE email != %s', [request.session['email']])

            cursor = connection.cursor()
            cursor.execute(
                'SELECT * FROM claim_owner co, user_posts up WHERE co.postId = up.id and co.STATUS = %s ORDER BY co.id ASC;', ['Pending'])
            claims = cursor.fetchall()
            cursor.close()
            return render(request, 'admin_panel.html', {'user': user, 'pendings': pendings, 'claims': claims, 'users': users})
        else:
            messages.error(request, "Restricted! Only admin users can access.")
            return redirect('/', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# point add function (Admin Panel)


def point_add(request, token):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM app_users au, payment p WHERE au.email = p.email and p.id = %s ORDER BY p.id DESC', [token])

    pointuser = cursor.fetchall()
    cursor.close()
    try:
        user = UserModel.objects.get(email=request.session['email'])
        if user.email == 'rajsumitpandya@gmail.com':

            tuser = UserModel.objects.get(email=pointuser[0][18])

            tuser.point = str(int(tuser.point) + int(pointuser[0][21]))
            tuser.save()

            pointend = Payment.objects.get(id=token)
            pointend.status = "Done"
            pointend.save()

            send_point_success_mail(pointuser[0][18])

            messages.success(request, "Point added to " +
                            pointuser[0][17] + " user successfully.")
            return redirect('/admin-panel', {'user': user})
        else:
            messages.error(request, "Restricted! Only admin users can access.")
            return redirect('/', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('login')


# signup function

def signup(request):
    if request.method == 'POST':
        if request.POST.get('name') and request.POST.get('email') and request.POST.get('password'):
            saveUser = UserModel()
            saveToken = ResetPwdTokens()

            saveUser.name = request.POST.get('name')
            saveUser.email = request.POST.get('email')
            saveUser.password = make_password(request.POST.get('password'))
            saveUser.completeProfile = '25%'
            saveUser.point = '200'

            if saveUser.isExists():
                messages.error(
                    request, request.POST.get('email') + " email address already registered...! Please Log in.")
                # return render(request, 'authenticate.html', context)
                return redirect('../authenticate')
            else:
                saveUser.save()
                saveToken.user = saveUser
                saveToken.save()
                messages.success(
                    request, "Hello " + request.POST.get('name') + ", registration details saved successfully...! Please Log in now.")
                return redirect('../authenticate')
    else:
        return redirect('../authenticate')


# login function

def login(request):
    if request.method == 'POST':
        try:
            userDetail = UserModel.objects.get(
                email=request.POST.get('email'))
            if check_password(request.POST.get('password'), (userDetail.password)):
                request.session['email'] = userDetail.email
                return redirect('/')
            else:
                messages.error(
                    request, 'Password incorrect...!')
        except UserModel.DoesNotExist as e:
            messages.error(
                request, 'No user found of this email....!')
    return redirect('../authenticate')


# logout function

def logout(request):
    try:
        del request.session['email']
        messages.success(request, "Successfully logged out.")
    except:
        messages.error(request, "An error occurred. Try again.")
        return redirect('/')
    return redirect('/')


# privacy policy function

def privacy_policy(request):
    return render(request, 'privacy_policy.html')


# terms & conditions function

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

# view profile page


def view_profile(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])
        return render(request, 'view_profile.html', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# edit profile page


def edit_profile(request):
    if request.method == 'POST':
        user = UserModel.objects.get(email=request.session['email'])
        if request.POST.get('editName') and request.POST.get('editPhn') and request.POST.get('editLocation') and request.POST.get('editBio') and request.POST.get('editMessengerUrl') and request.POST.get('editWhatsappUrl'):

            user.name = request.POST.get('editName')
            user.phoneNumber = request.POST.get('editPhn')
            user.location = request.POST.get('editLocation')
            user.bio = request.POST.get('editBio')
            user.messengerUrl = request.POST.get('editMessengerUrl')
            user.whatsappUrl = request.POST.get('editWhatsappUrl')
            if request.POST.get('editTelegramUrl'):
                user.telegramUrl = request.POST.get('editTelegramUrl')
            user.completeProfile = '100%'

            # TODO: single photo file save
            if len(request.FILES) != 0:
                user.profileImg = request.FILES['editPhoto']
                user.AadharFrontImg = request.FILES['editAadharFront']
                user.AadharBackImg = request.FILES['editAadharBack']

            user.save()
            messages.success(
                request, "Your profile updated successfully...!")
            return redirect('view-profile')

    else:
        try:
            user = UserModel.objects.get(email=request.session['email'])
            return render(request, 'edit_profile.html', {'user': user})
        except:
            messages.error(request, 'You need to login first')
            return redirect('authenticate')

# contact function


def contact(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])

        if request.method == 'POST':
            if request.POST.get('txtname') and request.POST.get('txtEmail') and request.POST.get('txtMsg'):
                saveContact = UserContact()

                saveContact.messengerId = user.id
                saveContact.messengerName = user.name
                saveContact.messengerEmail = user.email
                saveContact.message = request.POST.get('txtMsg')

                saveContact.save()
                time.sleep(3)
                return redirect('/')
        else:
            return render(request, 'contact.html', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# feedback functon


def feedback(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])
        if request.method == 'POST':
            if request.POST.get('feedbackMsg'):
                saveFeedback = UserFeedback()

                saveFeedback.messengerId = user.id
                saveFeedback.messengerName = user.name
                saveFeedback.messengerEmail = user.email
                saveFeedback.message = request.POST.get('feedbackMsg')

                saveFeedback.save()
                return redirect('/')
        else:
            return render(request, 'feedback.html', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# reset password functon


def forget_password(request):
    try:
        if request.method == 'POST' and request.POST.get('resetEmail'):
            email = request.POST.get('resetEmail')

        if not UserModel.objects.filter(email=email).first():
            messages.error(request, 'No user found with this email.')
            return render(request, 'reset_password/forget-password.html')

        user_obj = UserModel.objects.get(email=email)
        token = str(uuid.uuid4())
        resetPwdToken_obj = ResetPwdTokens.objects.get(user=user_obj.id)
        resetPwdToken_obj.forget_password_token = token
        resetPwdToken_obj.save()
        send_forget_password_mail(user_obj.email, token)
        messages.success(request, 'An email has been sent to ' + user_obj.email +
                        '. If you don\'t find any email in your mailbox, please check spam folder.')
        return render(request, 'reset_password/forget-password.html')

    except Exception as e:
        print(e)
    return render(request, 'reset_password/forget-password.html')

# change password functon


def change_password(request, token):
    context = {}

    try:
        resetPwdToken_obj = ResetPwdTokens.objects.filter(
            forget_password_token=token).first()
        context = {'user_id': resetPwdToken_obj.user.id}

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.error(request, 'No user id found.')
                return render(request, f'reset_password/change-password/{token}/.html', context)

            if new_password != confirm_password:
                messages.error(request, 'both should be equal.')
                return render(request, f'reset_password/change-password/{token}/.html', context)

            user_obj = UserModel.objects.filter(id=user_id).first()
            user_obj.password = make_password(new_password)
            user_obj.save()
            messages.success(request, 'Password updated.')
            return render(request, 'reset_password/change-password.html', context)
        else:
            return render(request, 'reset_password/change-password.html', context)

    except Exception as e:
        print(e)
        messages.error(request, 'url has already been used.')
        return render(request, 'reset_password/change-password.html', context)

# write post function


def write_post(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])
        if user.completeProfile == '100%':
            if request.method == 'POST':
                if request.POST.get('title') and request.POST.get('location') and request.POST.get('description') and request.POST.get('datetime'):

                    savePost = PostModel()

                    savePost.publisherId = user.id
                    savePost.publisherName = user.name
                    savePost.title = request.POST.get('title')
                    savePost.description = request.POST.get('description')
                    savePost.location = request.POST.get('location')
                    savePost.lostDateTime = request.POST.get('datetime')

                    if len(request.FILES) != 0:
                        savePost.fileImg = request.FILES['fileImg']
                        savePost.fileSecretImg = request.FILES['fileSecretImg']

                    user.point = str(int(user.point) + 50)

                    user.save()
                    savePost.save()

                    messages.success(request, "Your post has been submitted!")
                    return redirect('/')
            else:
                return render(request, 'write_post.html', {'user': user})
        else:
            messages.error(request, "Complete your profile first!")
            return render(request, 'view_profile.html', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# edit post function


def edit_post(request, token):
    try:
        user = UserModel.objects.get(email=request.session['email'])
        post = PostModel.objects.get(id=token)
        if request.method == 'POST':
            if request.POST.get('title') and request.POST.get('location') and request.POST.get('description'):

                post.publisherId = user.id
                post.publisherName = user.name
                post.title = request.POST.get('title')
                post.description = request.POST.get('description')
                post.location = request.POST.get('location')

                post.save()

                messages.success(request, "Your post has been edited!")
                return redirect('/')
        else:
            return render(request, 'edit_post.html', {'user': user, 'post': post})
    except:
        messages.error(request, 'You need to login first')
        return redirect('authenticate')

# view post function


def view_post(request, token):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM app_users au, user_posts up WHERE au.id = up.publisherId and up.id = %s', [token])
    posts = cursor.fetchall()
    cursor.close()
    try:
        user = UserModel.objects.get(email=request.session['email'])
        return render(request, 'view_post.html', {'posts': posts, 'user': user})
    except:
        return render(request, 'view_post.html', {'posts': posts})

# claim owner function


# def claim_owner(request, token):
#     cursor = connection.cursor()
#     print(token)
#     cursor.execute(
#         'SELECT * FROM app_users au, user_posts up WHERE au.id = up.publisherId and up.id = %s', [token])
#     posts = cursor.fetchall()
#     print(posts)
#     cursor.close()
#     try:
#         user = UserModel.objects.get(email=request.session['email'])

#         if user.completeProfile == '100%':

#             claimOwner = ClaimOwner()

#             claimOwner.claimerId = user.id
#             claimOwner.claimerName = user.name
#             claimOwner.claimerEmail = user.email
#             claimOwner.postId = token
#             claimOwner.postPunlisherEmail = posts[0][2]
#             claimOwner.postPunlisherName = posts[0][18]
#             claimOwner.status = 'Pending'

#             if len(request.FILES) != 0:
#                 claimOwner.claimFileImg = request.FILES['secretPic']

#             claimOwner.save()

#             user.point = str(int(user.point) - 100)
#             user.save()

#             messages.success(
#                 request, "Your claim has been submitted! You will get updates through email.")
#             return redirect('/')
#         else:
#             messages.error(request, "Complete your profile first!")
#             return render(request, 'view_profile.html', {'user': user})
#     except:
#         messages.error(
#             request, "Something went wrong. Please try again later.")
#         return redirect('/')




def claim_owner(request, token):
    # Step 1: Check if the user is logged in (via session)
    print(token)
    if 'email' not in request.session:

        messages.error(request, "You need to be logged in to claim ownership.")
        return redirect('/login')

    try:
        # Step 2: Fetch the user and the post details from the database
        user = UserModel.objects.get(email=request.session['email'])
        # print(user)

        # Fetch the post details based on the token provided
        cursor = connection.cursor()
        cursor.execute(
            '''SELECT * FROM app_users au join  user_posts up on au.id = up.publisherId WHERE up.id = %s''', [token])
        posts = cursor.fetchall()
        # print(posts)
        cursor.close()

        if not posts:
            messages.error(request, "Post not found.")
            return redirect('/')

        # Step 3: Check if the user's profile is complete
        if user.completeProfile != '100%':
            messages.error(request, "Complete your profile first!")
            return render(request, 'view_profile.html', {'user': user})

        # Step 4: Create a ClaimOwner instance
        claim_owner = ClaimOwner(
            claimerId=user.id,
            claimerName=user.name,
            claimerEmail=user.email,
            postId=token,
            postPublisherEmail=posts[0][2],  # Assuming email is in first column
            postPublisherName=posts[0][18],   # Assuming name is in second column
            status='Pending',
        )

        # Step 5: Handle file upload if it exists
        if 'secretPic' in request.FILES:
            claim_owner.claimFileImg = request.FILES['secretPic']

        # Step 6: Save the claim
        claim_owner.save()

        # Step 7: Deduct points from the user
        if int(user.point) >= 100:
            user.point = str(int(user.point) - 100)
            user.save()
        else:
            messages.error(request, "You do not have enough points.")
            return redirect('/')

        # Step 8: Success message
        messages.success(request, "Your claim has been submitted! You will get updates through email.")
        return redirect('/')

    except UserModel.DoesNotExist:
        # Handle case where the user does not exist
        messages.error(request, "User not found. Please log in.")
        return redirect('/')

    except Exception as e:
        # Generic error handling for any unexpected issues
        messages.error(request, f"Something went wrong: {str(e)}")
        return redirect('/')





# claim owner ACCEPTION function


def claim_accept(request, token):
    try:
        claimOwner = ClaimOwner.objects.get(id=token)
        claimOwner.status = 'Accepted'
        claimOwner.save()

        user = UserModel.objects.get(email=claimOwner.postPublisherEmail)

        send_claim_acception_mail(user, claimOwner.claimerEmail)

        messages.success(request, "Claim has been accepted!")
        return redirect('admin-panel')
    except:
        messages.error(
            request, "Something went wrong. Please try again later.")
        return redirect('/')

# claim owner REJECTION function


def claim_reject(request, token):
    try:
        claimOwner = ClaimOwner.objects.get(id=token)
        claimOwner.status = 'Rejected'
        claimOwner.save()

        send_claim_rejection_mail(claimOwner.claimerEmail)

        messages.success(request, "Claim has been rejected!")
        return redirect('admin-panel')
    except:
        messages.error(
            request, "Something went wrong. Please try again later.")
        return redirect('/')

# point purchase function


def point_purchase(request):
    try:
        user = UserModel.objects.get(email=request.session['email'])

        if request.method == 'POST':
            if request.POST.get('inputName') and request.POST.get('inputEmail') and request.POST.get('phoneNumber') and request.POST.get('transactionId') and request.POST.get('inputPoint'):

                savePayment = Payment()

                savePayment.name = request.POST.get('inputName')
                savePayment.email = request.POST.get('inputEmail')
                savePayment.status = 'Pending'
                savePayment.phoneNumber = request.POST.get('phoneNumber')
                savePayment.transactionId = request.POST.get(
                    'transactionId')
                savePayment.point = request.POST.get('inputPoint')

                savePayment.save()
                send_point_purchase_mail(request.POST.get('inputName'))
                messages.success(
                    request, "Your point purchase request has been submitted. We will confirm you by email within an hour.")
                return render(request, 'point-purchase.html', {'user': user})
        else:
            return render(request, 'point-purchase.html', {'user': user})
    except:
        messages.error(request, 'You need to login first')
        return redirect('login')


# test html page for developers