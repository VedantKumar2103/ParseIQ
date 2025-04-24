import streamlit as st
import nltk
import spacy
nltk.download('stopwords')
spacy.load('en_core_web_sm')
import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import pafy
import plotly.express as px
import youtube_dl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# ML Model for Resume Classification
def train_resume_classifier():
    resumes = [
        "machine learning deep learning tensorflow keras pytorch data science",
        "python django flask react javascript web development",
        "android kotlin java mobile development",
        "ios swift xcode mobile development",
        "ui ux design figma adobe xd prototyping"
    ]
    labels = ['Data Science', 'Web Development', 'Android Development', 'IOS Development', 'UI-UX Development']
    
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(resumes, labels)
    return model

try:
    model = joblib.load('resume_classifier.joblib')
except:
    model = train_resume_classifier()
    joblib.dump(model, 'resume_classifier.joblib')

def classify_resume(text):
    return model.predict([text])[0]

# Profile-Specific Cover Letter Generator
cover_letter_templates = {
    "Data Science": """
Dear {hiring_manager},

I'm excited to apply for the {job_title} position at {company_name}. With my {experience_level} background in data science and skills in {top_skills}, I'm confident I can contribute to your team.

Key qualifications:
- Developed {project_count} ML models using {top_skills}
- Achieved {achievement} in data analysis
- Strong skills in {skills}

I'd welcome the opportunity to discuss how I can help with {job_requirement}.

Sincerely,
{name}
""",
    "Web Development": """
Dear {hiring_manager},

As a {experience_level} web developer specializing in {top_skills}, I'm eager to apply for the {job_title} role at {company_name}.

Why I'm a great fit:
- Built {project_count} web applications using {top_skills}
- Experience with {web_tech}
- Strong problem-solving skills

Let's schedule a time to discuss this opportunity.

Best regards,
{name}
""",
    "default": """
Dear Hiring Manager,

I'm excited to apply for the {job_title} position. My skills in {skills} align well with your needs.

Sincerely,
{name}
"""
}

def generate_cover_letter(resume_data, job_title="", company_name="", job_description=""):
    predicted_field = classify_resume(resume_data.get("resume_text", ""))
    template = cover_letter_templates.get(predicted_field, cover_letter_templates["default"])
    
    skills = resume_data.get('skills', [])
    top_skills = ", ".join(skills[:3]) if skills else "relevant skills"
    
    return template.format(
        name=resume_data.get('name', 'Your Name'),
        hiring_manager="Hiring Manager",
        job_title=job_title or "the position",
        company_name=company_name or "your company",
        experience_level="Junior" if resume_data.get('no_of_pages', 1) <= 1 else "Senior",
        skills=", ".join(skills) if skills else "relevant skills",
        top_skills=top_skills,
        project_count=resume_data.get('no_of_pages', 1)+1,
        achievement="85% accuracy" if predicted_field == "Data Science" else "successful projects",
        job_requirement=job_description.split(".")[0] if job_description else "your data initiatives",
        web_tech="responsive design" if predicted_field == "Web Development" else "modern frameworks"
    )

# PDF Processing Functions
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Database Functions
connection = pymysql.connect(host='localhost', user='root', password='')
cursor = connection.cursor()

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

# UI Components
def highlight_sections(resume_text):
    sections = {
        'Objective': False, 'Skills': False, 'Experience': False,
        'Education': False, 'Projects': False, 'Achievements': False
    }
    
    for section in sections:
        if section.lower() in resume_text.lower():
            sections[section] = True
    
    st.subheader("Resume Section Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Present Sections**")
        for section, exists in sections.items():
            if exists:
                st.success(f"✓ {section}")
    
    with col2:
        st.markdown("**Missing Sections**")
        for section, exists in sections.items():
            if not exists:
                st.warning(f"✗ {section}")
    
    return sections

def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    no_of_reco = st.slider('Choose Number of Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for i, (c_name, c_link) in enumerate(course_list[:no_of_reco], 1):
        st.markdown(f"{i}. [{c_name}]({c_link})")

# Main App
def main():
    st.set_page_config(page_title="Smart Resume Analyzer", page_icon="📄")
    st.title("📄 Smart Resume Analyzer")
    
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose Mode:", activities)
    
    # Initialize database
    cursor.execute("CREATE DATABASE IF NOT EXISTS SRA;")
    connection.select_db("sra")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(100) NOT NULL,
            Email_ID VARCHAR(50) NOT NULL,
            resume_score VARCHAR(8) NOT NULL,
            Timestamp VARCHAR(50) NOT NULL,
            Page_no VARCHAR(5) NOT NULL,
            Predicted_Field VARCHAR(25) NOT NULL,
            User_level VARCHAR(30) NOT NULL,
            Actual_skills VARCHAR(300) NOT NULL,
            Recommended_skills VARCHAR(300) NOT NULL,
            Recommended_courses VARCHAR(600) NOT NULL
        )
    """)
    
    if choice == 'User':
        pdf_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
        
        if pdf_file:
            save_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            
            tab1, tab2 = st.tabs(["Resume Preview", "Analysis"])
            
            with tab1:
                show_pdf(save_path)
            
            with tab2:
                resume_data = ResumeParser(save_path).get_extracted_data()
                if resume_data:
                    resume_text = pdf_reader(save_path)
                    
                    # Display basic info
                    st.success(f"Hello {resume_data.get('name', 'User')}")
                    cols = st.columns(3)
                    cols[0].text(f"Name: {resume_data.get('name', '')}")
                    cols[1].text(f"Email: {resume_data.get('email', '')}")
                    cols[2].text(f"Pages: {resume_data.get('no_of_pages', 1)}")
                    
                    # Experience level
                    exp_level = "Fresher" if resume_data.get('no_of_pages', 1) == 1 else "Experienced"
                    st.info(f"Career Level: {exp_level}")
                    
                    # Domain prediction
                    domain = classify_resume(resume_text)
                    st.success(f"Predicted Domain: {domain}")
                    
                    # Skills analysis
                    st.subheader("Skills Analysis")
                    user_skills = st_tags(label="Your Skills:", 
                                         value=resume_data.get('skills', []))
                    
                    # Cover Letter Generator
                    st.subheader("Cover Letter Generator")
                    job_title = st.text_input("Job Title")
                    company = st.text_input("Company Name (optional)")
                    job_desc = st.text_area("Job Description (optional)")
                    
                    if st.button("Generate Cover Letter"):
                        letter = generate_cover_letter(
                            resume_data,
                            job_title=job_title,
                            company_name=company,
                            job_description=job_desc
                        )
                        st.text_area("Your Cover Letter", value=letter, height=300)
                        
                        # Download button
                        st.download_button(
                            "Download Cover Letter",
                            data=letter,
                            file_name=f"cover_letter_{resume_data.get('name', '')}.txt"
                        )
                    
                    # Resume scoring and other features...
                    # (Include the rest of your resume scoring logic here)
                    
                else:
                    st.error("Failed to process resume")
    
    else:  # Admin mode
        st.subheader("Admin Login")
        if st.text_input("Username") == "admin" and st.text_input("Password", type="password") == "admin123":
            st.success("Logged in as Admin")
            # Add admin dashboard components
        else:
            st.error("Invalid credentials")

if __name__ == '__main__':
    main()