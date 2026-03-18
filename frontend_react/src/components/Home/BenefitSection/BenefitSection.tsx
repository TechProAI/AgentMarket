import { Zap, Globe, Brain, MessageCircle } from 'lucide-react'
import './BenefitSection.css'

const benefitsArray = [
    {
      icon: Zap,
      title: "Fast AI responses",
      description: "Get instant answers powered by cutting-edge AI technology",
      gradient: {
        background: "linear-gradient(to bottom right, #2563EB, #9333EA)"
      }
    },
    {
      icon: Globe,
      title: "Real-time web data",
      description: "Access the latest information from across the internet",
      gradient: {
        background: "linear-gradient(to bottom right, #9333EA, #DB2777)"
      }
    },
    {
      icon: Brain,
      title: "Smart reasoning agents",
      description: "Advanced AI that understands context and nuance",
      gradient: {
        background: "linear-gradient(to bottom right, #DB2777, #EA580C)"
      }
    },
    {
      icon: MessageCircle,
      title: "Simple chat interface",
      description: "Natural conversation with AI in an intuitive interface",
      gradient: {
        background: "linear-gradient(to bottom right, #EA580C, #DC2626)"
      }
    }
]

const BenefitSection = () => {

    return (
        <>
        <div className="benefit-container" id="benefit-section">
            <div className="benefit-section">
                <div className='benefit-head'><h1>Why Choose AgentHub AI</h1></div>
                <div className='benefit-desc'>Powerful features that set us apart</div>
                <div className='benefit-main'>
                    {
                        benefitsArray.map((benefit, index) => {
                            return (
                                <div key={index} className='benefit-card'>
                                    <div style={benefit.gradient} className='icon-div'>
                                        <benefit.icon className='b-icon'/>
                                    </div>
                                    <div className='b-title'>
                                        {benefit.title}
                                    </div>
                                    <div className='b-desc'>
                                        {benefit.description}
                                    </div>
                                </div>
                            )
                        })
                    }
                </div>
            </div>
        </div>
        </>
    )
}

export default BenefitSection