import { createContext, useContext, useReducer, type ReactNode } from 'react';
import type { DefaultProps } from '../core/types';
import { useHttpClient } from '@lepton/core/contexts/ApiContext';
import { useEffect } from 'react';

interface AppDataModel {
  history?: string[];
}

type AppDataState = {
    loading: boolean;
    data: AppDataModel | null;
};

const defaultAppDataState: AppDataState = {
    loading: false,
    data: null
};

type AppDataAction =
    | { type: "IS_LOADING"; }
    | { type: 'SET_DATA'; data: AppDataModel }

function appDataReducer(state: AppDataState, action: AppDataAction): AppDataState {
    switch (action.type) {
        case 'IS_LOADING':
            return {...defaultAppDataState, loading: true};
        case 'SET_DATA':
            return { ...state, data: action.data, loading: false };
        default:
            return state;
    }
}

const AppDataContext = createContext<AppDataState | undefined>(undefined);
export const AppDataDispatchContext = createContext<React.Dispatch<AppDataAction> | null>(null);

function AppDataProviderInner(props: { children: ReactNode }) {
    const [state, dispatch] = useReducer(appDataReducer, defaultAppDataState);
    const httpClient = useHttpClient();

    useEffect(() => {
        dispatch({ type: 'IS_LOADING' });
        httpClient.get<AppDataModel>('/appdata')
            .then((data) => {
                dispatch({ type: 'SET_DATA', data });
            })
            .catch((error) => {
                console.error('Failed to load app data:', error);
                dispatch({ type: 'SET_DATA', data: null });
            });
    }, [httpClient]);
    
    return (
        <AppDataContext.Provider value={state}>
            <AppDataDispatchContext.Provider value={dispatch}>
                {props.children}
            </AppDataDispatchContext.Provider>
        </AppDataContext.Provider>
    );
}

export function AppDataProvider(props: DefaultProps) {
    return <AppDataProviderInner children={props.children} />;
}

export function useAppDataActions() {
    const dispatch = useContext(AppDataDispatchContext);
    const httpClient = useHttpClient();

    const loadAppData = () => {
        if (!dispatch) throw new Error('useAppDataActions must be used within a AppDataProvider');
        dispatch({ type: 'IS_LOADING' });
        httpClient.get<AppDataModel>('/appdata')
            .then((data) => {
                dispatch({ type: 'SET_DATA', data });
            })
            .catch((error) => {
                console.error('Failed to load app data:', error);
            });
    }

    return {
        loadAppData
    };
}

export function useAppData() {
    const state = useContext(AppDataContext);
    const actions = useAppDataActions();

    if (!state) {
        throw new Error('useAppData must be used within a AppDataProvider');
    }

    return {
        loading: state.loading,
        ...state.data,
        ...actions,
    };
}
