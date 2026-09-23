// Snapcheck-specific types
// Replaces @lepton/api-client imports

import type { ObjectShortModel } from '@lepton/core/api/types';

export interface SnapModel extends ObjectShortModel {
  id: string;
  name?: string;
  path?: string;
  content?: any;
  metadata?: Record<string, any>;
  has_changed?: boolean;
  version?: number;
}

export interface BoardModel {
  id: string;
  name?: string;
  boards?: any[];
}

export interface RatingModel {
  id?: string;
  value?: number;
  scale?: number;
}

export interface RatingScaleItem {
  id: string | number;
  label: string;
  value: number;
}

export interface NoteScaleItem {
  id: string | number;
  label: string;
  value: number;
}

export interface QualityControlModel {
  id: string;
  name?: string;
  ratings?: RatingModel[];
}

export interface DirectoryItemModel {
  path: string;
  filename: string;
  isdir: boolean;
}

export interface DirectoryModel {
  path: string;
  content: DirectoryItemModel[];
  parent?: string | null;
}

export interface OpenAPIConfig {
  BASE: string;
  VERSION: string;
  WITH_CREDENTIALS: boolean;
  CREDENTIALS: string;
  TOKEN?: string;
  HEADERS?: Record<string, string>;
}

// OpenAPI config object (replaces @lepton/api-client OpenAPI)
export const OpenAPI: OpenAPIConfig = {
  BASE: 'http://localhost:8000',
  VERSION: '1.0.0',
  WITH_CREDENTIALS: false,
  CREDENTIALS: 'include',
  TOKEN: undefined,
  HEADERS: undefined,
};

// Service adapters
export const SettingsService = {
  getAllSettings: async () => {
    // This will be implemented via useSettingsContext
    return {};
  }
};

export const FilesService = {
  listDirectory: async (path?: string, extensions?: string[]): Promise<DirectoryModel> => {
    // Will be replaced with useFileServices
    return { path: '', content: [], parent: null };
  }
};

export const ContentService = {
  getStaticContent: async (path: string) => {
    // Will be replaced with useContentServices
    return { content: '' };
  }
};

export const ObjectsService = {
  open: async (path: string) => ({} as SnapModel),
  close: async (path: string) => {},
  save: async (snapId: string) => ({} as SnapModel),
  saveAs: async (objectId: string, newPath: string) => ({} as SnapModel),
  exportAsHtml: async (snapId: string, path: string) => ({ success: true }),
  exportAsPdf: async (snapId: string, path: string) => ({ success: true }),
  updateField: async (snapId: string, data: any) => ({ version: 0, has_changed: false }),
};
