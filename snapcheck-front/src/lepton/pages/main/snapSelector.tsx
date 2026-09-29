import { snapQueryOptions, useCloseSnap } from '@api/snap';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import { useQueries } from '@tanstack/react-query';
import TabSelector from '../../components/lib/tabSelector/tabSelector';

export const SnapSelector: React.FC = () => {
    const { openPaths, currentLObjectPath, setCurrentLObject, closeLObject } = useLObjectSession();
    const closeSnap = useCloseSnap();

    // One query per open tab (useQueries handles a dynamic number of hooks safely).
    const results = useQueries({ queries: openPaths.map((p) => snapQueryOptions(p)) });

    const items = openPaths.map((path, i) => {
        const snap = results[i]?.data;
        const name = snap?.filename ?? path.split('/').pop() ?? path;
        return {
            label: name + (snap?.has_changed ? ' *' : ''),
            onSelect: () => setCurrentLObject(path),
            onClose: () => {
                if (snap?.id) closeSnap.mutate({ snapId: snap.id, path });
                closeLObject(path);
            },
            isActive: path === currentLObjectPath,
        };
    });

    return <TabSelector items={items} />;
};
