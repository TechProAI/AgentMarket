import BenefitSection from '../BenefitSection/BenefitSection'
import './ExamplePromptSection.css'
import { Sparkles } from 'lucide-react'


const promptArray:string[] = [
    "Plan a 5 day trip to Japan",
    "Find best places to visit in Paris",
    "Latest AI trends in 2026",
    "What's the weather like in Bali?",
    "Create a weekend itinerary for Rome",
    "Best restaurants in Tokyo"
]

const ExamplePromptSection = () => {

    return (
        <>
        <div className="prompt-container" id="prompt-section">
             <div className="prompt-section">
                <div className='prompt-head'><h1>Try These Examples</h1></div>
                <div className='prompt-desc'>Get started with these popular prompts</div>
                <div className='prompt-main'>
                    {
                        promptArray.map((prompt:string,index:number) => {
                            return (
                                <div className='prompt' key={index}>
                                    <Sparkles className='sparkles'/>
                                    <div className='prompt-line'>{prompt}</div>
                                </div>
                            )
                        })
                    }
                </div>
             </div>
        </div>
        <BenefitSection />
        </>
    )
}

export default ExamplePromptSection