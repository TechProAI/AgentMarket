import React, { useState, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { useNavigate } from "react-router";
import './TravelAgent.css'
import { useAuth } from "../../context/AuthContext";

interface Message {
    role: "user" | "assistant";
    content: string;
}

const TravelAgentPage = () => {
    const [input, setInput] = useState<string>("");
    const [aiLoading, setAiLoading] = useState<Boolean>(false);
    const [messages, setMessages] = useState<Message[]>(() => {
        const saved = localStorage.getItem("travel_chat");
        return saved ? JSON.parse(saved) : [];
    });
    const navigate = useNavigate()
    const { token } = useAuth()

    useEffect(() => {
        localStorage.setItem("travel_chat", JSON.stringify(messages));
    }, [messages]);

    const sendQuery = async () => {
        if (!input) return;
        setAiLoading(true)

        const userMessage: Message = { role: "user", content: input };

        setMessages((prev) => [...prev, userMessage]);

        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_URL}/api/travel-agent`,
                { text: input },
                {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            const aiMessage: Message = {
                role: "assistant",
                content: response.data.message
            };

            setMessages((prev) => [...prev, aiMessage]);
            setInput("");
        } catch (error) {
            console.error(error);
        } finally {
            setAiLoading(false)
        }
    };

    const clearChat = () => {
        localStorage.removeItem("travel_chat");
        setMessages([]);
    };

    return (
        <div className='travel-agent-container'>
            <div className="travel-agent-section">
            <div className="btns">
                <button className='btn' onClick={() => navigate(-1)}>Back to Home Page</button>
                <button className='btn' onClick={clearChat}>Clear Chat</button>
            </div>

            {/* Chat Area */}
            <div className='response-section'>
                {messages.map((msg, index) => (
                    <div className={`response-main ${msg.role === "user" ? "end-chat" : "start-chat"} `}
                        key={index}
                    >
                        <div className={`message-content ${msg.role === "user" ? "user-msg" : "ai-msg"}`}
                        >
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                    </div>
                ))}
                {aiLoading && (
                    <div className="response-main start-chat">
                        <div className="message-content ai-msg thinking">
                            AI is thinking...
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="input-section">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask your travel assistant..."
                />

                <button className="send-btn" onClick={sendQuery}>Send</button>
            </div>
            </div>
        </div>
    );
};

export default TravelAgentPage;