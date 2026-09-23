import React, { useEffect } from 'react';
import { useSnapServices } from '../../../api/snapServices';

const ImageElementComponent: React.FC<{
    snapId: string;
    src: string;
    style?: React.CSSProperties;
}> = ({ snapId, src, style }) => {

    const [imageUrl, setImageUrl] = React.useState<string | null>(null);
    const snapServices = useSnapServices();

    useEffect(() => {
        let url: string | null = null;
        const fetchImage = async () => {
            try {
                const blob = await snapServices.getSnapImage(snapId, src);
                url = URL.createObjectURL(blob);
                setImageUrl(url);
            } catch (error) {
                console.error('Error fetching image:', error);
                setImageUrl(null);
            }
        };
        fetchImage();
        // Cleanup function for useEffect
        return () => {
            if (url) {
                URL.revokeObjectURL(url);
            }
        };
    }, [snapId, src]);

    return imageUrl ? (
        <img src={imageUrl} alt={src} style={style} />
    ) : (
        <div>Loading...</div>
    );
};


export default ImageElementComponent;


