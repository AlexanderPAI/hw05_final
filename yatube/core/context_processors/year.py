from datetime import datetime


def year(request):
    """Добавляет в консекст переменную year с текущим годом"""
    return {
        'year': int(datetime.now().strftime('%Y'))
    }
