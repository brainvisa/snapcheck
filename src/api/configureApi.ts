import { client } from './generated/client.gen';

/**
 * Configure the generated hey-api client once, at app start.
 * The auth token is read lazily so it always reflects the current session,
 * even though the client is configured before the session token exists.
 */
let currentToken: string | null = null;

export function setApiToken(token: string | null): void {
  currentToken = token;
}

export function configureApi(): void {
  client.setConfig({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8050',
    // Applied to every operation that declares the bearer security scheme.
    auth: () => currentToken ?? undefined,
  });
}
