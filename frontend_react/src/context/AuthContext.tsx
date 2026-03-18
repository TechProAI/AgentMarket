import React, { useState, useEffect, useContext } from 'react'

interface AuthContextType {
    token: string | null,
    login: (token: string, email: string) => void,
    logout: () => void,
    authLoading: boolean,
    user?: string | null
}

const AuthContext = React.createContext<AuthContextType | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {

    const [token, setToken] = useState<string | null>(null)
    const [user, setUser] = useState<string | null>(null)
    const [authLoading, setAuthLoading] = useState<boolean>(true)

    useEffect(() => {
        const storedToken = localStorage.getItem("token")
        if (storedToken) {
            setToken(storedToken)
        }
        setAuthLoading(false)
    }, [])

    const login = (newToken: string, userMail: string) => {
        localStorage.setItem("token", newToken)
        setToken(newToken)
        setUser(userMail)
    }

    const logout = () => {
        localStorage.removeItem("token")
        setToken(null)
    }

    return (
        <AuthContext.Provider value={{ token, login, logout, authLoading, user }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error("useAuth must be used inside AuthProvider");
    }
    return context;
}