import type { BoardModel, Rating } from '@lepton/api-client';

/**
 * Return the ratings intended by the elements of a board, without duplicates (same id).
 *
 * The elements in rows and in the content of other elements are included.
 *
 * N.B: the intended ratings are copies of the ratings of the snap. Only use their id (or their
 * definition), and read and write the values in `snap.ratings`.
 *
 * @param board - The board
 * @returns The intended ratings, in the order of the elements
 */
export function getBoardIntendedRatings(board: BoardModel): Rating[] {
    const ratings = new Map<Rating['id'], Rating>();

    const visit = (item: unknown) => {
        if (Array.isArray(item)) {
            item.forEach(visit);
            return;
        }
        if (item == null || typeof item !== 'object') {
            return;
        }
        const element = item as { intended_ratings?: Rating[]; content?: unknown };
        for (const rating of element.intended_ratings ?? []) {
            if (!ratings.has(rating.id)) {
                ratings.set(rating.id, rating);
            }
        }
        visit(element.content);
    };

    visit(board.elements);
    return [...ratings.values()];
}

/**
 * Return true if a rating is intended by an element of the board (see getBoardIntendedRatings).
 */
export function boardHasRating(board: BoardModel, rating: Rating): boolean {
    return getBoardIntendedRatings(board).some((intendedRating) => intendedRating.id === rating.id);
}
