/* @flow */

export const CLOSE: 'lightbox/CLOSE' = 'lightbox/CLOSE';
export const OPEN: 'lightbox/OPEN' = 'lightbox/OPEN';

/**
 * Open the lightbox to show the specified image.
 */
export type OpenAction = {
    type: typeof OPEN,
    image: string,
};
export function open(image: string): OpenAction {
    return {
        type: OPEN,
        image,
    };
}

/**
 * Hide the lightbox.
 */
export type CloseAction = {
    type: typeof CLOSE,
};
export function close(): CloseAction {
    return {
        type: CLOSE,
    };
}

export default {
    close,
    open,
};
