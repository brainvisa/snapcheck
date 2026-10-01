import { usePatchField, useSnap } from '@api/snap';
import type { RatingModel } from '@lepton/api-client';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import React from 'react';
import FilesBrowser from '../../../components/files/browser/browser';
import InlineToggle from '../../../components/lib/inlineToggle';
import VerticalStackLayout, { type StackSection } from '../../../components/lib/layouts/verticalStackLayout';
import RatingInput from '../../../components/specials/ratinginput/ratinginput';
import { boardHasRating } from '../../../utils/ratings';
import './sidebar.css';

const FilesControl: React.FC<{}> = () => {
    const [currentPath, setCurrentPath] = React.useState<string | null>(null);
    const { openLObject, setLObjectSetting } = useLObjectSession();

    return (
        <FilesBrowser
            path={currentPath}
            onPathChange={(p) => setCurrentPath(p)}
            onFileSelect={(path: string) => {
                openLObject(path);
                setLObjectSetting('currentBoard', 0, path);
            }}
            extensions={['.snpk']}
        />
    );
};

const SnapControl: React.FC<{}> = () => {
    const { currentLObjectPath, currentObjectSettings } = useLObjectSession();
    const { data: snap } = useSnap(currentLObjectPath);
    const patchField = usePatchField(currentLObjectPath, snap?.id ?? undefined);

    const currentBoardIndex: number = currentObjectSettings.currentBoard || 0;
    const currentBoard = snap?.boards ? snap.boards[currentBoardIndex] : null;
    const [showAllratings, setShowAllRatings] = React.useState(true);

    const updateRatingField = (id: RatingModel['id'], field: string, value: any) => {
        patchField.mutate({ fieldPath: `ratings.{id:${id}}.${field}`, value });
    };

    return (
        <div className="snap-control-panel">
            <div className="panel-header">
                <div>
                    <InlineToggle
                        off="Board"
                        on="All"
                        value={showAllratings}
                        onChange={(value) => setShowAllRatings(value)}
                    />
                </div>
            </div>

            <div className="ratings-list">
                {snap?.id &&
                    snap?.ratings
                        ?.filter((rating) => currentBoard && (showAllratings || boardHasRating(currentBoard, rating)))
                        .map((rating) => (
                            <RatingInput
                                key={rating.id}
                                rating={rating}
                                onChange={updateRatingField}
                                highlight={
                                    (showAllratings && !!currentBoard && boardHasRating(currentBoard, rating)) || false
                                }
                            />
                        ))}
            </div>
        </div>
    );
};

const Sidebar: React.FC<{}> = () => {
    const menuItems: StackSection[] = [
        { id: 'files', title: 'Files', content: <FilesControl /> },
        { id: 'snap', title: 'Ratings', content: <SnapControl /> },
    ];

    return <VerticalStackLayout sections={menuItems} height="100%"></VerticalStackLayout>;
};

export default Sidebar;
