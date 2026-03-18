import AgentsSection from '../AgentsSection/AgentsSection'
import './HeroSection.css'
import { Sparkles,ArrowRight } from 'lucide-react'

const HeroSection = () => {

    return (<>
        <div className="hero-container" id="hero-section">
            <div className='hero-section'>
                <div className='hero-section-left'>
                    <div className='left-spark'>
                        <Sparkles className='sparkle'/> <span>Powered by Advanced AI</span>
                    </div>
                    <div className='left-h1'>
                        <h1>AI Agents That Work For You</h1>
                    </div>
                    <div className='left-purpose'>Use specialized AI agents to search the web, plan trips, and automate tasks.</div>
                    <div className='left-btns'>
                        <button className='left-btn-travel'>Try Travel Agent <ArrowRight className='arrow-right'/></button>
                        <button className='left-btn-web'>Try Web Search Agent</button>
                    </div>
                </div>
                <div className='hero-section-right'>
                    <div className='right-colors'>
                        <span className='color red'></span>
                        <span className='color orange'></span>
                        <span className='color green'></span>
                    </div>
                    <div className='right-question'>
                        <div className='user-icon'></div>
                        <div className='user-question'>Plan a 5 day trip to Japan</div>
                    </div>
                    <div className='right-answer'>
                        <div className='ai-icon'><Sparkles className='sparkle-right'/></div>
                        <div className='ai-answer'>
                            <p className='ai-answer-head'>Here's a curated 5-day Japan itinerary:</p>

                            <div className='ai-answer-list'>
                                <p><strong>Day 1-2:</strong> Tokyo - Visit Shibuya, Senso-ji Temple</p>
                                <p><strong>Day 3:</strong> Mount Fuji day trip</p>
                                <p><strong>Day 4-5:</strong> Kyoto - Bamboo Forest, Fushimi Inari</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <AgentsSection />
        </>
    )
}

export default HeroSection