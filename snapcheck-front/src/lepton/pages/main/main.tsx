import { useSnap } from '@api/snap';
import type { BoardModel } from '@lepton/api-client';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import { useEffect } from 'react';
import { TransformComponent, TransformWrapper } from 'react-zoom-pan-pinch';
import Board from './board';
import './main.css';

const BoardView: React.FC<{ snapId: string; board: BoardModel | null }> = ({ snapId, board }) => {
    if (!board) {
        return (
            <div className="vertical-center">
                <p className="default-text">No boards available.</p>
            </div>
        );
    }

    return (
        <TransformWrapper
            limitToBounds={false}
            minScale={0.1}
            maxScale={10}
            panning={{ allowLeftClickPan: false, allowRightClickPan: false }}
        >
            <TransformComponent wrapperStyle={{ width: '100%', height: 'calc(100vh - 50px)' }}>
                <Board snapId={snapId} board={board} />
            </TransformComponent>
        </TransformWrapper>
    );
};

const MainContent: React.FC<{}> = () => {
    const { currentLObjectPath, setLObjectSetting, currentObjectSettings } = useLObjectSession();
    const { data: snap } = useSnap(currentLObjectPath);

    const currentBoardIndex: number = currentObjectSettings.currentBoard || 0;
    const currentBoard = snap?.boards ? snap.boards[currentBoardIndex] : null;

    const setCurrentBoard = (index: number) => {
        setLObjectSetting('currentBoard', index);
    };

    useEffect(() => {
        const handleTabKey = (event: KeyboardEvent) => {
            if (event.key === 'Tab') {
                event.preventDefault();
                if (snap?.boards && snap.boards.length > 0) {
                    setCurrentBoard((currentBoardIndex + 1) % snap.boards.length);
                }
            }
        };
        window.addEventListener('keydown', handleTabKey);
        return () => window.removeEventListener('keydown', handleTabKey);
    }, [currentBoardIndex, snap]);

    // No document currently open (e.g. after closing the last tab): show nothing,
    // regardless of any stale query data.
    if (!currentLObjectPath) {
        return (
            <div className="vertical-center">
                <p className="default-text">No document open.</p>
            </div>
        );
    }

    return (
        <div>
            <div className="main-header">
                {snap?.boards?.length ? (
                    <ul className="board-list">
                        {snap.boards.map((board: BoardModel, index: number) => (
                            <li
                                key={index}
                                onClick={() => setCurrentBoard(index)}
                                className={currentBoardIndex === index ? 'active' : ''}
                            >
                                {board.title}
                            </li>
                        ))}
                    </ul>
                ) : null}
                <span>{snap?.title}</span>
            </div>
            <BoardView snapId={snap?.id || ''} board={currentBoard} />
        </div>
    );
};

export default MainContent;
