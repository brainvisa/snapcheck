import { ApiTokenSync } from '@api/ApiTokenSync';
import { useCloseSnap, useSaveSnap, useSaveSnapAs, useSnap } from '@api/snap';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useEffect, useRef } from 'react';
import { useAppUIState } from './contexts/AppUIStateContext';
import Modal from './lepton/components/lib/modal/modal';
import MainContent from './lepton/pages/main/main';
import Sidebar from './lepton/pages/main/sidebar/sidebar';
import TopBar from './lepton/pages/main/topbar/topbar';
import './Snapcheck.css';

const ShortCuts: React.FC<{}> = () => {
    const { showSidebar, setState } = useAppUIState();
    const { currentLObjectPath, closeLObject } = useLObjectSession();
    const { data: snap } = useSnap(currentLObjectPath);
    const saveSnap = useSaveSnap();
    const saveSnapAs = useSaveSnapAs();
    const closeSnap = useCloseSnap();

    // Keep the latest values in a ref so the (mount-once) listener never sees stale state.
    const latest = useRef({ snap, showSidebar, currentLObjectPath });
    latest.current = { snap, showSidebar, currentLObjectPath };

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!e.ctrlKey) return;
            const key = e.key.toLowerCase();
            const { snap, showSidebar, currentLObjectPath } = latest.current;

            if (key === 'b') {
                e.preventDefault();
                setState({ showSidebar: !showSidebar });
            } else if (key === 's' && e.shiftKey) {
                e.preventDefault();
                if (snap?.id) {
                    const newPath = prompt('Enter the save path:');
                    if (newPath) saveSnapAs.mutate({ snapId: snap.id, newPath });
                }
            } else if (key === 's') {
                e.preventDefault();
                if (snap?.id && currentLObjectPath) saveSnap.mutate({ snapId: snap.id, path: currentLObjectPath });
            } else if (key === 'w') {
                e.preventDefault();
                if (snap?.id && currentLObjectPath) {
                    if (confirm('Are you sure you want to close the snap? Unsaved changes will be lost.')) {
                        closeSnap.mutate({ snapId: snap.id, path: currentLObjectPath });
                        closeLObject(currentLObjectPath);
                    }
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [setState, closeLObject, saveSnap, saveSnapAs, closeSnap]);

    return <></>;
};

function SnapCheck() {
    const { showSidebar } = useAppUIState();
    return (
        <div className="app">
            <ApiTokenSync />
            <ShortCuts />
            <div className="app-topbar">
                <TopBar />
            </div>
            <div className="page-container">
                <div className="sidebar-container" style={{ display: showSidebar ? 'block' : 'none' }}>
                    <Sidebar />
                </div>
                <div className="main-container">
                    <div className="board-container">
                        <MainContent />
                    </div>
                    <div className="modal-container">
                        <Modal />
                    </div>
                </div>
            </div>
            {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
        </div>
    );
}

export default SnapCheck;
