import { useQuery } from '@tanstack/react-query';
import type React from 'react';
import { useEffect, useMemo } from 'react';
import { useSnapServices } from '../../../api/snapServices';

const ImageElementComponent: React.FC<{
    snapId: string;
    src: string;
    style?: React.CSSProperties;
}> = ({ snapId, src, style }) => {
    const snapServices = useSnapServices();

    // The image blob is cached by (snapId, src): switching boards or files and
    // coming back reuses it instead of re-downloading. staleTime Infinity because
    // a snap's assets don't change server-side while it is open.
    const { data: blob, isError } = useQuery({
        queryKey: ['snap-image', snapId, src],
        queryFn: () => snapServices.getSnapImage(snapId, src),
        enabled: !!snapId && !!src,
        staleTime: Infinity,
        gcTime: 1000 * 60 * 30, // keep for 30 min after the last board using it unmounts
    });

    // Derive a short-lived object URL from the cached blob and revoke it on
    // unmount. Recreating it is instant (no network) since the blob is cached.
    const imageUrl = useMemo(() => (blob ? URL.createObjectURL(blob) : null), [blob]);
    useEffect(() => {
        return () => {
            if (imageUrl) URL.revokeObjectURL(imageUrl);
        };
    }, [imageUrl]);

    if (isError) {
        return <div className="error-text">Image not found: {src}</div>;
    }

    return imageUrl ? <img src={imageUrl} alt={src} style={style} /> : <div>Loading...</div>;
};

export default ImageElementComponent;
