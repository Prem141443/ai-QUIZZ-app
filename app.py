import streamlit as st
import PyPDF2
import docx
import random
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize, word_tokenize

# ---------- Helper functions ----------
def read_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        pdf_file = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_file.pages:
            text += page.extract_text()
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif uploaded_file.name.endswith(".txt"):
        text = str(uploaded_file.read(), "utf-8")
    else:
        st.warning("Unsupported file type")
    return text

def generate_quiz(text, num_questions=5, level="easy"):
    sentences = sent_tokenize(text)
    questions = []
    for i in range(min(num_questions, len(sentences))):
        sentence = sentences[i]
        words = word_tokenize(sentence)
        keywords = [w for w in words if w.isalpha() and len(w) > 4]
        if not keywords:
            continue
        answer = random.choice(keywords)
        question_text = sentence.replace(answer, "_____")
        distractors = random.sample([w for w in keywords if w != answer] + ["OptionX","OptionY"],3)
        options = [answer]+distractors
        random.shuffle(options)
        questions.append({'question':question_text,'options':options,'answer':answer})
    return questions

# ---------- Streamlit App ----------
st.title("📝 Offline Quiz Generator")

# Step 1: Upload file
uploaded_file = st.file_uploader("Upload your document (PDF, DOCX, TXT)", type=["pdf","docx","txt"])

if uploaded_file is not None:
    document_text = read_file(uploaded_file)
    
    # Step 2: Select difficulty
    level = st.selectbox("Select difficulty level", ["easy", "medium", "hard"])
    num_questions = st.slider("Number of questions", 1, 20, 5)
    
    if st.button("Generate Quiz"):
        st.session_state['questions'] = generate_quiz(document_text, num_questions, level)
        st.session_state['answers'] = []

    # Display quiz if generated
    if 'questions' in st.session_state:
        st.subheader("Quiz")
        for idx, q in enumerate(st.session_state['questions']):
            st.markdown(f"**Q{idx+1}: {q['question']}**")
            choice = st.radio(f"Select answer for Q{idx+1}", q['options'], key=f"q{idx}")
            if len(st.session_state['answers']) < len(st.session_state['questions']):
                st.session_state['answers'].append(choice)
            else:
                st.session_state['answers'][idx] = choice

        if st.button("Submit Quiz"):
            score = 0
            for idx, q in enumerate(st.session_state['questions']):
                if st.session_state['answers'][idx].lower() == q['answer'].lower():
                    score += 1
            total = len(st.session_state['questions'])
            percentage = (score/total)*100
            st.success(f"Your Score: {score}/{total} ({percentage:.2f}%)")
            if percentage >= 80:
                st.balloons()
                st.success("Feedback: Excellent! 🎉")
            elif percentage >= 50:
                st.info("Feedback: Good job! Keep improving. 👍")
            else:
                st.warning("Feedback: Try again! You can do better. 💪")
