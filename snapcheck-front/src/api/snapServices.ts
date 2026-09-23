import { useHttpClient } from '@lepton/core/contexts/ApiContext';
import type { ObjectShortModel } from '@lepton/core/api/types';

export interface SnapModel extends ObjectShortModel {
  content?: any;
  metadata?: Record<string, any>;
}

export interface FileResponse {
  success: boolean;
  message?: string;
}

export interface UpdateFieldResponse {
  version?: number;
  has_changed?: boolean;
}

export function useSnapServices() {
  const httpClient = useHttpClient();

  return {
    // Snap operations
    openSnap: (path: string) => httpClient.post<SnapModel>('/snap/open', { path }),
    closeSnap: (snapId: string) => httpClient.post<void>('/snap/close', { snap_id: snapId }),
    saveSnap: (snapId: string) => httpClient.post<SnapModel>('/snap/save', { snap_id: snapId }),
    saveSnapAs: (snapId: string, newPath: string) => httpClient.post<SnapModel>('/snap/save-as', { snap_id: snapId, new_path: newPath }),
    updateSnapField: (snapId: string, field: string, value: any) => 
      httpClient.put<UpdateFieldResponse>(`/snap/${snapId}/field`, { field_path: field, value }),
    
    // Export operations
    exportAsHtml: (snapId: string, path: string) => httpClient.post<FileResponse>(`/snap/${snapId}/html/${path}`, {}),
    downloadAsHtml: (snapId: string) => httpClient.get<Blob>(`/snap/${snapId}/html/download`),
    exportAsPdf: (snapId: string, path: string) => httpClient.post<FileResponse>(`/snap/${snapId}/pdf/${path}`, {}),
    downloadAsPdf: (snapId: string) => httpClient.get<Blob>(`/snap/${snapId}/pdf/download`),
    
    // Image/content operations
    getSnapImage: (snapId: string, src: string) => `http://localhost:8000/snap/${snapId}/image/${src}`,
  };
}

export function useFileServices() {
  const httpClient = useHttpClient();

  return {
    listDirectory: (path?: string, extensions?: string[]) => {
      const url = path ? `/files/${path}` : '/files/';
      const params = extensions ? { extensions: extensions.join(',') } : {};
      return httpClient.get(url, { params });
    },
    getFile: (path: string) => httpClient.get(`/files/${path}`),
  };
}

export function useContentServices() {
  const httpClient = useHttpClient();

  return {
    getStaticContent: (path: string) => 
      httpClient.get<{ content: string }>(`/content/${path}`),
  };
}
