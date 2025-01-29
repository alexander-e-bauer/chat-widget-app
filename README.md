
# **React + Flask Chatbot Application**

This repository hosts a fully functional chatbot application that combines a **React frontend** with a **Flask backend**. The app leverages **OpenAI's GPT-based embeddings** for intelligent responses, document embeddings, and conversational memory. It supports real-time communication via **Socket.IO** and includes features like **dark mode**, **conversation history**, and **document-based query handling**.

---

## **Table of Contents**
- [Features](#features)
- [Demo](#demo)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
  - [Frontend (React)](#frontend-react)
  - [Backend (Flask)](#backend-flask)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Deployment](#deployment)
  - [Frontend Deployment](#frontend-deployment)
  - [Backend Deployment](#backend-deployment)
- [Contributing](#contributing)
- [License](#license)

---

## **Features**
- **Real-time Chat**: Interactive messaging powered by Socket.IO.
- **Document Embeddings**: Extract and embed text from Word, PDF, Markdown, and HTML files for intelligent query responses.
- **Dark Mode**: User-friendly theme toggle.
- **Conversation History**: Persistent storage of conversation IDs in `localStorage`.
- **Dynamic Backend**: Flask backend with support for OpenAI GPT embeddings and document-related queries.
- **Responsive Design**: Mobile-first UI with smooth transitions and animations.

---

## **Demo**
🎥 **Live Demo**: [Link to Deployed App](https://alexander-e-bauer.github.io)

---

## **Tech Stack**
### **Frontend**
- React.js
- TailwindCSS
- Socket.IO (for real-time communication)
- Lucide React Icons
- Markdown Renderer

### **Backend**
- Flask
- Flask-SocketIO
- OpenAI GPT (for embeddings and chat completions)
- PyPDF2, BeautifulSoup, and Python-docx (for document parsing)
- Pandas and Scipy (for data processing and embeddings)

### **Deployment**
- **Frontend**: GitHub Pages
- **Backend**: Heroku

---

## **Project Structure**
```
root
├── frontend/ (React App)
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   ├── ChatbotWidget.js
│   │   └── ...
│   └── public/
├── backend/ (Flask App)
│   ├── xyz/llm/
│   │   ├── embedding_model.py
│   │   ├── embedding_generator.py
│   │   └── ...
│   ├── app.py
│   ├── config.py
│   └── ...
├── README.md
└── requirements.txt
```

---

## **Setup and Installation**

### **Frontend (React)**
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
   The app will be available at `http://localhost:3000`.

### **Backend (Flask)**
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`.
   

## **Usage**
1. Start both the frontend and backend servers.
2. Open the React app in your browser.
3. Interact with the chatbot:
   - Send messages.
   - Upload documents for embeddings.
   - Toggle dark mode.
   - Start new conversations.

---

## **Deployment**

### **Frontend Deployment**
1. Build the React app:
   ```bash
   npm run build
   ```
2. Deploy the `build` folder to GitHub Pages or any hosting service.

### **Backend Deployment**
1. Push the backend code to a GitHub repository.
2. Deploy to Heroku:
   ```bash
   heroku create
   git push heroku main
   heroku config:set OPENAI_API_KEY=<your_openai_api_key>
   ```

---

## **Contributing**
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
