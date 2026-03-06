# 🚜 KrishivanX: Digital Farming Partner & FinTech Advisory

### 🌐 Live Demo: [Click here to launch KrishivanX](https://krishivanx-ayh3ahe4csfjc8f3.centralindia-01.azurewebsites.net/)

**KrishivanX** is a comprehensive, AI-powered agricultural advisory platform designed to empower rural Indian farmers. It bridges the gap between crop disease diagnosis and government financial relief by providing instant, multilingual visual diagnostics and a voice-activated bureaucratic roadmap.

## 🚀 The Problem & Solution
Diagnosing a crop disease is only half the battle; navigating the bureaucracy to secure financial relief or subsidies is the true hurdle. 
KrishivanX solves this by acting as an end-to-end advisor: it scans the diseased crop, identifies the pathogen, provides immediate organic/chemical remedies, and instantly maps out the exact government scheme (including documents needed, office locations, and processing times) required for financial support.

## ✨ Key Features
* **📷 AI Visual Diagnostics:** Upload a photo of an infected leaf to receive a comprehensive 150-word diagnostic report using Vision AI. Includes both organic and chemical treatment plans.
* **🎙️ Multilingual Voice Advisory:** Speak naturally in over 25+ Indian regional languages and dialects. The AI transcribes, processes, and responds via text and text-to-speech (TTS) audio.
* **🏛️ FinTech & Bureaucratic Roadmap:** Generates step-by-step action plans for government schemes (e.g., PM Fasal Bima Yojana, PM-KISAN), detailing required documents, specific local offices to visit, and estimated costs.
* **🗄️ Secure Cloud History:** All farmer consultations, including compressed image data and voice query transcripts, are securely logged into an enterprise-grade NoSQL database for future reference.
* **🌗 Adaptive UI:** A fully responsive, app-like interface built with Streamlit that adapts to user devices.

## 🛠️ Tech Stack & Architecture
* **Frontend:** Streamlit, Custom CSS/HTML, Pillow (Image Compression)
* **Backend Brain:** Azure GitHub Models API (GPT-4o Vision & Text)
* **Audio Processing:** SpeechRecognition (Google Web Speech API), gTTS (Google Text-to-Speech)
* **Database:** Azure Cosmos DB for NoSQL (Serverless)
* **Hosting:** Microsoft Azure Web Apps

## ⚙️ Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ASbhay24/KrishivanX.git](https://github.com/ASbhay24/KrishivanX.git)
   cd KrishivanX
