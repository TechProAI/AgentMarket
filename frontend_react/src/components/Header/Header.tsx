import React,{useState} from 'react'
import './Header.css'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useLocation } from 'react-router-dom'

const Header = () => {

    const [isUserClicked, setIsUserClicked] = useState<boolean>(false)

    const navigate = useNavigate()
    const { token, user, logout } = useAuth()
    const location = useLocation()
    
    const userLetter = user ? user[0] : ''

    const capitalizeFirstLetter = (text:string | undefined | null) => {
        if(text) {
            const str = text[0].toUpperCase() + text.slice(1, text.length)
            return str
        }
    }

    const handleLogout = () => {
        logout()
    }

    if(location.pathname.includes('login') || location.pathname.includes('signup')){
        return <></>
    }
    return (
        <div className='header-container'>
            <div className='header-left-section'>
                <div className='header-title'>
                    <p className='header-icon'>A</p>
                    <p className='header-name' onClick={() => navigate('/')}>AgentHub AI</p>
                </div>
                {/* <div className='header-components'>
                    <p><a href="#home-page">Home</a></p>
                    <p><a href="#agents-section">Agents</a></p>
                    <p><a href="#">Pricing</a></p>
                    <p><a href="#">Docs</a></p>
                </div> */}
            </div>
            <div className='header-right-section'>
                {
                    token ?
                        <>
                            <button className='header-get-started'>
                                <a href="#agents-section">Explore AI Agents</a>
                            </button>
                            <div className='username' onClick={() => setIsUserClicked(!isUserClicked)}>
                                {userLetter.toUpperCase()}
                                {isUserClicked ? 
                                <div className='header-logout'>
                                    <div>{capitalizeFirstLetter(user)}</div>
                                    <div onClick={handleLogout}>Logout</div>
                                </div> : <></>}
                            </div>
                        </>
                        :
                        <>
                            <button className='header-login-btn' onClick={() => navigate('/login')}>
                                Login
                            </button>
                            <button className='header-get-started'>
                                <a href="#agents-section">Explore AI Agents</a>
                            </button>
                        </>
                }

            </div>
        </div>
    )
}

export default Header