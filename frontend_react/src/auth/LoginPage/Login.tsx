import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router'
import { useAuth } from '../../context/AuthContext'
import './Login.css'
import { Zap } from 'lucide-react'
import { useAPI } from '../../context/APIContext'

const Login = () => {
    const [mail, setMail] = useState<string | null>(null)
    const [pass, setPass] = useState<string | null>(null)
    const navigate = useNavigate()
    const { token, login } = useAuth()
    const {url} = useAPI()
    console.log(url)

    useEffect(() => {
        if (token) {
            navigate('/')
        }
    }, [token])

    const handleLogin = async (e: any) => {
        e.preventDefault()
        const res = await axios.post(`${url}login`, {
            "email": mail,
            "password": pass
        });
        console.log(res)
        const token = res.data.access_token
        const userName = res.data.username
        login(token, userName);
        if (res.statusText.toLowerCase() === "ok" && res.data.access_token) {
            navigate('/')
        }
    };

    return (
        <div className='login-container' id='login-section'>
            <div className='login-section'>
                <div className='login-icon'>
                    <Zap className='zap-login'/>
                </div>
                <div className='login-head'><h1>Welcome Back</h1></div>
                <div className='login-desc'>Sign in to your account</div>
                    <form onSubmit={handleLogin} className='login-form'>
                        <div className='form-email'>
                            <label>Email</label>
                            <input type="email" placeholder='you@example.com' onChange={(e) => setMail(e.target.value)} />
                        </div>
                        <div className='form-password'>
                            <label>Password</label>
                            <input type="password" placeholder='........' onChange={(e) => setPass(e.target.value)} />
                        </div>
                        <button type="submit" className='login-submit'>Sign In</button>
                    </form>
                <div className='login-foot'>
                    <p>Don't have an account?</p> <a href="/signup">Sign Up</a>
                </div>
            </div>
        </div>
    )
}

export default Login