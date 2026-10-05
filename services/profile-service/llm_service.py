import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Interview servisiyle aynı LLM_* değişkenleri; OpenAI uyumlu herhangi bir endpoint.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or None
LLM_MODEL = os.getenv("LLM_MODEL") or "google/gemma-4-31b"
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS") or 60)

_client = None


def _get_client() -> OpenAI:
    # Client ilk istekte oluşturulur: anahtar boşsa servis açılışta çökmez,
    # yalnızca analiz isteği hata döner.
    global _client
    if _client is None:
        if not LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY tanımlı değil")
        _client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=LLM_TIMEOUT_SECONDS)
    return _client


def analyze_job_and_cv(job_text: str, cv_text: str) -> dict:
    prompt = f"""
    Sen uzman, son derece titiz, objektif ve sektörden bağımsız çalışan bir İK Değerlendirme Yapay Zekasısın.
    Aşağıda adayın CV metni ve başvurduğu iş ilanı metni verilmiştir.
    
    Lütfen şu görevleri yap ve çıktıyı SADECE geçerli bir JSON olarak ver:
    
    1. İlanı parse et:
       - 'title': Pozisyon veya görev adı
       - 'seniority': Pozisyonun deneyim seviyesi (Stajyer, Giriş/Junior, Orta Düzey/Mid, Kıdemli/Senior, Yönetici, Uzman veya 'Belirtilmemiş')
       - 'technical_skills': İlanda adayın sahip olması beklenen tüm temel mesleki bilgi, uzmanlık, araç ve yetkinlikler listesi.
       - 'description': Pozisyonun kısa rol tanımı.
       
    2. CV ile ilanı karşılaştır ve analiz et:
       - 'cv_skills': Adayın CV'sinde açıkça geçen mesleki beceriler listesi.
       - 'matching_skills': İlanla örtüşen temel yetkinlik adları (Örn: ["Python", "PostgreSQL"]).
       - 'missing_skills': İlanda istenip CV'de bulunmayan yetkinlik adları (Örn: ["AWS", "Docker"]).
       - 'match_score': round((Eşleşen Sayısı / İlanda İstenen Toplam Sayı) * 100) formülüyle 0-100 arasında tam sayı skor.
       - 'feedback': Adaya yönelik 1-2 cümlelik genel değerlendirme.

    3. Kullanıcı Arayüzü Kartları İçin Detaylı Eşleşme Analizi:
       - 'strong_matches' (Güçlü Eşleşmeler): İlan ve CV'nin örtüştüğü alanlar için kategori ve açıklama objeleri listesi.
         Format: [{{"category": "Kategori Adı (Örn: Programlama Dilleri)", "description": "Örn: Python ve C# tecrübeniz ilanla birebir örtüşüyor."}}]
       - 'improvements' (Geliştirilmesi Gerekenler): İlanda istenip CV'de eksik olan alanlar için kategori ve açıklama objeleri listesi.
         Format: [{{"category": "Kategori Adı (Örn: Bulut Teknolojileri)", "description": "Örn: İlanda AWS tecrübesi isteniyor, CV'nizde bu alanda eksik var. Mülakatta bu konuya hazırlıklı olun."}}]

    İş İlanı Metni:
    \"\"\"{job_text}\"\"\"

    Adayın CV Metni:
    \"\"\"{cv_text}\"\"\"

    JSON Formatı:
    {{
        "job_details": {{
            "title": "...",
            "seniority": "...",
            "technical_skills": ["..."],
            "description": "..."
        }},
        "analysis": {{
            "cv_skills": ["..."],
            "match_score": 82,
            "matching_skills": ["..."],
            "missing_skills": ["..."],
            "feedback": "...",
            "strong_matches": [
                {{
                    "category": "Programlama Dilleri",
                    "description": "Python ve C# tecrübeniz ilanla birebir örtüşüyor."
                }}
            ],
            "improvements": [
                {{
                    "category": "Bulut Teknolojileri",
                    "description": "İlanda AWS tecrübesi isteniyor, CV'nizde bu alanda eksik var. Mülakatta bu konuya hazırlıklı olun."
                }}
            ]
        }}
    }}
    """

    response = _get_client().chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system", 
                "content": "You are a strict, objective HR evaluation engine. Always output strict JSON matching the exact requested format."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)