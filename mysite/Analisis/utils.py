from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Siapkan stemmer 
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def stem_text(text):
    #Mengembalikan hasil stemming dari teks.
    return stemmer.stem(text)