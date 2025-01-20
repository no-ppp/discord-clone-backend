from drf_spectacular.utils import OpenApiResponse



GET_NOTIFICATIONS_DOCS = {
    'summary': 'Lista powiadomień',
    'description': 'Pobiera listę wszystkich powiadomień dla użytkownika',
    'responses': {
        '200': OpenApiResponse(description='Lista powiadomień')
    }
}
DELETE_NOTIFICATION_DOCS = { 
    'summary': 'Usuwanie powiadomienia',
    'description': 'Usuwa powiadomienie',
    'responses': {
        '204': OpenApiResponse(description='Powiadomienie usunięte')
    }
}
MARK_AS_READ_DOCS = {
    'summary': 'Oznaczenie powiadomienia jako przeczytane',
    'description': 'Oznacza powiadomienie jako przeczytane',
    'responses': {
        '200': OpenApiResponse(description='Powiadomienie oznaczone jako przeczytane'),
        '404': OpenApiResponse(description='Powiadomienie nie znalezione')
    }
}
MARK_AS_READ_ALL_DOCS = {
    'summary': 'Oznaczenie powiadomień jako przeczytane',
    'description': 'Oznacza wszystkie powiadomienia jako przeczytane',
    'responses': {
        '200': OpenApiResponse(description='Wszystkie powiadomienia oznaczone jako przeczytane')
    }
}