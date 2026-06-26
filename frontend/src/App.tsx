import React, { useState, useRef, useEffect } from 'react';
import './App.css';

// TypeScript workaround for browser-native Speech APIs
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

// Define the shape of our chat messages
interface Message {
  role: 'user' | 'assistant' | 'system';
  text: string;
}

function App() {
  const [sessionId] = useState<string>(() => Math.random().toString(36).substring(2, 10));
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [pendingApproval, setPendingApproval] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Voice: Text to Speech
  const speakResponse = (text: string) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel(); // Stop current speech
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  // Voice: Speech to Text
  const toggleListening = () => {
    if (!recognition) return alert("Voice recognition not supported in this browser.");
    
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };
      recognition.onerror = () => setIsListening(false);
    }
  };

  // API Call: Send Message to FastAPI
  const sendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, user_input: userMessage })
      });
      
      const data = await response.json();

      if (data.status === "pending_approval") {
        setPendingApproval(true);
        setMessages(prev => [...prev, { role: 'system', text: 'Action paused. Waiting for manager approval.' }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);
        speakResponse(data.response); // Agent speaks back!
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'system', text: 'Error connecting to backend.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  // API Call: Manager Approval
  const handleAdminAction = async (approved: boolean) => {
    setPendingApproval(false);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/admin/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, approved })
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);
      speakResponse(data.response);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', fontFamily: 'Arial' }}>
      <h2>🏥 AI Healthcare Assistant</h2>
      <p style={{ color: 'gray' }}>Session ID: {sessionId}</p>

      {/* Chat History Box */}
      <div style={{ height: '400px', border: '1px solid #ccc', padding: '20px', overflowY: 'auto', marginBottom: '20px', borderRadius: '8px' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ textAlign: msg.role === 'user' ? 'right' : 'left', margin: '10px 0' }}>
            <span style={{ 
              background: msg.role === 'user' ? '#007BFF' : msg.role === 'system' ? '#FFC107' : '#E9ECEF', 
              color: msg.role === 'user' ? 'white' : 'black', 
              padding: '10px', 
              borderRadius: '8px',
              display: 'inline-block',
              maxWidth: '80%'
            }}>
              {msg.text}
            </span>
          </div>
        ))}
        {isLoading && <div style={{ color: 'gray' }}>Typing...</div>}
        <div ref={chatEndRef} />
      </div>

      {/* Input Form & Voice Button */}
      <form onSubmit={sendMessage} style={{ display: 'flex', gap: '10px' }}>
        <button type="button" onClick={toggleListening} style={{ background: isListening ? 'red' : 'green', color: 'white', border: 'none', padding: '10px', borderRadius: '5px', cursor: 'pointer' }}>
          {isListening ? '🛑 Listening...' : '🎤 Speak'}
        </button>
        <input 
          value={input} 
          onChange={e => setInput(e.target.value)} 
          placeholder="Type or speak a message..." 
          style={{ flex: 1, padding: '10px' }}
          disabled={pendingApproval}
        />
        <button type="submit" disabled={pendingApproval || isLoading}>Send</button>
      </form>

      {/* Admin HITL Modal */}
      {pendingApproval && (
        <div style={{ background: '#FFF3CD', padding: '20px', border: '1px solid #FFEEBA', marginTop: '20px', borderRadius: '8px' }}>
          <h3 style={{ color: '#856404' }}>🛑 Manager Override Required</h3>
          <p>The AI is attempting a high-risk action (booking). Do you approve?</p>
          <button onClick={() => handleAdminAction(true)} style={{ background: 'green', color: 'white', padding: '10px', marginRight: '10px', cursor: 'pointer' }}>✅ Approve</button>
          <button onClick={() => handleAdminAction(false)} style={{ background: 'red', color: 'white', padding: '10px', cursor: 'pointer' }}>❌ Reject</button>
        </div>
      )}
    </div>
  );
}

export default App;