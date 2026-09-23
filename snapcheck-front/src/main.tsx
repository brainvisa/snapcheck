import { startLeptonApp } from '@lepton/core/bootstrap';
import { ModalProvider } from '@lepton/core/contexts/ModalContext';
import { AppUIStateProvider } from './contexts/AppUIStateContext';
import Snapcheck from './Snapcheck.tsx'
import './index.css'

// Configure API base URL
const apiConfig = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
};

startLeptonApp(
  <ModalProvider><Snapcheck /></ModalProvider>,
  AppUIStateProvider,
  apiConfig
);
