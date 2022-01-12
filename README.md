Repozytorium zawiera dwie aplikacje - backend i frontend - stworzone w języku Python, we frameworku FastAPI.\
Aplikacje komunikują się ze sobą poprzez REST API. 

Przed uruchomieniem projektu, w folderze każdej aplikacji należy umieścić plik .env. Zmienne:
- backend:
  - SECRET_KEY (klucz używany do podpisu JWT)
  - ALGORITHM (algorytm używany do podpisu JWT)
  - DATABASE_URL (url do bazy danych)
  - MEDIA_DIR (folder, w którym zapisywane będą pliki przesyłane przez użytkowników)
  - SENDGRID_API_KEY (klucz API klienta pocztowego Sendgrid)
  - MAIN_EMAIL_TEMPLATE (kod wykorzystywanego przez Sendgrid szablonu)
  - FRONTEND_URL (adres strony wpisywany przez użytkownika w przeglądarkę, bez slasha na końcu)
  - BACKEND_DOMAIN (domena backendu, np. backend - jak w pliku compose)
- frontend:
  - FRONTEND_URL (adres strony wpisywany przez użytkownika w przeglądarkę, bez slasha na końcu)
  - FRONTEND_DOMAIN (domena frontendu - powinna być zgodna z urlem)
  - BACKEND_URL (adres backendu)
