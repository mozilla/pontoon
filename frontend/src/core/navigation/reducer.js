/* @flow */

export type Action = {
    type: string,
};

export type State = {
    +locale: string,
    +project: string,
    +resource: string,
    +entity: number | null,
};


const initialParams: State = {
    locale: 'af',
    project: 'amo',
    resource: 'LC_MESSAGES/django.po',
    entity: null,
};

export default function reducer(state: State = initialParams, action:Action): State {
    switch (action.type) {
        default:
            return state;
    }
}
