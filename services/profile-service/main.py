import io
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from bson import ObjectId

from auth import get_current_user, create_dev_token
from database import cv_collection, job_collection, match_collection, ping_database
from llm_service import analyze_job_and_cv

app = FastAPI(
    title="Profile and CV Matching Service",
    description="Microservice for CV analysis, job matching, and interview preparation data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3011", "http://127.0.0.1:3011", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 1. SİSTEM VE GELİŞTİRİCİ KAPILARI ---

@app.get("/health", tags=["System"])
async def health_check():
    """Liveness probe: Servisin çalıştığını doğrular."""
    return {"status": "ok"}

@app.get("/ready", tags=["System"])
async def ready_check():
    """Readiness probe: MongoDB bağlantısını denetler."""
    db_alive = await ping_database()
    if not db_alive:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )
    return {
        "status": "ready",
        "database": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/dev/token", tags=["Development"])
def generate_dev_token(user_id: str = "test-user-123"):
    """Swagger'da test yapabilmek için geçici bearer token üretir."""
    token = create_dev_token(user_id=user_id)
    return {"access_token": token, "token_type": "bearer"}


# --- 2. CV & İLAN EŞLEŞTİRME VE ANLAMSAL ANALİZ SERVİSİ (AI / LLM) ---

@app.post("/api/v1/matches/analyze", tags=["Matching"])
async def analyze_match(
    cv_file: UploadFile = File(..., description="Adayın PDF formatındaki CV dosyası"),
    job_text: str = Form(..., description="İş ilanı metni"),
    user=Depends(get_current_user)
):
    user_id = user.get("sub", "default_user")

    # PDF kontrolü ve metin çıkarma
    if not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lütfen geçerli bir PDF dosyası yükleyin."
        )

    try:
        pdf_bytes = await cv_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        cv_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                cv_text += text + "\n"
        
        if not cv_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF dosyasından metin okunamadı veya dosya boş."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PDF okuma hatası: {str(e)}"
        )

    # LLM ile analiz
    try:
        llm_output = await run_in_threadpool(analyze_job_and_cv, job_text, cv_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Analiz Hatası: {str(e)}"
        )

    job_info = llm_output.get("job_details", {})
    analysis_info = llm_output.get("analysis", {})

    match_score = analysis_info.get("match_score", 0)
    matching_skills = analysis_info.get("matching_skills", [])
    missing_skills = analysis_info.get("missing_skills", [])
    feedback = analysis_info.get("feedback", "")
    strong_matches = analysis_info.get("strong_matches", [])
    improvements = analysis_info.get("improvements", [])
    
    # Adayın CV'sindeki tüm becerileri al, yoksa eşleşenleri koru
    cv_skills = analysis_info.get("cv_skills", matching_skills)

    # 1. İlanı MongoDB'ye kaydet
    job_id = f"job-{uuid4()}"
    job_title = job_info.get("title", "Yazılım Pozisyonu")
    
    job_doc = {
        "_id": job_id,
        "title": job_title,
        "seniority": job_info.get("seniority", "Junior"),
        "technical_skills": job_info.get("technical_skills", []),
        "description": job_info.get("description", job_text),
        "raw_text": job_text,
        "created_at": datetime.now(timezone.utc)
    }
    await job_collection.insert_one(job_doc)

    # 2. CV'yi MongoDB'ye kaydet
    cv_doc = {
        "user_id": user_id,
        "skills": cv_skills,
        "raw_text": cv_text,
        "uploaded_at": datetime.now(timezone.utc)
    }
    cv_result = await cv_collection.insert_one(cv_doc)

    # 3. Analiz sonucunu (Mockup arayüz kartları dahil) MongoDB'ye kaydet
    match_doc = {
        "user_id": user_id,
        "job_posting_id": job_id,
        "job_title": job_title,
        "cv_id": str(cv_result.inserted_id),
        "match_score": match_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "feedback": feedback,
        "strong_matches": strong_matches,
        "improvements": improvements,
        "created_at": datetime.now(timezone.utc)
    }
    insert_res = await match_collection.insert_one(match_doc)

    return {
        "match_id": str(insert_res.inserted_id),
        "job_posting_id": job_id,
        "job_title": job_title,
        "match_score": match_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "feedback": feedback,
        "strong_matches": strong_matches,
        "improvements": improvements
    }

@app.get("/api/v1/matches/history", tags=["Matching"])
async def get_match_history(user=Depends(get_current_user)):
    user_id = user.get("sub", "default_user")
    cursor = match_collection.find({"user_id": user_id}).sort("created_at", -1)
    history = []
    async for doc in cursor:
        history.append({
            "match_id": str(doc["_id"]),
            "job_posting_id": doc.get("job_posting_id"),
            "job_title": doc.get("job_title", "Belirtilmemiş Pozisyon"),
            "match_score": doc.get("match_score", 0),
            "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None
        })
    return history

@app.get("/api/v1/matches/{match_id}", tags=["Matching"])
async def get_match_detail(match_id: str, user=Depends(get_current_user)):
    user_id = user.get("sub", "default_user")
    try:
        doc = await match_collection.find_one({"_id": ObjectId(match_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz match_id.")
    
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kayıt bulunamadı.")
    doc["id"] = str(doc.pop("_id"))
    return doc


# --- 3. CV & İLAN ENTEGRASYON KAPILARI (MÜLAKAT SERVİSİ & UI İÇİN) ---

@app.get("/api/v1/cvs/latest", tags=["CV Operations"])
async def get_latest_cv(user=Depends(get_current_user)):
    """Giriş yapan kullanıcının en güncel CV'sini döner."""
    user_id = user.get("sub", "default_user")
    cv = await cv_collection.find_one({"user_id": user_id}, sort=[("uploaded_at", -1)])
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcıya ait CV bulunamadı.")
    cv["id"] = str(cv.pop("_id"))
    return cv

@app.get("/api/v1/users/{user_id}/cvs/latest", tags=["CV Operations"])
async def get_latest_cv_by_user_id(user_id: str, user=Depends(get_current_user)):
    """Mülakat servisi için geriye dönük uyumluluk kapısı."""
    cv = await cv_collection.find_one({"user_id": user_id}, sort=[("uploaded_at", -1)])
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcıya ait CV bulunamadı.")
    cv["id"] = str(cv.pop("_id"))
    return cv

@app.get("/api/v1/cvs/{cv_id}", tags=["CV Operations"])
async def get_cv_by_id(cv_id: str, user=Depends(get_current_user)):
    user_id = user.get("sub", "default_user")
    try:
        cv = await cv_collection.find_one({"_id": ObjectId(cv_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz cv_id.")
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV bulunamadı.")
    cv["id"] = str(cv.pop("_id"))
    return cv

@app.get("/api/v1/job-postings/{job_posting_id}", tags=["Job Postings"])
async def get_job_posting(job_posting_id: str, user=Depends(get_current_user)):
    job = await job_collection.find_one({"_id": job_posting_id})
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İş ilanı bulunamadı.")
    job["id"] = str(job.pop("_id"))
    return job