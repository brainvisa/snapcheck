// Back-compat type shim for legacy `@lepton/api-client` type imports.
// Real types now come from the generated hey-api client. Runtime call sites
// use the generated SDK / TanStack hooks in src/api/*, not this file.
export type {
  SnapModel,
  BoardModel,
  Rating,
  RatingScale,
  RatingScaleItem,
  DirectoryModel,
  DirectoryItemModel,
  SettingsGroupModel,
  ObjectShortModel,
} from '../../../src/api/generated/types.gen';

import type { Rating, RatingScaleItem } from '../../../src/api/generated/types.gen';

// Legacy aliases kept so existing imports keep resolving.
export type RatingModel = Rating;
export type NoteScaleItem = RatingScaleItem;

// Only used by the (currently unmounted) NoteStatBar component.
export interface QualityControlModel {
  id: string;
  name?: string;
  notes?: Array<{ value?: number | null }>;
}
