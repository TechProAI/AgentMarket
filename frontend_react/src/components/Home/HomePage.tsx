import HeroSection from "./HeroSection/HeroSection"
import './HomePage.css'
import { useNavigate } from "react-router-dom"

const HomePage = () => {
    const navigate = useNavigate()

    return (
        <div className="home-page" id="home-page">
            <HeroSection />
        </div>
    )
}

export default HomePage