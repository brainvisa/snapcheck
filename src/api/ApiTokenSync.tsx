import { useEffect } from 'react';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import { setApiToken } from './configureApi';

/** Keeps the generated API client's bearer token in sync with the session. */
export function ApiTokenSync() {
  const { sessionState } = useLObjectSession();
  useEffect(() => {
    setApiToken(sessionState ?? null);
  }, [sessionState]);
  return null;
}
