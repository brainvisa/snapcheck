import { useModal } from '@lepton/core/contexts/ModalContext';
import { Close, FilterNone, Maximize, Minimize } from '@mui/icons-material';
import { useEffect, useRef } from 'react';
import Menu from '../../../components/lib/menu/menu';
import ServerContent from '../../../components/lib/serverContent';
import { SnapSelector } from '../snapSelector';
import './topbar.css';
import { useSaveSnap, useSetSetting, useSetting, useSnap } from '@api/snap';
import { exportAsHtml } from '@lepton/api';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import { useAppUIState } from '../../../../contexts/AppUIStateContext';
import ExportHTMLPage from '../../exportHTML/exportHTML';

// Declare missing globals and types
declare const QWebChannel: any;

const TopBar: React.FC<{}> = () => {
    const { showModal } = useModal();
    const { showSidebar, setState } = useAppUIState();
    const { currentLObjectPath, openLObject } = useLObjectSession();
    const { data: snap } = useSnap(currentLObjectPath);
    const saveSnap = useSaveSnap();
    const autosave = useSetting('snap.autosave') === true;
    const setSetting = useSetSetting();

    const dragTimer = useRef<number | null>(null);
    const isDragDelayed = useRef(false);

    useEffect(() => {
        const handleGlobalMouseUp = () => {
            if (dragTimer.current) {
                clearTimeout(dragTimer.current);
                dragTimer.current = null;
                isDragDelayed.current = false;
            }
            stopWindowDrag();
        };
        document.addEventListener('mouseup', handleGlobalMouseUp);
        return () => document.removeEventListener('mouseup', handleGlobalMouseUp);
    }, []);

    const openFile = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.onchange = (e: any) => {
            const file = e.target.files?.[0];
            if (file) {
                openLObject(file.path);
            }
        };
        input.click();
    };

    const withBridge = (fn: (bridge: any) => void) => {
        if (typeof window !== 'undefined' && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, (channel: any) => {
                (window as any).bridge = channel.objects.bridge;
                fn((window as any).bridge);
            });
        }
    };

    const close = () => withBridge((b) => b.close());
    const maximize = () => withBridge((b) => b.maximize());
    const minimize = () => withBridge((b) => b.minimize());
    const restore = () => withBridge((b) => b.restore());
    const toggleWindowSize = () => withBridge((b) => b.toggleWindowSize());
    const startWindowDragDelayed = () => withBridge((b) => b.startWindowDrag());
    const stopWindowDrag = () => withBridge((b) => b.stopWindowDrag());

    const handleMouseDown = (e: React.MouseEvent) => {
        if (e.currentTarget === e.target && e.button === 0) {
            dragTimer.current = window.setTimeout(() => {
                startWindowDragDelayed();
                isDragDelayed.current = true;
            }, 150);
        }
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        if (e.currentTarget === e.target) {
            if (dragTimer.current) {
                clearTimeout(dragTimer.current);
                dragTimer.current = null;
                isDragDelayed.current = false;
            }
            toggleWindowSize();
        }
    };

    const toggleAutosave = () => {
        const enable = !autosave;
        setSetting.mutate({ path: 'snap.autosave', value: enable });
        // Save right away the modifications made before enabling the auto save
        if (enable && snap?.id && snap.has_changed) saveSnap.mutate({ snapId: snap.id, path: currentLObjectPath! });
    };

    const exportToHTML = () => {
        if (!snap || !snap.id) return;
        const snapId = snap.id;
        showModal(
            <ExportHTMLPage
                onSubmit={async (path: string) => {
                    try {
                        await exportAsHtml({ path: { snap_id: snapId, path }, throwOnError: true });
                        return false; // no error
                    } catch (error) {
                        console.error('Export failed:', error);
                        return 'An error occurred while exporting.';
                    }
                }}
            />,
        );
    };

    return (
        <div className="topbar" onMouseDown={handleMouseDown} onDoubleClick={handleDoubleClick}>
            <div>
                <img src="assets/icon-32.png" className="app-logo" />
                <Menu
                    items={[
                        {
                            label: 'File',
                            children: [
                                { label: 'Open file...', onClick: openFile },
                                { type: 'separator' },
                                {
                                    label: 'Save',
                                    onClick: () => {
                                        snap?.id && saveSnap.mutate({ snapId: snap.id, path: currentLObjectPath! });
                                    },
                                    disabled: !snap?.has_changed,
                                },
                                // {
                                //     label: 'Save As...',
                                //     onClick: () => {
                                //         if (snap?.id) {
                                //             const p = prompt('Enter the save path:');
                                //             if (p) saveSnapAs.mutate({ snapId: snap.id, newPath: p });
                                //         }
                                //     },
                                //     disabled: !snap?.id,
                                // },
                                { label: 'Auto save', onClick: toggleAutosave, checked: autosave },
                                { type: 'separator' },
                                { label: 'Export to HTML', onClick: exportToHTML, disabled: !snap },
                                { type: 'separator' },
                                { label: 'Quit', onClick: close },
                            ],
                        },
                        // {
                        //     label: 'Edit',
                        //     children: [],
                        // },
                        {
                            label: 'View',
                            children: [
                                {
                                    label: 'Show Sidebar',
                                    onClick: () => setState({ showSidebar: !showSidebar }),
                                    checked: showSidebar,
                                },
                            ],
                        },
                        {
                            label: 'More',
                            children: [
                                {
                                    label: 'About',
                                    onClick: () => {
                                        showModal(<ServerContent path="about.html" />);
                                    },
                                },
                            ],
                        },
                    ]}
                />
            </div>
            <div className="snap-selector-container">
                <SnapSelector />
            </div>
            <div className="topbar-buttons">
                <div onClick={minimize}>
                    <Minimize />
                </div>
                <div onClick={maximize}>
                    <Maximize />
                </div>
                <div onClick={restore}>
                    <FilterNone />
                </div>
                <div onClick={close}>
                    <Close />
                </div>
            </div>
        </div>
    );
};

export default TopBar;
