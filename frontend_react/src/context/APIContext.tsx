import React, { useState, useEffect, useContext } from 'react'
import { useLocation } from 'react-router-dom'

interface APIContextType {
    url: string | undefined
}

const APIContext = React.createContext<APIContextType | null>(null)


export const APIProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {

    const url = process.env.REACT_APP_DEV_API_URL

    return (
        <APIContext.Provider value={{ url }}>
            {children}
        </APIContext.Provider>
    )
}

export const useAPI = () => {
    const context = useContext(APIContext)
    if (!context) {
        throw new Error("useAPI must be used inside APIProvider");
    }
    return context;
}