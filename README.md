# MassiveGameArchive

MassiveGameArchive ist eine Webplattform zum Teilen und Entdecken von Großgruppenspielen. Die Plattform ermöglicht es Spielleitern, Pädagogen und Gruppenbetreuern, ihre besten Spiele zu teilen und von der kollektiven Erfahrung der Community zu profitieren.

## Funktionen

- **Spielsammlung**: Entdecke eine umfangreiche Sammlung von Großgruppenspielen für verschiedene Altersgruppen, Teilnehmerzahlen und Anlässe
- **Materiallisten**: Jedes Spiel enthält detaillierte Materiallisten, damit du genau weißt, was du brauchst
- **Varianten**: Entdecke verschiedene Spielvariationen oder teile deine eigenen kreativen Anpassungen
- **Verbesserungsvorschläge**: Helfe mit, die Spiele kontinuierlich zu verbessern
- **Kommentare & Feedback**: Teile deine Erfahrungen und lerne von anderen Spielleitern
- **Bewertungssystem**: Finde schnell die besten und beliebtesten Spiele

## Technologie-Stack

- Django 5.2
- PostgreSQL (Produktionsumgebung)
- SQLite (Entwicklungsumgebung)
- Redis für Cache und Session-Verwaltung
- Bootstrap 5.3 für das Frontend

## Installation

1. Repository klonen:
   ```
   git clone https://github.com/yourusername/MassiveGameArchive.git
   cd MassiveGameArchive
   ```

2. Virtuelle Umgebung erstellen und aktivieren:
   ```
   python -m venv .venv
   source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate
   ```

3. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

4. Datenbank initialisieren:
   ```
   python manage.py migrate
   ```

5. Entwicklungsserver starten:
   ```
   python manage.py runserver
   ```

## Docker-Installation

Alternativ kannst du das Projekt mit Docker starten:

```
docker-compose up
```

## Projektkonfiguration

Die Hauptkonfiguration erfolgt über Umgebungsvariablen:

- `DATABASE_URL`: Verbindungs-URL zur Datenbank
- `CACHE_URL`: Verbindungs-URL zum Redis-Cache
- `SECRET_KEY`: Django Secret Key
- `DEBUG`: Debug-Modus (True/False)

## Projektstruktur

- `games/`: Django-App für die Spielverwaltung
- `users/`: Django-App für Benutzerprofile und Authentifizierung
- `templates/`: Projektweite Templates
- `static/`: Statische Dateien (CSS, JS, Bilder)

## Code-Stil

Unser Projekt folgt diesen Codierungs-Grundsätzen:
- Kurze, prägnante Docstrings
- Einfache, unkomplexe Funktionen
- Vermeidung von tiefen Verschachtelungen
- PEP 484 Typ-Annotationen

Details findest du in der `CODE_STYLE_GUIDE.md` Datei.

## Mitwirken

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Eröffne einen Pull Request

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe die [LICENSE](LICENSE) Datei für Details.

## Kontakt

Projektteam - [email@example.com](mailto:email@example.com)

Projektlink: [https://github.com/yourusername/MassiveGameArchive](https://github.com/yourusername/MassiveGameArchive)