from django.shortcuts import render


def index(request):
    data = {'title': 'Главная страница!',
            'values': ['some', 'hello', '123'],
            'obj':{
                'clan': 'gangrel',
                'sect': 'camarilla',
                'generation': 13,
            }
            }
    # путь к файлу указывается исходя из того что вы уже находитесь в папке tamplates
    return render(request, 'main/main.html', data)
