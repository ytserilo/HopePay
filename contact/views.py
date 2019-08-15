from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from HopePay.celery import app
import smtplib, redis, json

asked_storage = redis.Redis(host='localhost', port=6379, db=6)

class Error(View):
    def get(self, request):
        return render(request, 'error.html')

class AskView(View):
    def get(self, request):
        result = self.ascked_test(request)
        return render(request, 'ask.html', context={
            'ascked': result
        })
    @app.task
    def send_mail(self, message, email):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("hopepay.my@gmail.com", "Zzzhbr1111")
        server.sendmail("hopepay.my@gmail.com", email, message.encode())
        server.quit()

    def valid(self, val):
        result = None
        if val == 'on':
            result = True
        else:
            result = False
        return result

    def ascked_test(self, request):
        try:
            user_token = str(request.COOKIES['csrftoken'])
            result = asked_storage.get(user_token)

            ascked = None

            if result != None:
                ascked = True
            else:
                ascked = False
            return ascked
        except:
            return False

    def append_data(self, question, yes='', no='', text=''):
        html = '\n'+question
        if yes != '' and yes:
            html += '\n {} \n'.format('Так')
            if text != '':
                html += '\n {} '.format(text)
        elif no != '' and no:
            html += '\n {} \n'.format('Ні')
            if text != '':
                html += '\n {} '.format(text)
        return html

    def post(self, request):
        data = request.POST
        first_yes = self.valid(data.get('first-yes'))
        first_not = self.valid(data.get('first-not'))
        first_text = data.get('first-text')

        second_yes = self.valid(data.get('second-yes'))
        second_not = self.valid(data.get('second-not'))
        second_text = data.get('second-text')

        third_yes = self.valid(data.get('third-yes'))
        third_not = self.valid(data.get('third-not'))
        third_text = data.get('third-text')

        four_yes = self.valid(data.get('four-yes'))
        four_not = self.valid(data.get('four-not'))
        four_text = data.get('four-text')

        five_yes = self.valid(data.get('five-yes'))
        five_not = self.valid(data.get('five-not'))
        five_text = data.get('five-text')

        six_text = data.get('six-text')
        sevent_text = data.get('seven-text')

        last_yes = self.valid(data.get('lasr-yes'))
        last_not = self.valid(data.get('last-not'))
        last_text = data.get('last-text')

        email = data.get('email')

        html = ''

        question1 = self.append_data(question='Вам подобається наша ідея ?',
                                     yes=first_yes,
                                     no=first_not,
                                     text=first_text)
        html += question1
        question2 = self.append_data(question='Ви бачили схожий сайт в інтернеті ?',
                                     yes=second_yes, no=second_not, text=second_text)
        html += question2
        question3 = self.append_data(question='Ви порекомендували б наш сайт своїм рідним чи друзям ?',
                                     yes=third_yes, no=third_not, text=third_text)
        html += question3
        question4 = self.append_data(question='Ви б користувалися даним сайтом постійно ?',
                                     yes=four_yes, no=four_not, text=four_text)
        html += question4
        question5 = self.append_data(question='Ви колись попадались на вудку шахраїв в інтернеті ?',
                                     yes=five_yes, no=five_not, text=five_text)

        html += question5
        html += 'Оцініть ідею від 0 до 10  ( '+ six_text +' )\n\n'
        html += 'Якщо хочете на пишіть побажання або корективи \n {}'.format(sevent_text)

        result = self.ascked_test(request)
        if result:
            return redirect('/chat/remittances/')
        else:
            self.send_mail(AskView, message=html, email='acemirskija@gmail.com')
            self.send_mail(AskView, message='Дякую Вам за ваш корисний відгук', email=email)
            asked_storage.set(str(request.COOKIES['csrftoken']), 'True')
            return redirect('/chat/remittances/')


class Main(View):
    def get(self, request):
        return render(request, 'index.html')
