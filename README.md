# 🌐 LingoAI Translator

**LingoAI Translator** is a simple, user-friendly, and interactive language translation application developed using Python and Streamlit.

It allows users to translate text between multiple languages, listen to translated content, download translations, and maintain a history of previous translations.

## ✨ Features

- 🌍 Supports 25 different languages.
- 🔄 Translate text from one language to another.
- ↔️ Swap source and target languages.
- 🔊 Listen to translated text using text-to-speech.
- 📋 Copy translated text.
- 📥 Download translations as a `.txt` file.
- 🕘 Save and view translation history.
- 🗑️ Clear input text easily.
- ⚠️ Input validation and error handling.
- 🎨 Modern dark-themed user interface.
- ⏳ Loading indicators for translation and audio generation.

## 🛠️ Technologies Used

- **Python** – Main programming language.
- **Streamlit** – Web application interface.
- **MyMemory Translation API** – Text translation.
- **gTTS** – Text-to-speech functionality.
- **SQLite** – Translation history database.
- **Requests** – API communication.

## 📂 Project Structure

```text
Language_Translation_Tool/
│
├── app.py
├── requirements.txt
├── README.md
├── translations.db
└── venv/
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Rameezali-ai/CodeAlpha-Language-Translation-Tool.git
```

### 2. Navigate to the Project Folder

```bash
cd CodeAlpha-Language-Translation-Tool
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python -m streamlit run app.py
```

The application will open in your web browser.

## 📌 Requirements

- Python 3.10 or higher
- Internet connection for translation and text-to-speech services.

## 👨‍💻 Developer

**Rameez Ali**

GitHub: https://github.com/Rameezali-ai

## 🎓 Internship Project

Developed as part of the **CodeAlpha Artificial Intelligence Internship**.

---

⭐ If you like this project, don't forget to give it a star!
