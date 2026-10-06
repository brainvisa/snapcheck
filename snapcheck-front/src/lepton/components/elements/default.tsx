import type React from 'react';

const DefaultElementComponent: React.FC<{
    style?: React.CSSProperties;
    content?: React.ReactNode;
    contentIsHtml?: boolean;
}> = ({ style, content, contentIsHtml = false }) => {
    if (contentIsHtml && typeof content === 'string') {
        // biome-ignore lint/security/noDangerouslySetInnerHtml: the element content is HTML from the snap file
        return <div style={style} dangerouslySetInnerHTML={{ __html: content }} />;
    }

    return <div style={style}>{content}</div>;
};

export default DefaultElementComponent;
