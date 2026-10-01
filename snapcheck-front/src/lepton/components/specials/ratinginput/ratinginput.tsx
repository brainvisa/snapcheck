import type { RatingModel, RatingScaleItem } from '@lepton/api-client';
import type React from 'react';
import { useEffect, useRef, useState } from 'react';

import './ratinginput.css';

interface RatingInputProps {
    rating: RatingModel;
    onChange?: (ratingId: RatingModel['id'], field: string, value: any) => void;
    highlight?: boolean;
}

const RatingInput: React.FC<RatingInputProps> = ({ rating, onChange, highlight }) => {
    // The value is driven directly by the cached document (single source of truth):
    // no local copy, so a change made anywhere (sidebar, board menu) shows up here.
    const selectedValue = rating.value;

    // The comment is free text: keep a local draft while typing, commit on blur.
    const [comment, setComment] = useState<string>(rating.comment || '');
    const commentInputRef = useRef<HTMLInputElement>(null);
    // Reseed the draft only when switching to another rating.
    useEffect(() => {
        setComment(rating.comment || '');
    }, [rating.id]);

    const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const raw = event.target.value;
        if (commentInputRef.current) {
            commentInputRef.current.focus();
        }
        if (onChange) {
            onChange(rating.id, 'value', raw === '' ? null : Number(raw));
        }
    };

    const commitComment = () => {
        if (onChange && comment !== (rating.comment || '')) {
            onChange(rating.id, 'comment', comment);
        }
    };

    const name = rating.name || 'Unnamed (#' + rating.id + ')';
    const selectedRatingScale = rating.scale?.ratings?.find((nt: RatingScaleItem) => nt.value === selectedValue);

    return (
        <div className={`rating-input ${highlight ? ' rating-highlight' : ''}`}>
            <div className="rating-state-bar"></div>
            <div className="rating-content">
                <div>
                    <span className="rating-name">{name}</span>
                    { rating.is_boolean ? (
                        <input type="checkbox" 
                            checked={selectedValue === 1}
                            onChange={(event) => {
                                if (onChange) {
                                    onChange(rating.id, 'value', event.target.checked ? 1 : 0);
                                }
                            }}
                        />
                        ) : (
                        <select
                            className="rating-select"
                            value={selectedValue === undefined || selectedValue === null ? '' : String(selectedValue)}
                            onChange={handleSelectChange}
                            disabled={rating.scale == null}
                            style={
                                selectedRatingScale && selectedRatingScale.color
                                    ? { backgroundColor: selectedRatingScale.color }
                                    : {}
                            }
                        >
                            <option value="">--</option>
                            {rating.scale?.ratings &&
                                rating.scale.ratings.map((nt: RatingScaleItem, idx: number) => (
                                    <option key={idx + 1} value={nt.value}>
                                        {nt.value} - {nt.name}
                                    </option>
                                ))}
                        </select>
                        )}
                </div>
                <div className="rating-second-line">
                    <input
                        type="text"
                        className="rating-comment"
                        ref={commentInputRef}
                        placeholder="No comment"
                        value={comment}
                        onChange={(event) => setComment(event.target.value)}
                        onBlur={commitComment}
                    />
                </div>
            </div>
        </div>
    );
};

export default RatingInput;
