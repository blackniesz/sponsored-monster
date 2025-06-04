# sponsored-monster
# 📝 Agent do Pisania Artykułów Sponsorowanych

Inteligentny agent oparty na Claude Sonnet 4, który automatycznie tworzy artykuły sponsorowane z subtelnymi wzmiankami o wybranych klinikach medycznych.

## 🌟 Funkcjonalności

- **Research automatyczny** - wyszukiwanie informacji za pomocą Google Search API
- **Generowanie konspektu** - strukturyzacja artykułu na podstawie zebranych danych
- **Pisanie artykułów** - naturalny, ludzki styl pisania bez typowych frazesów AI
- **Subtelne wzmianki** - integracja informacji o klinikach w naturalny sposób
- **Edytor Markdown** - edycja i podgląd gotowych artykułów
- **Export** - pobieranie artykułów w formacie .md

## 🏥 Obsługiwane kliniki

- **Klinika Hospittal** - chirurgia plastyczna, medycyna estetyczna, dermatologia
- **Centrum Medyczne Gunarys** - diagnostyka, kardiologia, ginekologia  
- **Klinika Ambroziak** - medycyna estetyczna, anti-aging, kosmetologia

## 🚀 Uruchomienie lokalne

### Wymagania
- Python 3.8+
- Klucz API Anthropic (Claude)
- Opcjonalnie: Klucz Google Search API + Custom Search Engine ID

### Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/twoja-nazwa/article-writer-agent.git
cd article-writer-agent
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Uruchom aplikację:
```bash
streamlit run app.py
```

4. Otwórz przeglądarkę na `http://localhost:8501`

## ☁️ Deployment na Streamlit Cloud

### Krok 1: Przygotowanie repozytorium
1. Wrzuć wszystkie pliki na GitHub
2. Upewnij się, że masz: `app.py`, `requirements.txt`, `README.md`

### Krok 2: Deployment
1. Idź na [share.streamlit.io](https://share.streamlit.io)
2. Zaloguj się przez GitHub
3. Kliknij "New app"
4. Wybierz swoje repozytorium
5. Ustaw główny plik na `app.py`
6. Kliknij "Deploy!"

### Krok 3: Konfiguracja kluczy API
1. W panelu Streamlit Cloud idź do "Settings" → "Secrets"
2. Dodaj swoje klucze API w formacie TOML:

```toml
ANTHROPIC_API_KEY = "twój-klucz-anthropic"
GOOGLE_API_KEY = "twój-klucz-google"
GOOGLE_CSE_ID = "twoje-cse-id"
```

## 🔧 Konfiguracja API

### Anthropic API (wymagane)
1. Załóż konto na [console.anthropic.com](https://console.anthropic.com)
2. Wygeneruj klucz API
3. Wklej w aplikacji lub dodaj do secrets

### Google Search API (opcjonalne)
1. Idź do [Google Cloud Console](https://console.cloud.google.com)
2. Włącz Custom Search JSON API
3. Utwórz klucz API
4. Stwórz Custom Search Engine na [cse.google.com](https://cse.google.com)
5. Skopiuj Search Engine ID

## 📖 Jak używać

1. **Wpisz temat** - np. "Wpływ stresu na zdrowie skóry"
2. **Wybierz klinikę** - z rozwijanej listy
3. **Przeprowadź research** - kliknij przycisk researchu
4. **Stwórz konspekt** - na podstawie zebranych informacji
5. **Wygeneruj artykuł** - pełny proces generowania
6. **Edytuj i pobierz** - finalne poprawki w edytorze Markdown

## 🎯 Cechy artykułów

- **Naturalny styl** - jak napisane przez człowieka
- **Brak frazesów AI** - unikanie "kluczowy", "innowacyjny", "nowoczesny"
- **Lifestyleowy ton** - merytoryczny, ale przystępny
- **Hook we wstępie** - chwytliwe rozpoczęcie (3-4 zdania)
- **Subtelne wzmianki** - naturalne wplatanie informacji o klinikach
- **Struktura markdown** - czytelne formatowanie

## 🔒 Bezpieczeństwo

- Klucze API nie są przechowywane lokalnie
- Używaj Streamlit Secrets dla deployment
- Nie commituj kluczy do repozytorium

## 🛠️ Rozwój

Aplikacja jest modułowa i łatwa do rozszerzenia:

- Dodawanie nowych klinik w słowniku `CLINICS`
- Implementacja dodatkowych źródeł researchu
- Integracja z bazami danych
- Eksport do różnych formatów
- Harmonogram publikacji

## 📝 Licencja

MIT License - możesz swobodnie używać i modyfikować.

## 🤝 Kontakt

Jeśli masz pytania lub sugestie, śmiało twórz Issues na GitHubie!

---

**Zbudowano z użyciem:**
- [Streamlit](https://streamlit.io/) - framework do aplikacji
- [Claude Sonnet 4](https://www.anthropic.com/) - model językowy  
- [Google Search API](https://developers.google.com/custom-search/) - research
