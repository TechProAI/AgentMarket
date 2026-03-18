import { Plane, Globe, File } from "lucide-react";
import './AgentsSection.css'
import HowItWorksSection from "../HowItWorksSection/HowItWorksSection";
import { useNavigate } from "react-router-dom";

const AgentsSection = () => {

    const navigate = useNavigate()

    return (
        <>
        <div className='agents-container' id='agents-section'>
            <div className='agents-section'>
                <h1 className='agents-section-head'>Explore AI Agents</h1>
                <div className='agents-section-desc'>Choose the perfect agent for your task</div>
                <div className='agents-section-agents'>
                    <div className='travel-agent'>
                        <div className="plane-icon"><Plane className="plane"/></div>
                        <h2>Travel Agent</h2>
                        <p className="travel-agent-desc">Plan trips, generate itineraries, and find travel information.</p>
                        <button className="travel-agent-btn" onClick={() => navigate('/travel-agent')}>Launch Agent</button>
                    </div>
                    <div className='web-search-agent'>
                        <div className="globe-icon"><Globe className="globe"/></div>
                        <h2>Web Search Agent</h2>
                        <p>Ask questions and get summarized answers from the web.</p>
                        <button className="web-search-agent-btn" onClick={() => navigate('/web-search-agent')}>Launch Agent</button>
                    </div>
                    <div className='resume-builder-agent'>
                        <div className="file-icon"><File className="file"/></div>
                        <h2>Resume Builder Agent</h2>
                        <p>Provide the details and get perfect Resume based on input.</p>
                        <button className="resume-builder-agent-btn" onClick={() => navigate('/resume-builder-agent')}>Launch Agent</button>
                    </div>
                </div>
            </div>
        </div>
        <HowItWorksSection />
        </>
    )
}

export default AgentsSection