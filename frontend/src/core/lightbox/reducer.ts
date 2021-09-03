import { CLOSE, OPEN } from './actions';

import type { CloseAction, OpenAction } from './actions';

type Action = CloseAction | OpenAction;

// Read-only state.
export type LightboxState = {
    readonly image: string;
    readonly isOpen: boolean;
};

const initial: LightboxState = {
    image: '',
    isOpen: false,
};

export default function reducer(
    state: LightboxState = initial,
    action: Action,
): LightboxState {
    switch (action.type) {
        case OPEN:
            return {
                image: action.image,
                isOpen: true,
            };
        case CLOSE:
            return {
                image: '',
                isOpen: false,
            };
        default:
            return state;
    }
}
