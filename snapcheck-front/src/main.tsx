import { startLeptonApp } from '@lepton/core/bootstrap';
import { AppUIStateProvider } from './contexts/AppUIStateContext';
import { configureApi, getApiUrl } from '../../src/api/configureApi';
import Snapcheck from './Snapcheck.tsx'
import './index.css'

// Configure API base URL
const apiConfig = {
  baseURL: getApiUrl()
};

// Configure the generated hey-api client (baseURL + lazy bearer token).
configureApi();

startLeptonApp(
  <Snapcheck />,
  AppUIStateProvider,
  apiConfig
);
