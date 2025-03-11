chatgpt-clone/
│── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   ├── routes/
│   │   ├── user.py
│   │   ├── chat.py
│   ├── requirements.txt
│   ├── .env
│── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.js
│   │   │   ├── ChatWindow.js
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   ├── App.js
│   │   ├── index.js
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── .env
│── README.md



cd backend
pip install -r requirements.txt


 2️⃣ Create .env File
Inside the backend folder, create a .env file:

ini
Copy
Edit
DATABASE_URL=postgresql://username:password@localhost:5432/chatdb
SECRET_KEY=your_secret_key


database.py - PostgreSQL Connection
python
Copy
Edit
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


📌 4️⃣ models.py - Database Models
python
Copy
Edit
from sqlalchemy import Column, String, Text, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    messages = Column(Text)


auth.py - User Authentication
python
Copy
Edit
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import bcrypt
import jwt
import os
from models import User
from database import get_db

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "User registered"}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        token = jwt.encode({"username": user.username}, SECRET_KEY, algorithm="HS256")
        return {"token": token}
    raise HTTPException(status_code=400, detail="Invalid credentials")




chat.py - Chat API
python
Copy
Edit
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import openai
import os
from database import get_db
from models import Conversation

router = APIRouter()
openai.api_key = "your_openai_api_key"

@router.post("/chat")
def chat(conversation_id: str, message: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    messages = eval(conversation.messages) if conversation else []

    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    messages.append({"role": "assistant", "content": response.choices[0].message["content"]})

    if not conversation:
        conversation = Conversation(id=conversation_id, messages=str(messages))
        db.add(conversation)
    else:
        conversation.messages = str(messages)
    
    db.commit()
    return {"response": response.choices[0].message["content"]}
📌 7️⃣ main.py - Start FastAPI Server
python
Copy
Edit
from fastapi import FastAPI
from routes import auth, chat
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router, prefix="/auth")
app.include_router(chat.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
📌 8️⃣ Run the Backend
bash
Copy
Edit
uvicorn main:app --reload



🚀 Step 2: Frontend (React + TailwindCSS)
📌 1️⃣ Install Dependencies
bash
Copy
Edit
npx create-react-app frontend
cd frontend
npm install axios react-router-dom tailwindcss
npx tailwindcss init
📌 2️⃣ Configure tailwind.config.js
js
Copy
Edit
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
📌 3️⃣ Login.js - User Login
jsx
Copy
Edit
import { useState } from "react";
import axios from "axios";

const Login = ({ setToken }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    const response = await axios.post("http://localhost:8000/auth/login", { username, password });
    localStorage.setItem("token", response.data.token);
    setToken(response.data.token);
  };

  return (
    <div>
      <input placeholder="Username" onChange={(e) => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default Login;
📌 4️⃣ App.js - Routes
jsx
Copy
Edit
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import ChatWindow from "./components/ChatWindow";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ChatWindow />} />
      </Routes>
    </Router>
  );
}

export default App;
📌 5️⃣ Run Frontend
bash
Copy
Edit
npm start



📌 1️⃣ user.py - User API (Register & Login)
Create this inside backend/routes/user.py:

python
Copy
Edit
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import bcrypt
import jwt
import os
from database import get_db
from models import User

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY")

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "User registered"}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        token = jwt.encode({"username": user.username}, SECRET_KEY, algorithm="HS256")
        return {"token": token}
    raise HTTPException(status_code=400, detail="Invalid credentials")
📌 2️⃣ requirements.txt - Backend Dependencies
Create this inside backend/requirements.txt:

nginx
Copy
Edit
fastapi
uvicorn
sqlalchemy
psycopg2
python-dotenv
bcrypt
jwt
openai
📌 3️⃣ .env - Backend Config
Create this inside backend/.env:

ini
Copy
Edit
DATABASE_URL=postgresql://username:password@localhost:5432/chatdb
SECRET_KEY=your_secret_key
🔵 Frontend - React + TailwindCSS
📌 4️⃣ Register.js - User Registration
Create this inside frontend/src/components/Register.js:

jsx
Copy
Edit
import { useState } from "react";
import axios from "axios";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async () => {
    await axios.post("http://localhost:8000/auth/register", { username, password });
    alert("Registration successful!");
  };

  return (
    <div>
      <input placeholder="Username" onChange={(e) => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
      <button onClick={handleRegister}>Register</button>
    </div>
  );
};

export default Register;
📌 5️⃣ index.js - React Entry Point
Create this inside frontend/src/index.js:

jsx
Copy
Edit
import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import "./index.css";

ReactDOM.render(<App />, document.getElementById("root"));
📌 6️⃣ Sidebar.js - Sidebar for Chat History
Create this inside frontend/src/components/Sidebar.js:

jsx
Copy
Edit
import { useState, useEffect } from "react";
import axios from "axios";

const Sidebar = ({ selectChat }) => {
  const [chats, setChats] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/api/chat-history").then((res) => setChats(res.data));
  }, []);

  return (
    <div className="w-1/4 bg-gray-200 p-4">
      <h2>Chat History</h2>
      {chats.map((chat) => (
        <button key={chat.id} onClick={() => selectChat(chat.id)}>
          {chat.id}
        </button>
      ))}
    </div>
  );
};

export default Sidebar;
📌 7️⃣ ChatWindow.js - Chat Interface
Create this inside frontend/src/components/ChatWindow.js:

jsx
Copy
Edit
import { useState } from "react";
import axios from "axios";

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    const response = await axios.post("http://localhost:8000/api/chat", { message: input });
    setMessages([...messages, { role: "user", content: input }, { role: "assistant", content: response.data.response }]);
    setInput("");
  };

  return (
    <div className="w-3/4 p-4">
      {messages.map((msg, index) => (
        <div key={index} className={msg.role === "user" ? "text-blue-500" : "text-green-500"}>
          {msg.content}
        </div>
      ))}
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};

export default ChatWindow;
📌 8️⃣ package.json - Frontend Dependencies
Create this inside frontend/package.json:

json
Copy
Edit
{
  "name": "chatgpt-clone",
  "version": "1.0.0",
  "dependencies": {
    "axios": "^0.26.1",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-router-dom": "^6.2.1",
    "tailwindcss": "^3.0.0"
  }
}
📌 9️⃣ .env - Frontend Config
Create this inside frontend/.env:

ini
Copy
Edit
REACT_APP_BACKEND_URL=http://localhost:8000



 Changes & Updates
✅ 1️⃣ Backend: Add Logout API (backend/routes/user.py)
Modify user.py to include a logout endpoint by clearing the token on the frontend.

python
Copy
Edit
@router.post("/logout")
def logout():
    return {"message": "User logged out"}
✅ 2️⃣ Frontend: Add Logout Button (frontend/src/components/Sidebar.js)
Modify Sidebar.js to add a logout button.

jsx
Copy
Edit
const handleLogout = () => {
  localStorage.removeItem("token");
  window.location.reload();  // Reload to redirect to login
};

return (
  <div className="w-1/4 bg-gray-200 p-4">
    <h2>Chat History</h2>
    {chats.map((chat) => (
      <button key={chat.id} onClick={() => selectChat(chat.id)}>
        {chat.id}
      </button>
    ))}
    <button onClick={handleLogout} className="mt-4 bg-red-500 text-white p-2">Logout</button>
  </div>
);
✅ 3️⃣ Backend: New Chat API (backend/routes/chat.py)
Modify chat.py to allow users to start a new chat.

python
Copy
Edit
@router.post("/new-chat")
def new_chat(user: str, db: Session = Depends(get_db)):
    new_chat = Chat(user=user, messages=[])
    db.add(new_chat)
    db.commit()
    return {"chat_id": new_chat.id}
✅ 4️⃣ Frontend: Add "New Chat" Button (frontend/src/components/Sidebar.js)
Modify Sidebar.js to allow starting a new chat.

jsx
Copy
Edit
const startNewChat = async () => {
  const response = await axios.post("http://localhost:8000/api/new-chat", { user: "currentUser" });
  selectChat(response.data.chat_id);  // Load the new chat
};

return (
  <div className="w-1/4 bg-gray-200 p-4">
    <h2>Chat History</h2>
    {chats.map((chat) => (
      <button key={chat.id} onClick={() => selectChat(chat.id)}>
        {chat.id}
      </button>
    ))}
    <button onClick={startNewChat} className="mt-4 bg-blue-500 text-white p-2">New Chat</button>
    <button onClick={handleLogout} className="mt-4 bg-red-500 text-white p-2">Logout</button>
  </div>
);





import os
from PyPDF2 import PdfReader

# Directory containing PDF files
pdf_directory = '/path/to/your/pdf/folder'

# Output text file
output_file = 'combined_text.txt'

with open(output_file, 'w', encoding='utf-8') as txt_file:
    for filename in os.listdir(pdf_directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, filename)
            reader = PdfReader(pdf_path)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
            txt_file.write(f"## {filename}\n{text}\n")
            print(f"Processed {filename}")

print(f"All PDF files have been processed and combined into {output_file}")


with open("fullcode.text", "r", encoding="utf-8") as f:
     fullcode_as_string = f.read()


contents = [
    fullcode_as_string
]




import os
import fitz  # PyMuPDF
from PIL import Image

# Path to the PDF file
pdf_path = '/path/to/your/pdf_file.pdf'

# Output text file
output_file = 'output_text_with_images.txt'

# Directory to save extracted images
images_dir = 'extracted_images'
os.makedirs(images_dir, exist_ok=True)

# Open the PDF file
pdf_document = fitz.open(pdf_path)

# Function to extract images and save them
def save_image(image_index, image):
    image_bytes = image["image"]
    image_ext = image["ext"]
    image_filename = f"image_{image_index}.{image_ext}"
    image_filepath = os.path.join(images_dir, image_filename)
    with open(image_filepath, 'wb') as image_file:
        image_file.write(image_bytes)
    return image_filepath

# Process each page
with open(output_file, 'w', encoding='utf-8') as txt_file:
    image_counter = 1
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # Text block
                txt_file.write(block["text"] + "\n")
            elif block["type"] == 1:  # Image block
                image = pdf_document.extract_image(block["image"])
                image_path = save_image(image_counter, image)
                txt_file.write(f"[Image {image_counter}: {image_path}]\n")
                image_counter += 1

print(f"Processing complete. Text and image references saved in '{output_file}'. Extracted images are in the '{images_dir}' directory.")



cache = caching.CachedContent.create(
    model='models/gemini-1.5-flash-001',
    display_name='PDF-file', # used to identify the cache
    system_instruction=(
        'You are an expert text file analyzer, and your job is to answer '
        'the user\'s query based on the text file you have access to.'
    ),
    contents=contents,
    ttl=datetime.timedelta(minutes=15),
)

model = genai.GenerativeModel.from_cached_content(cached_content=cache)


Hey there! What can I do for you today?

Oh no, I'm sorry to hear that you're having service issues.  To help me assist you, could you please provide me with your fiber connection DTN number?


Okay, I've checked your account and it appears to be suspended due to an outstanding payment. Would you like to proceed with making a payment?


Great! We'll send a payment link to your registered email address. Once the payment is complete, your services will be resumed. Thanks for calling!  If you have any further questions, please don't hesitate to call back.






"You are the customer care IVR agent for [Company Name]. Your mission is to help customers feel welcome, understood, and supported from the moment they call. Your responses should be engaging, warm, and conversational—not plain or robotic. When greeting a caller, start with a friendly welcome, for example: 'Hello, thank you for calling [Company Name]! I'm here to help you today. How can I assist you?'

As the conversation progresses:

Show Empathy: Acknowledge the customer's concerns with phrases like, 'I understand how important this is for you,' or 'I’m sorry to hear that you’re experiencing an issue.'
Encourage Dialogue: Ask open-ended questions, such as 'Could you please tell me a bit more about what you're experiencing?' to ensure the customer feels heard.
Offer Clear Options: Provide concise, actionable choices to guide the conversation, like 'Press 1 for billing questions, 2 for technical support, or 3 to speak with an agent.'
Maintain an Engaging Tone: Use friendly language throughout and mix in light, conversational elements (when appropriate) to keep the call interesting without straying off-topic.
Your overall goal is to ensure that every response makes the customer feel valued and engaged while efficiently guiding them through their inquiry."

