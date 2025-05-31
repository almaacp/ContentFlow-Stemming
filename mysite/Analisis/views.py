from django.shortcuts import render
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from collections import Counter
import re
from urllib.parse import urlparse
from Analisis.utils import stem_text  

# Landing Page
def LandingPage(request):
    return render(request, 'landingpage.html')

# Halaman untuk menginput URL yang ingin dianalisis
def RecommendationURL(request):
    return render(request, 'recommendation-url.html')

# Halaman input untuk analisis URL
def AnalysisURL(request):
    return render(request, 'analysis-url.html')

# Hasil Analisis URL
stop_words = set(stopwords.words('indonesian') + stopwords.words('english'))

def calculate_score(title, headings, first_paragraph, content, images, alt_count, meta_content, keyword_list, internal_links, external_links):
    score = {}

    title_stemmed_words = re.findall(r'\b\w+\b', stem_text(title.lower()))
    first_paragraph_stemmed_words = re.findall(r'\b\w+\b', stem_text(first_paragraph.lower())) if first_paragraph else []

    title_length = len(title)
    heading_count = len(headings)
    word_count = len(content.split())

    if 50 <= title_length <= 60:
        score['Title Length'] = 10
    elif 45 <= title_length < 50 or 60 < title_length <= 65:
        score['Title Length'] = 5
    else:
        score['Title Length'] = 0

    if 2 <= heading_count <= 3:
        score['Heading Count'] = 10
    elif heading_count == 1:
        score['Heading Count'] = 5
    else:
        score['Heading Count'] = 0

    optimal_count = sum(1 for h in headings if 20 <= len(h.get_text().strip()) <= 70)
    if heading_count == 0:
        score['Heading Length'] = 0
    elif optimal_count == heading_count:
        score['Heading Length'] = 10
    elif optimal_count > 0:
        score['Heading Length'] = 5
    else:
        score['Heading Length'] = 0

    keyword_in_title_count = sum(1 for k in keyword_list if k.lower() in title_stemmed_words)
    if keyword_in_title_count == 1:
        score['Keyword in Title'] = 10
    elif keyword_in_title_count == 2:
        score['Keyword in Title'] = 5
    else:
        score['Keyword in Title'] = 0

    keyword_in_first_paragraph_count = sum(1 for k in keyword_list if k.lower() in first_paragraph_stemmed_words)
    if keyword_in_first_paragraph_count in [1, 2]:
        score['Keyword in First Paragraph'] = 10
    elif keyword_in_first_paragraph_count == 3:
        score['Keyword in First Paragraph'] = 5
    else:
        score['Keyword in First Paragraph'] = 0

    if 300 <= word_count <= 1500:
        score['Content Length'] = 10
    else:
        score['Content Length'] = 0

    if len(images) == 0:
        score['Alt Tag on Images'] = 0
    elif alt_count == len(images):
        score['Alt Tag on Images'] = 10
    elif alt_count > 0 > len(images):
        score['Alt Tag on Images'] = 5
    else:
        score['Alt Tag on Images'] = 0

    meta_has_keyword = any(k.lower() in meta_content.lower() for k in keyword_list) if meta_content else False
    if meta_content and meta_has_keyword:
        score['Meta Tag'] = 10
    elif meta_content:
        score['Meta Tag'] = 5
    else:
        score['Meta Tag'] = 0

    score['Internal Links'] = 10 if internal_links else 0
    score['External Links'] = 10 if external_links else 0

    total = sum(score.values())
    return total, score

def generate_recommendations(title, headings, first_paragraph, content, images, alt_count, meta_content, keyword_list, internal_links, external_links):
    recommendations = {}
    title_length = len(title)
    heading_count = len(headings)
    word_count = len(content.split())

    if title_length < 50:
        recommendations['Title Length'] = "Judul terlalu pendek, tambahkan detail penting untuk menarik pembaca."
    elif title_length > 60:
        recommendations['Title Length'] = "Judul terlalu panjang, ringkas menjadi 50-60 karakter tanpa menghilangka makna."
    else:
        recommendations['Title Length'] = "✓"

    if heading_count < 2:
        recommendations['Heading Count'] = "Jumlah heading masih sedikit, tambahkan heading lagi setidaknya hingga berjumlah 2 atau 3 heading untuk mempermudah pembaca memahami struktur artikel."
    elif heading_count > 3:
        recommendations['Heading Count'] = "Jumlah heading terlalu banyak, coba sederhanakan struktur artikel setidaknya hingga heading berjumlah 2 atau 3."
    elif heading_count == 0:
        recommendations['Heading Count'] = "Tidak ada heading ditemukan, tambahkan heading untuk membantu dalam memberikan informasi kepada pembaca."
    else:
        recommendations['Heading Count'] = "✓"

    if headings:
        recommendations['Heading Length'] = []
        for i, h in enumerate(headings, start=1):
            h_text = h.get_text().strip()
            h_length = len(h_text)
            if h_length < 20:
                recommendations['Heading Length'].append(
                    f"Heading {i} ('{h_text}') terlalu pendek ({h_length} karakter). Pertimbangkan untuk menambahkan lebih banyak kata agar lebih informatif."
                )
            elif h_length > 70:
                recommendations['Heading Length'].append(
                    f"Heading {i} ('{h_text}') terlalu panjang ({h_length} karakter). Pertimbangkan untuk mempersingkat agar lebih ringkas."
                )
        if not recommendations['Heading Length']:
            recommendations['Heading Length'].append("✓")
    else:
        recommendations['Heading Length'] = ["Tidak ada heading ditemukan, tambahkan heading untuk membantu dalam memberikan informasi kepada pembaca."]

    keyword_in_title_count = sum(title.lower().count(k.lower()) for k in keyword_list)
    if keyword_in_title_count > 1:
        recommendations['Keyword in Title'] = "Coba untuk tidak memasukkan kata kunci utama lebih dari sekali di judul untuk hasil SEO yang lebih baik."
    elif keyword_in_title_count < 1:
        recommendations['Keyword in Title'] = "Pastikan kata kunci utama muncul di judul artikel untuk meningkatkan relevansi SEO."
    else:
        recommendations['Keyword in Title'] = "✓"

    keyword_in_first_paragraph_count = sum(first_paragraph.lower().count(k.lower()) for k in keyword_list) if first_paragraph else 0
    if keyword_in_first_paragraph_count > 2:
        recommendations['Keyword in First Paragraph'] = "Cobalah untuk tidak menyebutkan kata kunci utama lebih dari dua kali di paragraf pertama."
    elif keyword_in_first_paragraph_count < 1:
        recommendations['Keyword in First Paragraph'] = "Tempatkan kata kunci utama di paragraf pertama untuk membantu mesin pencari memahami topik utama."
    else:
        recommendations['Keyword in First Paragraph'] = "✓"

    if word_count < 300:
        recommendations['Content Length'] = "Jumlah kata dalam konten terlalu sedikit karena kurang dari 300 kata. Tambahkan lebih banyak kata dalam konten untuk meningkatkan SEO artikel Anda."
    elif word_count > 1500:
        recommendations['Content Length'] = "Jumlah kata dalam konten terlalu banyak karena lebih dari 1500 kata. Pertimbangkan untuk mempersingkat agar lebih ringkas."
    else:
        recommendations['Content Length'] = "✓"

    if len(images) == 0:
        recommendations['Alt Tag on Images'] = "Tidak ada gambar ditemukan di halaman ini. Pertimbangkan untuk menambahkan gambar yang relevan dengan alt tag untuk meningkatkan aksesibilitas dan SEO."
    elif alt_count == len(images):
        recommendations['Alt Tag on Images'] = "✓"
    elif alt_count > 0:
        recommendations['Alt Tag on Images'] = "Beberapa gambar tidak memiliki alt tag. Pastikan semua gambar memiliki alt tag untuk meningkatkan aksesibilitas dan SEO."
    else:
        recommendations['Alt Tag on Images'] = "Tidak ada gambar yang memiliki alt tag. Tambahkan alt tag pada semua gambar untuk meningkatkan aksesibilitas dan SEO."

    if meta_content and any(k.lower() in meta_content.lower() for k in keyword_list):
        recommendations['Meta Tag'] = "✓"
    elif meta_content:
        recommendations['Meta Tag'] = "Meta description sudah ada, namun tidak mengandung keyword yang relevan. Pertimbangkan untuk menambahkan keyword agar lebih SEO-friendly."
    else:
        recommendations['Meta Tag'] = "Tidak ditemukan meta description. Tambahkan meta description yang mengandung keyword untuk meningkatkan visibilitas di mesin pencari."

    if internal_links:
        recommendations['Internal Links'] = "✓"
    else:
        recommendations['Internal Links'] = "Tidak ditemukan internal link. Sebaiknya menambahkan internal links untuk membantu meningkatkan navigasi situs dan SEO."

    if external_links:
        recommendations['External Links'] = "✓"
    else:
        recommendations['External Links'] = "Tidak ditemukan external link. Pertimbangkan untuk menambahkan link ke sumber eksternal yang relevan dan dapat dipercaya untuk meningkatkan otoritas halaman Anda."

    return recommendations

def determine_level(score):
    if score >= 80:
        return "Optimal", "optimal-green"
    elif score >= 60:
        return "Cukup Optimal", "optimal-yellow"
    elif score >= 40:
        return "Kurang Optimal", "optimal-orange"
    else:
        return "Tidak Optimal", "optimal-red"


def AnalysisResult(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url:
            return render(request, 'analysis-url.html', {'error': 'URL tidak boleh kosong.'})

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string if soup.title else 'No Title Found'
            body_content = soup.find('body')
            content = body_content.get_text(separator='\n', strip=True) if body_content else ''
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            meta_content = meta_tag['content'] if meta_tag else ''
            images = soup.find_all('img')
            alt_count = sum(1 for img in images if img.get('alt'))
            all_paragraphs = soup.find_all('p')
            first_paragraph = all_paragraphs[0].get_text(strip=True) if all_paragraphs else ''

            words_raw = re.findall(r'\b\w+\b', content.lower())
            filtered_words_raw = [w for w in words_raw if w not in stop_words]
            keywords_raw = Counter(filtered_words_raw).most_common(3)

            stemmed_content = stem_text(content.lower())
            words_stemmed = re.findall(r'\b\w+\b', stemmed_content)
            filtered_words_stemmed = [w for w in words_stemmed if w not in stop_words]
            keywords_stemmed = Counter(filtered_words_stemmed).most_common(3)

            page_domain = urlparse(url).netloc
            internal_links, external_links = [], []
            for link in soup.find_all('a', href=True):
                parsed_link = urlparse(link['href'])
                if not parsed_link.netloc or parsed_link.netloc == page_domain:
                    internal_links.append(link['href'])
                else:
                    external_links.append(link['href'])

            total_score_raw, score_raw = calculate_score(
                title, headings, first_paragraph, content,
                images, alt_count, meta_content,
                [k for k, _ in keywords_raw], internal_links, external_links
            )

            total_score_stemmed, score_stemmed = calculate_score(
                title, headings, first_paragraph, stemmed_content,
                images, alt_count, meta_content,
                [k for k, _ in keywords_stemmed], internal_links, external_links
            )

            level_raw, color_raw = determine_level(total_score_raw)
            level_stemmed, color_stemmed = determine_level(total_score_stemmed)

            recommendations = generate_recommendations(
                title, headings, first_paragraph, content,
                images, alt_count, meta_content,
                [k for k, _ in keywords_raw], internal_links, external_links
            )
            recommendations_stemmed = generate_recommendations(
                title, headings, first_paragraph, stemmed_content,
                images, alt_count, meta_content,
                [k for k, _ in keywords_stemmed], internal_links, external_links
            )

            result_data = {
                'url': url,
                'title': title,
                'content': content,
                'stemmed_content': stemmed_content,
                'keywords_raw': [k for k, _ in keywords_raw],
                'keywords_stemmed': [k for k, _ in keywords_stemmed],
                'criteria_scores_raw': score_raw,
                'criteria_scores_stemmed': score_stemmed,
                'total_score_raw': total_score_raw,
                'total_score_stemmed': total_score_stemmed,
                'optimization_level_raw': level_raw,
                'optimization_color_raw': color_raw,
                'optimization_level_stemmed': level_stemmed,
                'optimization_color_stemmed': color_stemmed,
                'recommendations': recommendations,
                'recommendations_stemmed': recommendations_stemmed,
            }

            return render(request, 'analysis-result.html', {'result': result_data})

        except requests.exceptions.RequestException as e:
            return render(request, 'analysis-url.html', {'error': f'Gagal mengambil data: {e}'})

    return render(request, 'analysis-url.html')

def FAQ(request):
    return render(request, 'faq.html')
