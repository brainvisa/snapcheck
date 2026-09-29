import { client } from './generated/client.gen';

/**
 * Configure the generated hey-api client once, at app start.
 * The auth token is read lazily so it always reflects the current session,
 * even though the client is configured before the session token exists.
 */
let currentToken: string | null = null;

const API_URL_KEY = 'snapcheck.apiUrl';

/**
 * URL of the backend, by priority:
 *  - the "api" query parameter (ex: ?api=http://127.0.0.1:8050), given by the Qt client at startup.
 *    It is kept for the tab session so that it survives a reload without the parameter.
 *  - the VITE_API_URL environment variable (development server)
 *  - the default backend URL
 */
export function getApiUrl(): string {
    const fromQuery = new URLSearchParams(window.location.search).get('api');
    try {
        if (fromQuery) {
            sessionStorage.setItem(API_URL_KEY, fromQuery);
        }
        return (
            fromQuery || sessionStorage.getItem(API_URL_KEY) || import.meta.env.VITE_API_URL || 'http://localhost:8050'
        );
    } catch {
        // sessionStorage may be unavailable
        return fromQuery || import.meta.env.VITE_API_URL || 'http://localhost:8050';
    }
}

export function setApiToken(token: string | null): void {
    currentToken = token;
}

export function configureApi(): void {
    client.setConfig({
        baseURL: getApiUrl(),
        // Applied to every operation that declares the bearer security scheme.
        auth: () => currentToken ?? undefined,
    });
}
