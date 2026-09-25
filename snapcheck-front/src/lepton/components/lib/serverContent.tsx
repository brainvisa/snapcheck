import React from 'react';
import { useServerContent } from '@api/snap';

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
            dangerouslySetInnerHTML={{ __html: data.content }}
        />
    );
};

export default ServerContent;
