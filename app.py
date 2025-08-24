import streamlit as st
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

def count_words_and_chars(text):
    """Count words and characters in the text"""
    if not text:
        return 0, 0
    
    # Count words (split by whitespace and filter empty strings)
    words = len([word for word in text.split() if word.strip()])
    
    # Count characters (including spaces)
    chars = len(text)
    
    return words, chars

def search_word_in_text(text, search_word):
    """Search for a specific word in the text and return count"""
    if not text or not search_word:
        return 0
    
    # Case-insensitive search using word boundaries
    pattern = r'\b' + re.escape(search_word.lower()) + r'\b'
    matches = re.findall(pattern, text.lower())
    
    return len(matches)

@st.cache_data
def download_nltk_data():
    """Download required NLTK data"""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)

def get_meaningful_words(text, top_n=5):
    """Extract meaningful words by removing stopwords and punctuation"""
    if not text:
        return []
    
    # Download NLTK data if needed
    download_nltk_data()
    
    # Get English stopwords
    stop_words = set(stopwords.words('english'))
    
    # Add common meaningless words that might not be in stopwords
    additional_stopwords = {'would', 'could', 'should', 'one', 'two', 'also', 'said', 'say', 'get', 'go', 'like', 'well', 'much', 'many', 'may', 'might', 'must', 'shall', 'will'}
    stop_words.update(additional_stopwords)
    
    # Use regex to find all words (same method as search function for consistency)
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter out stopwords and short words
    meaningful_words = [
        word for word in words 
        if word not in stop_words 
        and len(word) > 2
    ]
    
    # Count frequency
    word_freq = Counter(meaningful_words)
    return word_freq.most_common(top_n)

def main():
    st.set_page_config(
        page_title="Word Counter App",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("📝 Word Counter Application")
    st.markdown("---")
    
    # Text input area
    st.subheader("Enter your text:")
    user_text = st.text_area(
        "Type or paste your text here:",
        height=200,
        placeholder="Start typing your text here..."
    )
    
    # Word Search (always visible)
    st.subheader("🔍 Word Search")
    search_word = st.text_input(
        "Search for a specific word:",
        placeholder="Enter word to search..."
    )
    
    # Show search results only if both text and search word are provided
    if user_text and search_word:
        word_occurrences = search_word_in_text(user_text, search_word)
        
        if word_occurrences > 0:
            st.success(f"Found '{search_word}' {word_occurrences} time(s) in the text!")
        else:
            st.info(f"'{search_word}' not found in the text.")
    elif search_word and not user_text:
        st.warning("Please enter some text above to search for words.")
    elif user_text and not search_word:
        st.info("Enter a word above to search for it in your text.")
    
    # Submit button for detailed analysis
    submit_button = st.button("🔍 Analyze Text", type="primary", use_container_width=True)
    
    # Main analysis section
    if user_text and submit_button:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Text Statistics")
            word_count, char_count = count_words_and_chars(user_text)
            
            st.metric("Total Words", word_count)
            st.metric("Total Characters", char_count)
            st.metric("Characters (no spaces)", len(user_text.replace(" ", "")))
        
        # Additional features
        st.markdown("---")
        st.subheader("📈 Additional Analysis")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Most meaningful words (excluding stopwords)
            if user_text:
                try:
                    meaningful_words = get_meaningful_words(user_text, 5)
                    
                    if meaningful_words:
                        st.write("**Top 5 Meaningful Words:**")
                        st.caption("(Stopwords and common words removed)")
                        for word, count in meaningful_words:
                            st.write(f"• {word}: {count} times")
                    else:
                        st.write("**Top 5 Meaningful Words:**")
                        st.info("No meaningful words found after filtering stopwords")
                        
                except Exception as e:
                    st.write("**Top 5 Meaningful Words:**")
                    st.error("Error processing text with NLP. Falling back to basic word count.")
                    # Fallback to basic word counting
                    words = [word.lower().strip('.,!?";') for word in user_text.split() if word.strip()]
                    if words:
                        word_freq = Counter(words)
                        most_common = word_freq.most_common(5)
                        for word, count in most_common:
                            st.write(f"• {word}: {count} times")
        
        with col4:
            # Text statistics
            sentences = len([s for s in re.split(r'[.!?]+', user_text) if s.strip()])
            paragraphs = len([p for p in user_text.split('\n\n') if p.strip()])
            
            st.write("**Text Structure:**")
            st.write(f"• Sentences: {sentences}")
            st.write(f"• Paragraphs: {paragraphs}")
            if word_count > 0:
                avg_words_per_sentence = round(word_count / max(sentences, 1), 1)
                st.write(f"• Avg words per sentence: {avg_words_per_sentence}")
    
    elif user_text and not submit_button:
        st.info("👆 Click 'Analyze Text' button to see the analysis!")
    else:
        st.info("👆 Enter some text above and click 'Analyze Text' to see the analysis!")
    
    # Footer
    st.markdown("---")
    

if __name__ == "__main__":
    main()