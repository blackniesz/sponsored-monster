import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional
import re

# Konfiguracja strony
st.set_page_config(
    page_title="Agent do Pisania Artykułów Sponsorowanych",
    page_icon="📝",
    layout="wide"
)

# Stałe konfiguracyjne
CLINICS = {
    "Klinika Hospittal": {
        "nazwa": "Klinika Hospittal",
        "opis": "innowacyjny szpital chirurgii plastycznej łączący najwyższe standardy medyczne z dbałością o naturalne efekty",
        "specjalizacje": ["chirurgia plastyczna", "chirurgia rekonstrukcyjna", "medycyna estetyczna", "zabiegi estetyczne"]
    },
    "Centrum Medyczne Gunarys": {
        "nazwa": "Centrum Medyczne Gunarys",
        "opis": "nowoczesna klinika oferująca kompleksową opiekę medyczną z indywidualnym podejściem do każdego pacjenta",
        "specjalizacje": ["chirurgia estetyczna", "ginekologia", "laseroterapia", "medycyna estetyczna", "blefaroplastyka", "profilaktyka zdrowotna"]
    },
    "Klinika Ambroziak": {
        "nazwa": "Klinika Ambroziak",
        "opis": "klinika z ponad 20-letnim doświadczeniem wyznaczająca trendy dermatologii klinicznej i estetycznej w Polsce",
        "specjalizacje": ["dermatologia kliniczna", "dermatologia estetyczna", "medycyna estetyczna", "kosmetologia", "autorskie kosmetyki Dr Ambroziak Laboratorium"]
    }
}

class ArticleWriter:
    def __init__(self):
        self.anthropic_api_key = None
        self.outline = []
        self.article_content = ""
        
    def set_api_key(self, anthropic_key: str):
        self.anthropic_api_key = anthropic_key
    
    def call_claude_api(self, messages: List[Dict], max_tokens: int = 2000) -> str:
        """Wywołuje API Claude Sonnet 4"""
        if not self.anthropic_api_key:
            return "Błąd: Brak klucza API Anthropic"
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.anthropic_api_key,
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': max_tokens,
                'messages': messages
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'content' in result and len(result['content']) > 0:
                return result['content'][0]['text']
            else:
                return "Błąd: Brak odpowiedzi od API"
                
        except Exception as e:
            return f"Błąd API: {str(e)}"
    
    def create_outline(self, topic: str, clinic: str, context: str = "") -> List[str]:
        """Tworzy konspekt artykułu"""
        clinic_info = CLINICS.get(clinic, {})
        
        context_section = f"\nDodatkowy kontekst: {context}" if context else ""
        
        prompt = f"""Stwórz zwięzły konspekt artykułu na temat: "{topic}"{context_section}

WAŻNE: Artykuł ma być krótki - maksymalnie 800 słów, więc konspekt musi być zwięzły!

Wymagania:
1. Artykuł ma być merytoryczny, ale przystępny i lifestyleowy
2. Musi zawierać subtelną wzmiankę o klinice: {clinic_info.get('nazwa', clinic)}
3. Konspekt powinien składać się z 4-5 głównych punktów (śródtytułów) - NIE WIĘCEJ!
4. Każdy punkt powinien być konkretny i interesujący
5. Nie używaj słów "kluczowy", "innowacyjny", "nowoczesny"
6. Struktura: Wstęp z hookiem + 4-5 śródtytułów + zakończenie

Zwróć tylko listę śródtytułów w formacie:
1. Tytuł pierwszego punktu
2. Tytuł drugiego punktu
etc.

Pamiętaj - to ma być artykuł lifestyleowy, nie medyczny podręcznik. Krótki i na temat!"""

        messages = [{"role": "user", "content": prompt}]
        response = self.call_claude_api(messages, 800)
        
        # Parsowanie odpowiedzi na listę śródtytułów
        outline_lines = [line.strip() for line in response.split('\n') if line.strip()]
        outline = []
        
        for line in outline_lines:
            # Usuwanie numeracji
            clean_line = re.sub(r'^\d+\.\s*', '', line)
            if clean_line and len(clean_line) > 10:  # Filtrowanie zbyt krótkich linii
                outline.append(clean_line)
        
        # Ograniczenie do maksymalnie 5 punktów
        self.outline = outline[:5]
        return self.outline
    
    def generate_article(self, topic: str, clinic: str, outline: List[str], context: str = "") -> str:
        """Generuje cały artykuł za jednym razem"""
        clinic_info = CLINICS.get(clinic, {})
        
        context_section = f"\nDodatkowy kontekst dla artykułu: {context}" if context else ""
        
        prompt = f"""Napisz artykuł lifestyleowy na temat: "{topic}"{context_section}

Konspekt artykułu:
{chr(10).join([f"- {point}" for point in outline])}

Informacje o klinice do subtelnej wzmianki:
- Nazwa: {clinic_info.get('nazwa', clinic)}
- Opis: {clinic_info.get('opis', '')}
- Specjalizacje: {', '.join(clinic_info.get('specjalizacje', []))}

WAŻNE WYMAGANIA:
1. Artykuł ma mieć MAKSYMALNIE 800 słów (około 5000-6000 znaków)
2. Zacznij od chwytliwego tytułu artykułu
3. Potem krótki, chwytliwy wstęp (2-3 zdania) z hookiem
4. Rozwiń każdy punkt z konspektu w zwięzłej formie (80-120 słów na sekcję)
5. Wzmiankę o klinice umieść naturalnie w jednej z sekcji (najlepiej w środkowej lub końcowej)
6. Zakończ krótkim podsumowaniem (2-3 zdania)
7. Używaj śródtytułów dla każdej sekcji
8. Naturalny, lifestyleowy ton - bez zwracania się bezpośrednio do czytelnika
9. Bez słów "kluczowy", "innowacyjny", "nowoczesny"
10. Bez metafor i sztucznych sformułowań AI

Format odpowiedzi:
# [Tytuł artykułu]

[Wstęp]

## [Śródtytuł 1]
[Treść sekcji 1]

## [Śródtytuł 2]
[Treść sekcji 2]

itd.

Napisz cały artykuł bez żadnych dodatkowych komentarzy."""

        messages = [{"role": "user", "content": prompt}]
        return self.call_claude_api(messages, 2500)

# Inicjalizacja aplikacji
if 'writer' not in st.session_state:
    st.session_state.writer = ArticleWriter()

if 'generated_article' not in st.session_state:
    st.session_state.generated_article = ""

# Interfejs użytkownika
st.title("📝 Agent do Pisania Artykułów Sponsorowanych")
st.markdown("---")

# Sekcja konfiguracji API
with st.sidebar:
    st.header("🔧 Konfiguracja API")
    
    # Sprawdzenie czy klucze są w secrets (Streamlit Cloud)
    anthropic_key_default = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, 'secrets') else ""
    
    anthropic_key = st.text_input(
        "Klucz API Anthropic (Claude)",
        type="password",
        value=anthropic_key_default,
        help="Wymagany do generowania treści"
    )
    
    if anthropic_key_default:
        st.success("🔑 Klucz Anthropic załadowany z secrets")
    
    if st.button("💾 Zapisz konfigurację"):
        st.session_state.writer.set_api_key(anthropic_key)
        st.success("Konfiguracja zapisana!")

# Główny interfejs
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 Parametry artykułu")
    
    # Pole tematu
    topic = st.text_input(
        "Temat artykułu",
        placeholder="np. Wpływ stresu na zdrowie skóry"
    )
    
    # Pole kontekstu (opcjonalne)
    context = st.text_area(
        "Dodatkowy kontekst (opcjonalne)",
        placeholder="np. Artykuł skierowany do kobiet 30+, skupić się na praktycznych poradach...",
        height=100
    )
    
    # Wybór kliniki
    clinic = st.selectbox(
        "Wybierz klinikę do subtelnej wzmianki",
        options=list(CLINICS.keys()),
        help="Klinika zostanie wspomniana w naturalny sposób w artykule"
    )
    
    # Informacje o wybranej klinice
    if clinic:
        clinic_info = CLINICS[clinic]
        st.info(f"**{clinic_info['nazwa']}** - {clinic_info['opis']}")

with col2:
    st.header("🔍 Generowanie")
    
    # Przycisk generowania konspektu
    if st.button("📝 Stwórz konspekt", disabled=not topic or not anthropic_key):
        if topic and anthropic_key:
            with st.spinner("Tworzę konspekt artykułu..."):
                outline = st.session_state.writer.create_outline(topic, clinic, context)
                st.success("Konspekt utworzony!")
                
                # Wyświetlenie konspektu
                st.subheader("📋 Konspekt artykułu:")
                for i, point in enumerate(outline, 1):
                    st.write(f"{i}. {point}")

# Sekcja generowania artykułu
if st.session_state.writer.outline:
    st.markdown("---")
    st.header("✍️ Generowanie artykułu")
    
    if st.button("🚀 Wygeneruj pełny artykuł", type="primary"):
        if anthropic_key and topic:
            with st.spinner("Generuję artykuł..."):
                article = st.session_state.writer.generate_article(
                    topic, clinic, st.session_state.writer.outline, context
                )
                st.session_state.generated_article = article
                st.success("🎉 Artykuł został wygenerowany!")

# Wyświetlenie i edycja artykułu
if st.session_state.generated_article:
    st.markdown("---")
    st.header("📄 Gotowy artykuł")
    
    # Statystyki artykułu
    article_text = st.session_state.generated_article
    word_count = len(article_text.split())
    char_count = len(article_text)
    char_count_no_spaces = len(article_text.replace(' ', ''))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Słowa", word_count, delta=f"{word_count - 800}" if word_count > 800 else None)
    with col2:
        st.metric("Znaki ze spacjami", char_count, delta=f"{char_count - 5000}" if char_count > 5000 else None)
    with col3:
        st.metric("Znaki bez spacji", char_count_no_spaces)
    
    # Ostrzeżenia o długości
    if word_count > 800:
        st.warning(f"⚠️ Artykuł ma {word_count} słów - przekroczony limit 800 słów.")
    elif word_count < 600:
        st.info(f"ℹ️ Artykuł ma {word_count} słów - możesz go rozbudować.")
    
    # Podgląd artykułu
    st.subheader("👁️ Podgląd artykułu:")
    
    # Podgląd w kontenerze z ramką
    with st.container():
        st.markdown(st.session_state.generated_article)
    
    # Przyciski akcji
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        # Pobieranie jako Markdown
        st.download_button(
            label="📥 Pobierz (.md)",
            data=st.session_state.generated_article,
            file_name=f"artykul_{topic.replace(' ', '_').replace('/', '_')}.md",
            mime="text/markdown"
        )
    
    with col2:
        # Pobieranie jako tekst
        st.download_button(
            label="📥 Pobierz (.txt)",
            data=st.session_state.generated_article,
            file_name=f"artykul_{topic.replace(' ', '_').replace('/', '_')}.txt",
            mime="text/plain"
        )
    
    with col3:
        if st.button("🗑️ Usuń artykuł i zacznij od nowa"):
            st.session_state.generated_article = ""
            st.session_state.writer.outline = []
            st.rerun()
    
    # Edytor (rozwijany)
    with st.expander("✏️ Edytuj artykuł"):
        edited_article = st.text_area(
            "Edytuj treść:",
            value=st.session_state.generated_article,
            height=500,
            help="Możesz edytować artykuł w formacie Markdown"
        )
        
        if st.button("💾 Zapisz zmiany"):
            st.session_state.generated_article = edited_article
            st.success("Zmiany zapisane!")
            st.rerun()

# Stopka
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Agent do Pisania Artykułów Sponsorowanych v2.0</p>
        <p>Stworzony z użyciem Streamlit i Claude Sonnet 4</p>
    </div>
    """,
    unsafe_allow_html=True
)
