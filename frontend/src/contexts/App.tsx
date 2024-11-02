import React, { createContext, useContext, useState, ReactNode } from 'react';
import { LlmConnection, LlmModels } from '@/types/common';

interface AppContextProps {
    llmData: LlmConnection;
    setLlmData: React.Dispatch<React.SetStateAction<LlmConnection>>;
}

const AppContext = createContext<AppContextProps | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [llmData, setLlmData] = useState<LlmConnection>({
        apiKey: '',
        model: LlmModels.gpt4o,
    });

    return (
        <AppContext.Provider value={{ llmData, setLlmData }}>
            {children}
        </AppContext.Provider>
    );
};

export const useAppContext = (): AppContextProps => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within an AppProvider');
    }
    return context;
};