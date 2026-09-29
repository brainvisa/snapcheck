import { useServerContent } from '@api/snap';
import type React from 'react';

type ServerContentProps = {
    path: string;
    className?: string;
};

const ServerContent: React.FC<ServerContentProps> = ({ path, className }) => {
    const { data, error, isPending } = useServerContent(path);

    if (error) return <div className={className}>Error : {error.message}</div>;
    if (isPending || !data) return <div className={className}>Loading...</div>;

    return (
        <div
            className={className}
            // biome-ignore lint/security/noDangerouslySetInnerHtml: static HTML content served by the backend
            dangerouslySetInnerHTML={{ __html: data.content }}
        />
    );
};

export default ServerContent;
