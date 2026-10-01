import { usePatchField } from '@api/snap';
import type { BoardModel, Rating } from '@lepton/api-client';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import React, { Suspense, useEffect, useMemo, useState } from 'react';
import { ContextualMenu } from '../../components/lib/contextualMenu/contextualMenu';
import { getBoardIntendedRatings } from '../../utils/ratings';

const DefaultElementComponent = React.lazy(() => import('../../components/elements/default'));
const ImageElementComponent = React.lazy(() => import('../../components/elements/image'));

const renderElement = (snapId: string, element: any) => {
    if (element == null) {
        return null;
    }

    if (Array.isArray(element)) {
        return element.map((child, index) => (
            <React.Fragment key={index}>{renderElement(snapId, child)}</React.Fragment>
        ));
    }

    if (typeof element !== 'object') {
        return element;
    }

    if (!element?.type) {
        if (Object.prototype.hasOwnProperty.call(element, 'content')) {
            return renderElement(snapId, element.content);
        }
        return null;
    }

    switch (element.type) {
        case 'image':
            return (
                <Suspense fallback={<div>Loading...</div>}>
                    <ImageElementComponent snapId={snapId} src={element.src} style={element.style} />
                </Suspense>
            );
        case 'row':
            return (
                <div style={{ display: 'flex', flexDirection: 'row', flexWrap: 'wrap', ...element.style }}>
                    {element.content?.map((child: any, index: number) => (
                        <div key={index} style={{ marginRight: index < element.content.length - 1 ? '8px' : '0' }}>
                            {renderElement(snapId, child)}
                        </div>
                    ))}
                </div>
            );
        case 'default':
            return <DefaultElementComponent style={element.style} content={renderElement(snapId, element.content)} />;
        default:
            return <p className="error-text">Unsupported element type: {element.type}</p>;
    }
};

const BoardElement: React.FC<{ snapId: string; intendedRatings: Rating[]; element: any }> = ({
    snapId,
    intendedRatings,
    element,
}) => {
    const { currentLObjectPath } = useLObjectSession();
    const patchField = usePatchField(currentLObjectPath, snapId);

    const menuItems: any[] = [
        { label: 'Show this board in all files', onClick: () => console.log('Show this board in all views clicked') },
        ...intendedRatings.map((rating: any) => ({
            label: rating.name,
            items: [
                ...(rating.scale?.ratings?.map((rate: any) => ({
                    label: rate.name,
                    onClick: () =>
                        patchField.mutate({ fieldPath: `ratings.{id:${rating.id}}.value`, value: rate.value }),
                    style: { backgroundColor: rate.color || '' },
                })) || []),
                { label: 'Comment', onClick: () => console.log('Comment clicked') },
                { label: 'Infos', onClick: () => console.log('Infos clicked') },
            ],
        })),
    ];

    return (
        <ContextualMenu parentClass="board" items={menuItems}>
            <div className="board-element">{renderElement(snapId, element)}</div>
        </ContextualMenu>
    );
};

const Board: React.FC<{ snapId: string; board: BoardModel }> = ({ snapId, board }) => {
    const [boardElements, setBoardElements] = useState<any[]>([]);
    const intendedRatings = useMemo(() => getBoardIntendedRatings(board), [board]);

    useEffect(() => {
        if (board.elements) {
            setBoardElements(board.elements);
        }
    }, [board.elements]);

    return (
        <div className="board">
            {board.description && <p>{board.description}</p>}
            {boardElements.map((element, index) => (
                <BoardElement key={index} snapId={snapId} intendedRatings={intendedRatings} element={element} />
            ))}
        </div>
    );
};

export default Board;
