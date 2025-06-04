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
        self.title = ""
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
    
    def create_outline(self, topic: str, clinic: str, context: str = "") -> Dict[str, any]:
        """Tworzy tytuł i konspekt artykułu"""
        clinic_info = CLINICS.get(clinic, {})
        
        context_section = f"\nDodatkowy kontekst: {context}" if context else ""
        
        prompt = f"""Stwórz tytuł i zwięzły konspekt artykułu na temat: "{topic}"{context_section}

WAŻNE: Artykuł ma być krótki - maksymalnie 800 słów, więc konspekt musi być zwięzły!

Wymagania:
1. Artykuł ma być merytoryczny, ale przystępny i lifestyleowy
2. Musi zawierać subtelną wzmiankę o klinice: {clinic_info.get('nazwa', clinic)}
3. Konspekt powinien składać się z 4-5 głównych punktów (śródtytułów) - NIE WIĘCEJ!
4. Każdy punkt powinien być konkretny i interesujący
5. Nie używaj słów "kluczowy", "innowacyjny", "nowoczesny"
6. Tytuł ma być chwytliwy i intrygujący

Zwróć w formacie:
TYTUŁ: [tutaj tytuł artykułu]

ŚRÓDTYTUŁY:
1. Tytuł pierwszego punktu
2. Tytuł drugiego punktu
etc.

Pamiętaj - to ma być artykuł lifestyleowy, nie medyczny podręcznik!"""

        messages = [{"role": "user", "content": prompt}]
        response = self.call_claude_api(messages, 800)
        
        # Parsowanie odpowiedzi
        lines = response.split('\n')
        title = ""
        outline = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("TYTUŁ:"):
                title = line.replace("TYTUŁ:", "").strip()
            elif re.match(r'^\d+\.', line):
                clean_line = re.sub(r'^\d+\.\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    outline.append(clean_line)
        
        # Ograniczenie do maksymalnie 5 punktów
        self.outline = outline[:5]
        self.title = title
        
        return {"title": title, "outline": outline}
    
    def write_introduction(self, title: str, topic: str, outline: List[str], context: str = "") -> str:
        """Pisze wstęp z hookiem"""
        context_section = f"\nKontekst artykułu: {context}" if context else ""
        
        prompt = f"""Napisz krótki, chwytliwy wstęp do artykułu o tytule: "{title}"
Temat: {topic}{context_section}

Konspekt artykułu:
{chr(10).join([f"- {point}" for point in outline])}

Wymagania:
1. MAKSYMALNIE 2-3 zdania (około 50-80 słów)
2. Zaczynamy od ciekawego hooka - faktu, pytania retorycznego lub zaskakującej informacji
3. Naturalny, lifestyleowy ton
4. Bez zwracania się bezpośrednio do czytelnika (bez "Ci", "Twój", "Ciebie")
5. Bez metafor i sztucznych sformułowań AI
6. Ma płynnie wprowadzać w temat artykułu

Napisz tylko wstęp, bez żadnych dodatkowych komentarzy."""

        messages = [{"role": "user", "content": prompt}]
        return self.call_claude_api(messages, 500)
    
    def write_section(self, section_title: str, section_index: int, 
                     title: str, topic: str, clinic: str, outline: List[str], 
                     written_content: str, context: str = "") -> str:
        """Pisze pojedynczą sekcję artykułu"""
        clinic_info = CLINICS.get(clinic, {})
        
        # Co już napisano
        previous_sections = outline[:section_index]
        current_section = outline[section_index]
        remaining_sections = outline[section_index + 1:]
        
        # Sprawdzenie, czy to odpowiednie miejsce na wzmiankę o klinice
        should_mention_clinic = (section_index == len(outline) // 2 or 
                               section_index == len(outline) - 1)
        
        clinic_instruction = ""
        if should_mention_clinic:
            clinic_instruction = f"""
WAŻNE: W tej sekcji umieść subtelną wzmiankę o {clinic_info.get('nazwa', clinic)} - {clinic_info.get('opis', '')}. 
Wzmianka powinna być naturalna i pasować do kontekstu.
Specjalizacje kliniki: {', '.join(clinic_info.get('specjalizacje', []))}
"""

        context_section = f"\nKontekst artykułu: {context}" if context else ""

        prompt = f"""Napisz treść sekcji "{section_title}" dla artykułu o tytule: "{title}"
Temat główny: {topic}{context_section}

Informacje o strukturze:
- Już napisane sekcje: {previous_sections if previous_sections else 'tylko wstęp'}
- Obecna sekcja: {current_section}
- Pozostałe sekcje: {remaining_sections if remaining_sections else 'to ostatnia sekcja'}

Fragment tego, co już napisano (koniec):
{written_content[-400:] if len(written_content) > 400 else written_content}

{clinic_instruction}

WAŻNE OGRANICZENIA:
- Ta sekcja powinna mieć 100-150 słów (2-3 krótkie akapity)
- NIE powtarzaj informacji z wcześniejszych sekcji
- Bądź konkretny i podawaj praktyczne informacje

Wymagania stylistyczne:
1. Merytoryczna, ale przystępna treść
2. Bez zwracania się do czytelnika (bez "Ci", "Twój")
3. Naturalny, płynny język
4. Możesz użyć punktowania jeśli to zasadne
5. Pamiętaj o kontekście - co już było, co będzie

Napisz tylko treść sekcji, bez tytułu i dodatkowych komentarzy."""

        messages = [{"role": "user", "content": prompt}]
        return self.call_claude_api(messages, 800)
    
    def write_conclusion(self, title: str, topic: str, outline: List[str], 
                        written_content: str, context: str = "") -> str:
        """Pisze zakończenie artykułu"""
        context_section = f"\nKontekst artykułu: {context}" if context else ""
        
        prompt = f"""Napisz krótkie zakończenie artykułu o tytule: "{title}"
Temat: {topic}{context_section}

Sekcje artykułu:
{chr(10).join([f"- {point}" for point in outline])}

WAŻNE: 
- Zakończenie ma mieć MAKSYMALNIE 2-3 zdania
- Podsumuj główną myśl artykułu
- Zostaw czytelnika z wartościową refleksją
- NIE powtarzaj tego, co już było
- Naturalny ton, bez patosu

Napisz tylko zakończenie, bez dodatkowych komentarzy."""

        messages = [{"role": "user", "content": prompt}]
        return self.call_claude_api(messages, 300)

# Inicjalizacja aplikacji
if 'writer' not in st.session_state:
    st.session_state.writer = ArticleWriter()
    # Automatyczne ustawienie klucza API z secrets
    if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
        st.session_state.writer.set_api_key(st.secrets["ANTHROPIC_API_KEY"])

if 'generated_article' not in st.session_state:
    st.session_state.generated_article = ""

# Sprawdzenie dostępności klucza API
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, 'secrets') else ""

# Interfejs użytkownika
st.title("📝 Agent do Pisania Artykułów Sponsorowanych")
st.markdown("---")

# Informacja o statusie API w sidebarze
with st.sidebar:
    st.header("📊 Status")
    if anthropic_key:
        st.success("✅ API Claude aktywne")
    else:
        st.error("❌ Brak klucza API w secrets")

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
            with st.spinner("Tworzę tytuł i konspekt artykułu..."):
                result = st.session_state.writer.create_outline(topic, clinic, context)
                st.success("✅ Konspekt gotowy!")
                
                # Wyświetlenie tytułu i konspektu
                if result["title"]:
                    st.subheader("📌 Tytuł artykułu:")
                    st.info(result["title"])
                
                st.subheader("📋 Konspekt artykułu:")
                for i, point in enumerate(result["outline"], 1):
                    st.write(f"{i}. {point}")

# Sekcja generowania artykułu
if st.session_state.writer.outline and st.session_state.writer.title:
    st.markdown("---")
    st.header("✍️ Generowanie artykułu")
    
    if st.button("🚀 Wygeneruj pełny artykuł", type="primary"):
        if anthropic_key and topic:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Rozpoczynamy od tytułu
            full_article = f"# {st.session_state.writer.title}\n\n"
            total_steps = len(st.session_state.writer.outline) + 2  # +2 dla wstępu i zakończenia
            
            # Generowanie wstępu
            status_text.text("📝 Piszę wstęp...")
            intro = st.session_state.writer.write_introduction(
                st.session_state.writer.title, topic, 
                st.session_state.writer.outline, context
            )
            full_article += intro + "\n\n"
            progress_bar.progress(1 / total_steps)
            time.sleep(0.5)
            
            # Generowanie sekcji
            for i, section_title in enumerate(st.session_state.writer.outline):
                status_text.text(f"✏️ Piszę sekcję {i+1}/{len(st.session_state.writer.outline)}: {section_title[:30]}...")
                
                section_content = st.session_state.writer.write_section(
                    section_title, i, st.session_state.writer.title,
                    topic, clinic, st.session_state.writer.outline,
                    full_article, context
                )
                
                full_article += f"## {section_title}\n\n{section_content}\n\n"
                progress_bar.progress((i + 2) / total_steps)
                time.sleep(0.5)
            
            # Generowanie zakończenia
            status_text.text("🎯 Piszę zakończenie...")
            conclusion = st.session_state.writer.write_conclusion(
                st.session_state.writer.title, topic,
                st.session_state.writer.outline, full_article, context
            )
            full_article += conclusion
            
            st.session_state.generated_article = full_article
            progress_bar.progress(1.0)
            status_text.text("✅ Artykuł gotowy!")
            
            st.success("🎉 Artykuł został wygenerowany!")
            st.balloons()

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
