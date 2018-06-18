const initialParams = {
    locale: 'af',
    project: 'amo',
    resource: 'LC_MESSAGES/django.po',
    entity: null,
};

export default function reducer(state = initialParams, action) {
    switch (action.type) {
        default:
            return state;
    }
}
