from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, extend_schema
from .serializers import UserSerializer, FriendRequestSerializer

# Już istniejąca dokumentacja logowania
LOGIN_DOCS = {
    'summary': "Logowanie użytkownika",
    'description': "Loguje użytkownika i zwraca tokeny JWT oraz dane użytkownika",
    'request': {
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string'},
            },
            'required': ['email', 'password']
        }
    },
    'responses': {
        200: OpenApiResponse(
            description="Pomyślne logowanie",
            response={
                'type': 'object',
                'properties': {
                    'tokens': {
                        'type': 'object',
                        'properties': {
                            'access': {'type': 'string'},
                            'refresh': {'type': 'string'},
                        }
                    },
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'email': {'type': 'string'},
                            'username': {'type': 'string'},
                            'avatar': {'type': 'string', 'nullable': True},
                            'status': {'type': 'string', 'nullable': True},
                            'bio': {'type': 'string', 'nullable': True},
                            'is_online': {'type': 'boolean'},
                            'is_staff': {'type': 'boolean'}
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description="Błędne dane"),
        401: OpenApiResponse(description="Nieprawidłowe dane logowania")
    }
}

# Dokumentacja rejestracji
REGISTER_DOCS = {
    'summary': "Rejestracja użytkownika",
    'description': "Tworzy nowe konto użytkownika",
    'request': {
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string'},
                'password2': {'type': 'string'},
            },
            'required': ['email', 'password', 'password2']
        }
    },
    'responses': {
        201: OpenApiResponse(description="Użytkownik został utworzony"),
        400: OpenApiResponse(description="Błędne dane rejestracji")
    }
}

# Dokumentacja wylogowania
LOGOUT_DOCS = {
    'summary': "Wylogowanie użytkownika",
    'description': "Wylogowuje użytkownika i unieważnia token",
    'responses': {
        200: OpenApiResponse(description="Pomyślne wylogowanie"),
        400: OpenApiResponse(description="Błąd wylogowania")
    }
}

# Dokumentacja wysyłania zaproszenia do znajomych
SEND_FRIEND_REQUEST_DOCS = {
    'summary': "Wysyłanie zaproszenia do znajomych",
    'description': "Wysyła zaproszenie do znajomych do wybranego użytkownika",
    'parameters': [
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID użytkownika, do którego wysyłamy zaproszenie"
        ),
    ],
    'request': None,
    'responses': {
        200: OpenApiResponse(
            description="Zaproszenie wysłane",
            response={
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Zaproszenie wysłane'
                    }
                }
            }
        ),
        400: OpenApiResponse(
            description="Błąd wysyłania zaproszenia",
            response={
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Nie możesz wysłać zaproszenia do samego siebie'
                    }
                }
            }
        ),
        404: OpenApiResponse(description="Użytkownik nie znaleziony")
    }
}

# Dokumentacja akceptacji zaproszenia
ACCEPT_FRIEND_REQUEST_DOCS = {
    'summary': "Akceptacja zaproszenia",
    'description': "Akceptuje zaproszenie do znajomych od wybranego użytkownika",
    'parameters': [
        OpenApiParameter(
            name="pk",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID użytkownika, którego zaproszenie akceptujemy"
        ),
    ],
    'responses': {
        200: OpenApiResponse(
            description="Zaproszenie zaakceptowane",
            response={
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Zaproszenie zaakceptowane'
                    }
                }
            }
        ),
        404: OpenApiResponse(
            description="Nie znaleziono zaproszenia",
            response={
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Nie znaleziono oczekującego zaproszenia'
                    }
                }
            }
        ),
        400: OpenApiResponse(
            description="Błąd podczas akceptacji zaproszenia",
            response={
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string'
                    }
                }
            }
        )
    }
}

# Dokumentacja resetowania hasła
PASSWORD_RESET_DOCS = {
    'summary': "Żądanie resetowania hasła",
    'description': "Wysyła email z linkiem do resetowania hasła",
    'request': {
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
            },
            'required': ['email']
        }
    },
    'responses': {
        200: OpenApiResponse(
            description="Email z linkiem do resetowania hasła został wysłany"
        ),
        400: OpenApiResponse(description="Błędny email")
    }
}

# Dokumentacja potwierdzenia resetowania hasła
PASSWORD_RESET_CONFIRM_DOCS = {
    'summary': "Potwierdzenie resetowania hasła",
    'description': "Ustawia nowe hasło po resetowaniu",
    'request': {
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {'type': 'string'},
                'uidb64': {'type': 'string'},
                'password': {'type': 'string'},
                'password2': {'type': 'string'},
            },
            'required': ['token', 'uidb64', 'password', 'password2']
        }
    },
    'responses': {
        200: OpenApiResponse(description="Hasło zostało zmienione"),
        400: OpenApiResponse(description="Błędne dane"),
        404: OpenApiResponse(description="Nieprawidłowy token lub użytkownik")
    }
}

# Dokumentacja dla notyfikacji
NOTIFICATION_LIST_DOCS = {
    'summary': "Lista notyfikacji",
    'description': "Zwraca listę notyfikacji dla zalogowanego użytkownika",
    'parameters': [
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID notyfikacji"
        ),
    ],
    'responses': {
        200: OpenApiResponse(description="Lista notyfikacji"),
        401: OpenApiResponse(description="Brak autoryzacji")
    }
}

# Dokumentacja dla listy użytkowników
USER_LIST_DOCS = {
    'summary': "Lista użytkowników",
    'description': "Zwraca listę wszystkich użytkowników"
}

# Dokumentacja dla szczegółów użytkownika
USER_RETRIEVE_DOCS = {
    'summary': "Szczegóły użytkownika",
    'description': "Zwraca szczegółowe informacje o użytkowniku"
}

# Dokumentacja dla oczekujących zaproszeń
PENDING_REQUESTS_DOCS = {
    'summary': "Oczekujące zaproszenia",
    'description': "Zwraca listę oczekujących zaproszeń do znajomych"
}

# Dokumentacja dla odrzucenia zaproszenia
REJECT_FRIEND_REQUEST_DOCS = {
    'summary': "Odrzucenie zaproszenia",
    'description': "Odrzuca zaproszenie do znajomych"
}

# Dokumentacja dla danych zalogowanego użytkownika
ME_DOCS = {
    'summary': "Dane zalogowanego użytkownika",
    'description': "Zwraca szczegółowe informacje o zalogowanym użytkowniku",
    'responses': {
        200: UserSerializer,
        401: OpenApiResponse(description="Brak autoryzacji")
    }
}

# Dokumentacja dla sprawdzenia pojedynczego zaproszenia
GET_FRIEND_REQUEST_DOCS = {
    'summary': "Sprawdź pojedyncze zaproszenie",
    'description': "Zwraca szczegóły konkretnego zaproszenia do znajomych",
    'responses': {
        200: FriendRequestSerializer,
        404: OpenApiResponse(description="Nie znaleziono zaproszenia")
    }
}

# Dokumentacja dla listy znajomych
GET_FRIENDS_DOCS = {
    'summary': "Lista znajomych użytkownika",
    'description': "Zwraca listę aktywnych znajomych użytkownika"
}

# Dokumentacja dla szczegółów znajomości
FRIENDSHIP_STATUS_DOCS = {
    'summary': "Szczegóły znajomości",
    'description': "Zwraca szczegóły relacji znajomości między dwoma użytkownikami"
}

# Dokumentacja dla oznaczania notyfikacji jako przeczytanych
MARK_READ_DOCS = {
    'summary': "Oznacz jako przeczytane",
    'description': "Oznacza notyfikację jako przeczytaną"
}

# Dokumentacja dla oznaczania wszystkich notyfikacji jako przeczytanych
MARK_ALL_READ_DOCS = {
    'summary': "Oznacz wszystkie jako przeczytane",
    'description': "Oznacza wszystkie notyfikacje jako przeczytane"
}

# Dokumentacja dla liczby nieprzeczytanych notyfikacji
UNREAD_COUNT_DOCS = {
    'summary': "Liczba nieprzeczytanych",
    'description': "Zwraca liczbę nieprzeczytanych notyfikacji"
}

USER_UPDATE_DOCS = {
    'summary': "Aktualizacja danych użytkownika",
    'description': "Aktualizuje dane profilu użytkownika"
}

USER_DELETE_DOCS = {
    'summary': "Usunięcie konta",
    'description': "Usuwa konto użytkownika"
}

USER_CHANGE_PASSWORD_DOCS = {
    'summary': "Zmiana hasła",
    'description': "Zmienia hasło zalogowanego użytkownika"
}

UPDATE_STATUS_DOCS = {
    'summary': "Aktualizacja statusu użytkownika",
    'description': "Zmienia status użytkownika (online/offline/busy/away)",
    'request': {
        'content': {
            'application/json': {
                'example': {
                    'status': 'online'
                }
            }
        }
    },
    'responses': {
        200: OpenApiResponse(
            description="Status został zaktualizowany",
            response={
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'is_online': {'type': 'boolean'},
                    'last_online': {'type': 'string', 'format': 'date-time'}
                }
            }
        ),
        400: OpenApiResponse(description="Nieprawidłowy status")
    }
}

REMOVE_FRIEND_DOCS = {
    'summary': 'Usuń znajomego',
    'description': 'Usuwa użytkownika z listy znajomych',
    'responses': {
        200: OpenApiResponse(
            description="Znajomy został usunięty pomyślnie",
            response={
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Friend removed successfully'
                    }
                }
            }
        ),
        404: OpenApiResponse(
            description="Użytkownik nie został znaleziony"
        ),
        400: OpenApiResponse(
            description="Błędne żądanie"
        )
    }
}
