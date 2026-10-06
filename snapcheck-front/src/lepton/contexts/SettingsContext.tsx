import { useSettingsQuery } from '@api/snap';
import type { DefaultProps } from '../core/types';

/** Settings now come from the TanStack cache. Provider kept as a passthrough
 *  for backward compatibility with existing mount points. */
export function SettingsProvider(props: DefaultProps) {
    return <>{props.children}</>;
}

export function useSettings() {
    const { data, isPending } = useSettingsQuery();
    return {
        settings: data ?? [],
        loading: isPending,
    };
}
