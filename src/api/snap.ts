import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    getAllSettingsOptions,
    getAllSettingsQueryKey,
    getStaticContentOptions,
    listDirectoryOptions,
    listRootDirectoryOptions,
    openOptions,
    openQueryKey,
} from './generated/@tanstack/react-query.gen';
import { close, patchField, resetRating, save, saveAs, setSetting } from './generated/sdk.gen';
import type { LightweightResponse, SettingsGroupModel, SnapModel } from './generated/types.gen';
import { setByPath } from './setByPath';

/** Query key for a snap document, keyed by its file path (single source of truth). */
export const snapKey = (path: string) => openQueryKey({ path: { path } });

/** Query options for a snap, for use with useQuery/useQueries (keyed by path). */
export const snapQueryOptions = (path: string) => ({
    ...openOptions({ path: { path } }),
    staleTime: Infinity,
});

/** Read a snap document from the TanStack cache (fetches on first use). */
export function useSnap(path: string | null) {
    return useQuery({
        ...openOptions({ path: { path: path ?? '' } }),
        enabled: !!path,
        staleTime: Infinity,
    });
}

type PatchVars = { fieldPath: string; value: unknown };

/**
 * Patch a single field of a snap.
 *  - optimistic: applies the value to the cached document immediately (setByPath),
 *  - serialized per snap via `scope` so concurrent edits never drop a write,
 *  - sends expected_version and rolls back / refetches on conflict.
 */
export function usePatchField(path: string | null, snapId: string | undefined) {
    const qc = useQueryClient();
    const key = path ? snapKey(path) : null;

    return useMutation({
        scope: { id: snapId ? `lobject:${snapId}` : 'lobject' },
        mutationFn: async (vars: PatchVars): Promise<LightweightResponse> => {
            if (!snapId) throw new Error('No snap id');
            const prev = key ? qc.getQueryData<SnapModel>(key) : undefined;
            const { data } = await patchField({
                path: { snap_id: snapId },
                body: { field_path: vars.fieldPath, value: vars.value, expected_version: prev?.version ?? null },
                throwOnError: true,
            });
            return data!;
        },
        onMutate: async (vars) => {
            if (!key) return {};
            await qc.cancelQueries({ queryKey: key });
            const prev = qc.getQueryData<SnapModel>(key);
            if (prev) {
                let next = setByPath({ ...prev, has_changed: true }, vars.fieldPath, vars.value);
                // Same rule as the backend: editing a rating value or comment makes it not default anymore
                const m = vars.fieldPath.match(/^(ratings\.[^.]+)\.(value|comment)$/);
                if (m) next = setByPath(next, `${m[1]}.is_default`, false);
                qc.setQueryData<SnapModel>(key, next);
            }
            return { prev };
        },
        onError: (_err, _vars, ctx: any) => {
            if (key && ctx?.prev) qc.setQueryData(key, ctx.prev);
            if (key) qc.invalidateQueries({ queryKey: key });
        },
        onSuccess: (resp) => {
            if (!key) return;
            const cur = qc.getQueryData<SnapModel>(key);
            if (cur) qc.setQueryData<SnapModel>(key, { ...cur, version: resp.version, has_changed: resp.has_changed });
        },
    });
}

/**
 * Reset a rating of a snap to its default state (default value, no comment).
 * Shares the patch scope so it is serialized with the field updates of the same snap.
 */
export function useResetRating(path: string | null, snapId: string | undefined) {
    const qc = useQueryClient();
    const key = path ? snapKey(path) : null;

    return useMutation({
        scope: { id: snapId ? `lobject:${snapId}` : 'lobject' },
        mutationFn: async (ratingId: string): Promise<LightweightResponse> => {
            if (!snapId) throw new Error('No snap id');
            const { data } = await resetRating({
                path: { snap_id: snapId, rating_id: ratingId },
                throwOnError: true,
            });
            return data!;
        },
        onMutate: async (ratingId) => {
            if (!key) return {};
            await qc.cancelQueries({ queryKey: key });
            const prev = qc.getQueryData<SnapModel>(key);
            const rating = prev?.ratings?.find((r) => r.id === ratingId);
            if (prev && rating && !rating.is_default) {
                const next = setByPath({ ...prev, has_changed: true }, `ratings.{id:${ratingId}}`, {
                    ...rating,
                    value: rating.default ?? null,
                    comment: null,
                    is_default: true,
                });
                qc.setQueryData<SnapModel>(key, next);
            }
            return { prev };
        },
        onError: (_err, _ratingId, ctx: any) => {
            if (key && ctx?.prev) qc.setQueryData(key, ctx.prev);
            if (key) qc.invalidateQueries({ queryKey: key });
        },
        onSuccess: (resp) => {
            if (!key) return;
            const cur = qc.getQueryData<SnapModel>(key);
            if (cur) qc.setQueryData<SnapModel>(key, { ...cur, version: resp.version, has_changed: resp.has_changed });
        },
    });
}

export function useSaveSnap() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (vars: { snapId: string; path: string }) => {
            const { data } = await save({ query: { object_id: vars.snapId }, throwOnError: true });
            return { snap: data!, path: vars.path };
        },
        onSuccess: ({ snap, path }) => {
            if (snap) qc.setQueryData(snapKey(path), snap);
        },
    });
}

export function useSaveSnapAs() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (vars: { snapId: string; newPath: string }) => {
            const { data } = await saveAs({
                query: { object_id: vars.snapId, new_path: vars.newPath },
                throwOnError: true,
            });
            return data!;
        },
        onSuccess: () => qc.invalidateQueries(),
    });
}

export function useCloseSnap() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (vars: { snapId: string; path: string }) => {
            await close({ query: { object_id: vars.snapId }, throwOnError: true });
            return vars;
        },
        onSuccess: (vars) => qc.removeQueries({ queryKey: snapKey(vars.path) }),
    });
}

/* ------------------------------------------------------------------ */
/* Other server reads, now cached by TanStack                          */
/* ------------------------------------------------------------------ */

export function useSettingsQuery() {
    return useQuery({ ...getAllSettingsOptions(), staleTime: Infinity });
}

/** Value of a setting (`<group>.<setting>`), read from the cached settings. */
export function useSetting(path: string) {
    const { data } = useSettingsQuery();
    const [groupId, settingId] = path.split('.');
    return data?.find((g) => g.id === groupId)?.settings.find((s) => s.id === settingId)?.value;
}

type SettingValue = string | boolean | number | null;

/** Replace the value of a setting in a list of settings groups (immutable). */
function withSettingValue(groups: SettingsGroupModel[], path: string, value: SettingValue): SettingsGroupModel[] {
    const [groupId, settingId] = path.split('.');
    return groups.map((g) =>
        g.id !== groupId
            ? g
            : { ...g, settings: g.settings.map((s) => (s.id === settingId ? { ...s, value: value ?? s.default } : s)) },
    );
}

/** Set a setting on the server (saved in the user config), applied optimistically to the cached settings. */
export function useSetSetting() {
    const qc = useQueryClient();
    const key = getAllSettingsQueryKey();

    return useMutation({
        mutationFn: async (vars: { path: string; value: SettingValue }) => {
            const { data } = await setSetting({
                path: { path: vars.path },
                body: { value: vars.value },
                throwOnError: true,
            });
            return data!;
        },
        onMutate: async (vars) => {
            await qc.cancelQueries({ queryKey: key });
            const prev = qc.getQueryData<SettingsGroupModel[]>(key);
            if (prev) qc.setQueryData(key, withSettingValue(prev, vars.path, vars.value));
            return { prev };
        },
        onError: (_err, _vars, ctx: any) => {
            if (ctx?.prev) qc.setQueryData(key, ctx.prev);
            qc.invalidateQueries({ queryKey: key });
        },
        onSuccess: (setting, vars) => {
            const cur = qc.getQueryData<SettingsGroupModel[]>(key);
            if (cur) qc.setQueryData(key, withSettingValue(cur, vars.path, setting.value ?? null));
        },
    });
}

export function useDirectory(path: string | null, extensions?: string[]) {
    const options = path
        ? listDirectoryOptions({ path: { path }, body: extensions ?? null })
        : listRootDirectoryOptions({ body: extensions ?? null });
    return useQuery({ ...(options as any), placeholderData: keepPreviousData });
}

export function useServerContent(path: string) {
    return useQuery({ ...getStaticContentOptions({ path: { path } }), staleTime: Infinity });
}
