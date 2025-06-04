import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional
import re
import os

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
        self.google_api_key = None
        self.google_cse_id = None
        self.research_data = []
        self.outline = []
        self.article_content = ""
        
    def set_api_keys(self, anthropic_key: str, google_key: str = None, cse_id: str = None):
        self.anthropic_api_key = anthropic_key
        self.google_api_key = google_key
        self.google_cse_id = cse_id
    
    def google_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Wykonuje wyszukiwanie Google i zwraca wyniki"""
        if not self.google_api_key or not self.google_cse_id:
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': num_results,
                'gl': 'pl',
                'hl': 'pl'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            results = response.json()
            search_results = []
            
            for item in results.get('items', []):
                search_results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', '')
                })
            
            return search_results
        except Exception as e:
            st.error(f"Błąd podczas wyszukiwania Google: {str(e)}")
            return []
    
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
    
    def conduct_research(self, topic: str, clinic: str) -> List[Dict]:
        """Przeprowadza research na dany temat"""
        # Przygotowanie zapytań wyszukiwania
        search_queries = [
            f"{topic} badania naukowe",
            f"{topic} statystyki Polska",
            f"{topic} eksperci opinie",
            f"{topic} najnowsze informacje 2024 2025"
        ]
        
        all_results = []
        
        # Wyszukiwanie Google (jeśli dostępne)
        if self.google_api_key and self.google_cse_id:
            for query in search_queries:
                results = self.google_search(query, 3)
                all_results.extend(results)
        
        # Filtrowanie i organizowanie wyników
        unique_results = []
        seen_urls = set()
        
        for result in all_results:
            if result['link'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['link'])
        
        # Ograniczenie do 10 najlepszych wyników
        self.research_data = unique_results[:10]
        return self.research_data
    
    def create_outline(self, topic: str, clinic: str, research_data: List[Dict]) -> List[str]:
        """Tworzy konspekt artykułu"""
        clinic_info = CLINICS.get(clinic, {})
        
        # Przygotowanie kontekstu dla Claude
        research_context = "\n".join([
            f"- {item['title']}: {item['snippet']}"
            for item in research_data[:5]  # Top 5 wyników
        ])
        
        prompt = f"""Stwórz zwięzły konspekt artykułu na temat: "{topic}"

Kontekst z badań:
{research_context}

WAŻNE: Artykuł ma być krótki - maksymalnie 800 słów, więc konspekt musi być zwięzły!

Wymagania:
1. Artykuł ma być merytoryczny, ale przystępny i lifestyleowy
2. Musi zawierać subtelną wzmiankę o klinice: {clinic_info.get('nazwa', clinic)}
3. Konspekt powinien składać się z 4-5 głównych punktów (śródtytułów) - NIE WIĘCEJ!
4. Każdy punkt powinien być konkretny i interesujący
5. Nie używaj słów "kluczowy", "innowacyjny", "nowoczesny"
6. Struktura: Krótki wstęp z hookiem + 4-5 śródtytułów + naturalne zakończenie

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
    
    def write_introduction(self, topic: str, clinic: str, outline: List[str]) -> str:
        """Pisze wstęp z hookiem"""
        clinic_info = CLINICS.get(clinic, {})
        
        prompt = f"""Napisz krótki, chwytliwy wstęp do artykułu na temat: "{topic}"

Konspekt artykułu:
{chr(10).join([f"- {point}" for point in outline])}

Wymagania:
1. MAKSYMALNIE 2-3 zdania (około 50-80 słów)
2. Zaczynamy od ciekawego hooka - faktu, pytania retorycznego lub zaskakującej informacji
3. Naturalny, lifestyleowy ton
4. Bez zwracania się bezpośrednio do czytelnika (bez "Ci", "Twój", "Ciebie")
5. Bez metafor i sztucznych sformułowań AI
6. Bez słów "kluczowy", "innowacyjny", "nowoczesny"

Napisz tylko wstęp, bez żadnych dodatkowych komentarzy."""

        messages = [{"role": "user", "content": prompt}]
        return self.call_claude_api(messages, 500)
    
    def write_section(self, section_title: str, topic: str, clinic: str, 
                     outline: List[str], written_content: str, 
                     current_section_index: int) -> str:
        """Pisze pojedynczą sekcję artykułu"""
        clinic_info = CLINICS.get(clinic, {})
        
        # Kontekst z researchu
        research_context = "\n".join([
            f"- {item['snippet']}"
            for item in self.research_data[:3]
        ])
        
        # Informacje o tym, co już napisano i co będzie
        context_info = f"""
Temat główny: {topic}
Konspekt całego artykułu: {outline}
Aktualnie piszemy sekcję {current_section_index + 1}: "{section_title}"

Już napisane sekcje:
{written_content[-500:] if written_content else "Tylko wstęp"}

Pozostałe do napisania:
{outline[current_section_index + 1:] if current_section_index + 1 < len(outline) else "To jest ostatnia sekcja"}
"""

        # Sprawdzenie, czy to odpowiednie miejsce na wzmiankę o klinice
        should_mention_clinic = (current_section_index == len(outline) // 2 or 
                               current_section_index == len(outline) - 1)
        
        clinic_instruction = ""
        if should_mention_clinic:
            clinic_instruction = f"""
WAŻNE: W tej sekcji umieść subtelną wzmiankę o {clinic_info.get('nazwa', clinic)} - {clinic_info.get('opis', '')}. 
Wzmianka powinna być naturalna i pasować do kontekstu, np. jako przykład dobrej praktyki czy miejsca, gdzie można uzyskać profesjonalną pomoc.
"""

        prompt = f"""Napisz treść sekcji "{section_title}" dla artykułu o tematyce: {topic}

{context_info}

Informacje z researchu:
{research_context}

{clinic_instruction}

WAŻNE OGRANICZENIA DŁUGOŚCI:
- Cały artykuł ma mieć maksymalnie 800 słów
- Ta sekcja powinna mieć 80-120 słów (około 2-3 akapity)
- Bądź zwięzły i konkretny

Wymagania stylistyczne:
1. Merytoryczna, ale przystępna i lifestyleowa
2. Bez zwracania się do czytelnika (bez "Ci", "Twój", "Ciebie")
3. Bez metafor i typowych sformułowań AI
4. Bez słów "kluczowy", "innowacyjny", "nowoczesny"
5. Jeśli to zasadne, użyj punktowania dla lepszej czytelności
6. Nie powtarzaj informacji już zawartych w poprzednich sekcjach
7. Napisz w naturalny, ludzki sposób
8. Bez dodatkowych komentarzy - tylko treść sekcji

Pamiętaj: to ma być część większego artykułu, więc płynnie nawiązuj do wcześniejszych treści."""

        messages = [{"role": "user", "content": prompt}]
        return self.call_claude_api(messages, 800)

# Inicjalizacja aplikacji
if 'writer' not in st.session_state:
    st.session_state.writer = ArticleWriter()

# Interfejs użytkownika
st.title("📝 Agent do Pisania Artykułów Sponsorowanych")
st.markdown("---")

# Sekcja konfiguracji API
with st.sidebar:
    st.header("🔧 Konfiguracja API")
    
    # Sprawdzenie czy klucze są w secrets (Streamlit Cloud)
    anthropic_key_default = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, 'secrets') else ""
    google_key_default = st.secrets.get("GOOGLE_API_KEY", "") if hasattr(st, 'secrets') else ""
    google_cse_default = st.secrets.get("GOOGLE_CSE_ID", "") if hasattr(st, 'secrets') else ""
    
    anthropic_key = st.text_input(
        "Klucz API Anthropic (Claude)",
        type="password",
        value=anthropic_key_default,
        help="Wymagany do generowania treści"
    )
    
    if anthropic_key_default:
        st.success("🔑 Klucz Anthropic załadowany z secrets")
    
    st.subheader("Google Search API (opcjonalne)")
    google_key = st.text_input(
        "Klucz API Google",
        type="password",
        value=google_key_default,
        help="Dla lepszego researchu"
    )
    
    google_cse = st.text_input(
        "Custom Search Engine ID",
        value=google_cse_default,
        help="ID wyszukiwarki Google"
    )
    
    if google_key_default and google_cse_default:
        st.success("🔍 Google Search API załadowany z secrets")
    
    if st.button("💾 Zapisz konfigurację"):
        st.session_state.writer.set_api_keys(anthropic_key, google_key, google_cse)
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
    st.header("🔍 Research i generowanie")
    
    # Przycisk researchu
    if st.button("🔎 Przeprowadź research", disabled=not topic):
        if topic:
            with st.spinner("Przeprowadzam research..."):
                research_results = st.session_state.writer.conduct_research(topic, clinic)
                st.success(f"Znaleziono {len(research_results)} źródeł!")
                
                # Wyświetlenie wyników researchu
                if research_results:
                    st.subheader("Znalezione źródła:")
                    for i, result in enumerate(research_results[:5], 1):
                        st.write(f"{i}. **{result['title']}**")
                        st.write(f"   {result['snippet'][:100]}...")
    
    # Przycisk generowania konspektu
    if st.button("📝 Stwórz konspekt", disabled=not topic or not anthropic_key):
        if topic and anthropic_key:
            with st.spinner("Tworzę konspekt artykułu..."):
                outline = st.session_state.writer.create_outline(
                    topic, clinic, st.session_state.writer.research_data
                )
                st.success("Konspekt utworzony!")
                
                # Wyświetlenie konspektu
                st.subheader("Konspekt artykułu:")
                for i, point in enumerate(outline, 1):
                    st.write(f"{i}. {point}")

# Sekcja generowania artykułu
if st.session_state.writer.outline:
    st.markdown("---")
    st.header("✍️ Generowanie artykułu")
    
    if st.button("🚀 Wygeneruj pełny artykuł", type="primary"):
        if anthropic_key and topic:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            full_article = ""
            total_steps = len(st.session_state.writer.outline) + 1
            
            # Generowanie wstępu
            status_text.text("Piszę wstęp...")
            intro = st.session_state.writer.write_introduction(
                topic, clinic, st.session_state.writer.outline
            )
            full_article += f"# {topic}\n\n{intro}\n\n"
            progress_bar.progress(1 / total_steps)
            
            # Generowanie sekcji
            for i, section_title in enumerate(st.session_state.writer.outline):
                status_text.text(f"Piszę sekcję: {section_title}")
                
                section_content = st.session_state.writer.write_section(
                    section_title, topic, clinic, 
                    st.session_state.writer.outline,
                    full_article, i
                )
                
                full_article += f"## {section_title}\n\n{section_content}\n\n"
                progress_bar.progress((i + 2) / total_steps)
                
                # Krótka pauza między sekcjami
                time.sleep(1)
            
            st.session_state.writer.article_content = full_article
            progress_bar.progress(1.0)
            status_text.text("Artykuł gotowy!")
            
            st.success("🎉 Artykuł został wygenerowany!")

# Wyświetlenie i edycja artykułu
if st.session_state.writer.article_content:
    st.markdown("---")
    st.header("📄 Gotowy artykuł")
    
    # Statystyki artykułu
    article_text = st.session_state.writer.article_content
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
        st.warning(f"⚠️ Artykuł ma {word_count} słów - to za dużo! Docelowo maksymalnie 800 słów.")
    if char_count > 7000:
        st.warning(f"⚠️ Artykuł ma {char_count} znaków - to za dużo! Docelowo 5000-7000 znaków.")
    
    # Edytor markdown
    edited_article = st.text_area(
        "Edytuj artykuł (Markdown):",
        value=st.session_state.writer.article_content,
        height=400,
        help="Możesz edytować artykuł w formacie Markdown"
    )
    
    # Lepszy podgląd artykułu w dwóch kolumnach
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Kod Markdown:")
        st.code(edited_article, language="markdown")
    
    with col2:
        st.subheader("👁️ Podgląd:")
        st.markdown(edited_article)
    
    # Przycisk do pobrania
    st.download_button(
        label="📥 Pobierz artykuł (.md)",
        data=edited_article,
        file_name=f"artykul_{topic.replace(' ', '_')}.md",
        mime="text/markdown"
    )

# Stopka
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Agent do Pisania Artykułów Sponsorowanych v1.0</p>
        <p>Stworzony z użyciem Streamlit i Claude Sonnet 4</p>
    </div>
    """,
    unsafe_allow_html=True
)
