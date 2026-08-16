import os
import io
from fastapi import FastAPI, UploadFile, File, Form
from pypdf import PdfReader
from groq import Groq
from supabase import create_client, Client

# Safe environment loader for local & production
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Supabase setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Supabase setup
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Groq Client setup
groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(title="AI Career Copilot Backend")

@app.get("/")
def read_root():
    return {"status": "Success", "message": "Backend engine start ho gaya hai!"}

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    profile_id: str = Form(...),
    job_description: str = Form("")  # 🌟 NAYA: Job Description receive karne ke liye
):
    try:
        # 1. PDF se text nikalna
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        pdf_reader = PdfReader(pdf_file)
        
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        if not extracted_text.strip():
            extracted_text = "⚠️ Warning: PDF se koi text nahi mila."
            
        # 2. Database mein save karna
        supabase.table("resumes").insert({
            "profile_id": profile_id,
            "resume_text": extracted_text
        }).execute()

        # 3. Asli Groq AI (Llama-3) se Analysis
        ai_analysis = "AI analysis fail ho gaya."
        if len(extracted_text) > 50:
            try:
                print("🚀 DEBUG: Groq Llama-3 model chal raha hai...")
                
                # 🌟 NAYA: Agar JD di gayi hai, toh Prompt badal jayega
                if job_description.strip():
                    prompt = f"""
                    You are an expert ATS and Senior HR Recruiter.
                    Evaluate the following resume against this Job Description:
                    
                    Job Description:
                    {job_description}
                    
                    Give a report in this exact format:
                    🎯 ATS Match Score: [Give a match percentage out of 100%]
                    💪 Top 3 Strengths for this Role: [Bullet points]
                    ⚠️ Missing Keywords/Skills: [Bullet points showing what the resume lacks compared to the JD]
                    
                    Resume Text:
                    {extracted_text}
                    """
                else:
                    prompt = f"""
                    You are an expert ATS (Applicant Tracking System) and Senior HR Recruiter.
                    Analyze the following resume text and give me a general report in this exact format:
                    
                    🎯 ATS Score: [Give a general score out of 100]
                    💪 Top 3 Strengths: [Bullet points]
                    ⚠️ Areas of Improvement: [Bullet points what is missing or weak]
                    
                    Resume Text:
                    {extracted_text}
                    """
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant", # Aapka zinda model!
                )
                
                ai_analysis = chat_completion.choices[0].message.content
                
            except Exception as ai_error:
                print(f"AI Error: {ai_error}")
                ai_analysis = "Groq API me koi issue aaya. Check terminal."

        return {
            "status": "Success",
            "text_preview": extracted_text,
            "ai_analysis": ai_analysis
        }
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "status": "Error", 
            "text_preview": f"Error aaya: {str(e)}",
            "ai_analysis": ""
        }
@app.post("/hr-bot")
async def hr_mock_chat(
    resume_text: str = Form(""),
    user_answer: str = Form("")
):
    try:
        if not user_answer:
            prompt = f"""
            You are a strict but professional Technical HR Interviewer. 
            Review the following resume and ask ONE challenging interview question to start the mock round. 
            Focus on evaluating their core logical skills, problem-solving abilities, and concepts related to Database Management Systems, Theory of Computation, or C++ algorithmic structures if they align with the profile.
            Keep the response short (2-3 sentences max).
            
            Resume Text:
            {resume_text}
            """
        else:
            prompt = f"""
            You are a strict Technical HR Interviewer. 
            The candidate just answered your previous question with: "{user_answer}"
            
            Evaluate their answer strictly. Provide 1 sentence of constructive feedback, and then immediately ask the next challenging technical or behavioral question. 
            Keep it professional and conversational.
            """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        
        return {"status": "Success", "reply": chat_completion.choices[0].message.content}
        
    except Exception as e:
        print(f"HR Bot Error: {str(e)}")
        return {"status": "Error", "reply": "Connection to HR Bot failed. Please try again."}
