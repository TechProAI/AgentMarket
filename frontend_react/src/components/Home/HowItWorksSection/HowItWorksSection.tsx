import { MessageSquare, Cpu, Zap } from "lucide-react";
import './HowItWorksSection.css'
import ExamplePromptSection from "../ExamplePromptSection/ExamplePromptSection";

const HowItWorksSection = () => {

    return (
        <>
        <div className='works-container' id='works-section'>
            <div className='works-section'>
                <div className='works-title'>
                    <h1>How It Works</h1>
                </div>
                <div className='works-desc'>
                    Get answers in three simple steps
                </div>
                <div className='works-main'>
                    <div className='ask-question card'>
                        <div className="question-icon">
                            <div className="message-icon">
                                <MessageSquare className="icon message-square"/>
                            </div>
                            <div className="icon-1 number"><span>1</span></div>
                        </div>
                        <div className="question-title">Ask your question</div>
                        <div className="question-detail">Type your question or request in natural language</div>
                    </div>
                    <div className='agent-process card'>
                        <div className="question-icon">
                            <div className="cpu-icon">
                                <Cpu className="icon cpu"/>
                            </div>
                            <div className="icon-2 number"><span>2</span></div>
                        </div>
                        <div className="question-title">AI agent processes</div>
                        <div className="question-detail">Our specialized agent analyzes and understands your request</div>
                    </div>
                    <div className='get-results card'>
                        <div className="question-icon">
                            <div className="zap-icon">
                                <Zap className="icon zap"/>
                            </div>
                            <div className="icon-3 number"><span>3</span></div>
                        </div>
                        <div className="question-title">Get instant results</div>
                        <div className="question-detail">Receive comprehensive, accurate answers immediately</div>
                    </div>
                </div>
            </div>
        </div>
        <ExamplePromptSection />
        </>
    )
}

export default HowItWorksSection
