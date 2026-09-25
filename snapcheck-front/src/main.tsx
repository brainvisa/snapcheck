import { startLeptonApp } from '@lepton/core/bootstrap';
import { AppUIStateProvider } from './contexts/AppUIStateContext';
import { configureApi } from '../../src/api/configureApi';
import Snapcheck from './Snapcheck.tsx'
import './index.css'

// Configure API base URL
const apiConfig = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8050'
};

// Configure the generated hey-api client (baseURL + lazy bearer token).
configureApi();

startLeptonApp(
  <Snapcheck />,
  AppUIStateProvider,
  apiConfig
);
