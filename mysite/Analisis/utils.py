from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Siapkan stemmer (caching ini penting biar cepat)
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def stem_text(text):
    """Mengembalikan hasil stemming dari teks."""
    return stemmer.stem(text)