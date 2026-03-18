import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router'
import { useAuth } from '../../context/AuthContext'
import { Zap } from 'lucide-react'
import './Signup.css'

const Signup = () => {
    const [mail, setMail] = useState<string>("")
    const [pass, setPass] = useState<string>("")
    const [user, setUser] = useState<string>("")
    const navigate = useNavigate()
    const {token} = useAuth()

    useEffect(() => {
        if(token){
            navigate('/')
        }
    },[token])

    const handleSignup = async (e: any) => {
        e.preventDefault()
        console.log(mail)
        console.log(pass)
        const res = await axios.post("http://127.0.0.1:8000/signup", {
            "email": mail,
            "password": pass,
            "user_name": user
        })
        if(res.statusText.toLowerCase() === 'ok'){
            navigate('/login')
        }
    };

    return (
        <div className='signup-container' id='signup-section'>
            <div className='signup-section'>
                <div className='signup-icon'>
                    <Zap className='zap-signup'/>
                </div>
                <div className='signup-head'><h1>Create an Account</h1></div>
                <div className='signup-desc'>Get started with your account</div>
                    <form onSubmit={handleSignup} className='signup-form'>
                        <div className='form-email'>
                            <label>Email</label>
                            <input type="email" placeholder='you@example.com' onChange={(e) => setMail(e.target.value)} />
                        </div>
                        <div className='form-password'>
                            <label>Password</label>
                            <input type="password" placeholder='........' onChange={(e) => setPass(e.target.value)} />
                            <div className='password-requirement'>Must be at least 8 characters long</div>
                        </div>
                        <div className='form-username'>
                            <label>Username</label>
                            <input type="text" placeholder='Jhon' onChange={(e) => setUser(e.target.value)} />
                        </div>
                        <button type="submit" className='signup-submit'>Create Account</button>
                    </form>
                <div className='signup-foot'>
                    <p>Already have an account?</p> <a href="/login">Login</a>
                </div>
            </div>
        </div>
    )
}

export default Signup