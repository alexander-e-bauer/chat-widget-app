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
- [Embedding Generator](#embedding-generator)
  - [How It Works](#how-it-works)
  - [Folder Structure](#folder-structure)
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
│   │   │   ├── ChatbotWidget.js
│   │   │   ├── MarkdownRenderer.js
│   │   ├── App.js
│   │   └── ...
│   └── public/
├── backend/ (Flask App)
│   ├── llm/
│   │   ├── embeddings/
│   │   │   ├── example_embeddings.csv
│   │   │   ├── system_input.txt
│   │   ├── knowledge_sources/
│   │   │   ├── example_source.md
│   │   │   ├── [Put source douments here]
│   │   ├── embedding_model.py
│   │   ├── embedding_generator.py
│   │   └── ...
│   ├── app.py
│   ├── config.py
│   └── ...
├── README.md
└── requirements.txt
```

**Make sure to edit the system_input.txt and replace the example source with your own documents*

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

---

## **Usage**
1. Start both the frontend and backend servers.
2. Open the React app in your browser.
3. Interact with the chatbot:
   - Send messages.
   - Upload documents for embeddings.
   - Toggle dark mode.
   - Start new conversations.

---

## **Embedding Generator**

### **How It Works**

The `embedding_generator.py` script is used to process your knowledge base and create embeddings for documents. These embeddings are then utilized by the chatbot for intelligent, context-aware responses.

#### **Steps to Use the Embedding Generator**
1. **Prepare Your Knowledge Base**:
   - Place all your documents (`.docx`, `.pdf`, `.md`, `.html`) in the folder:  
     `xyz/llm/knowledge_sources/personal`.

2. **Generate Embeddings**:
   - Run the `embedding_generator.py` script to process the documents and generate embeddings:
     ```bash
     python embedding_generator.py
     ```
   - This script will:
     - Extract text from the documents in the specified folder.
     - Generate embeddings for the extracted text using OpenAI's API.
     - Save the embeddings to a CSV file located at:  
       `xyz/llm/embeddings/resume_test.csv`.

3. **Verify the Output**:
   - Ensure that the `resume_test.csv` file is created in the `xyz/llm/embeddings/` folder.  
   - The chatbot will use this file to retrieve embeddings for intelligent responses.

4. **Automatic Integration with Chatbot**:
   - The chatbot automatically reads the embeddings from the file using:
     ```python
     df = read_embedding('xyz/llm/embeddings/resume_test.csv')
     ```
   - Ensure the folder structure matches the paths specified in the scripts. If the structure is not set up correctly, the chatbot will not be able to load the embeddings.

### **Folder Structure**

To ensure the system works correctly, the folder structure must follow this layout:

```
xyz/
├── llm/
│   ├── embeddings/
│   │   ├── resume_test.csv
│   │   ├── system_input.txt
│   ├── knowledge_sources/
│   │   ├── personal/
│   │       ├── <your-documents-here>
│   ├── tools/
│   │   ├── telegram_update.py
│   ├── embedding_model.py
│   ├── embedding_generator.py
├── app.py
```

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
