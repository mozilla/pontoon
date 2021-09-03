import {
    createDefaultUser,
    createReduxStore,
    mountComponentWithStore,
} from 'test/store';

import { mockMatchMedia } from 'test/utils';

import Translation from './Translation';

const ORIGINAL = 'A horse, a horse! My kingdom for a horse!';
const DEFAULT_TRANSLATION = {
    sources: [
        {
            type: 'translation-memory',
        },
    ],
    original: ORIGINAL,
    translation: 'Un cheval, un cheval ! Mon royaume pour un cheval !',
};

function createTranslation(translation, entity) {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(Translation, store, {
        translation,
        entity,
    });

    createDefaultUser(store);

    return wrapper;
}

describe('<Translation>', () => {
    let getSelectionBackup;

    beforeAll(() => {
        getSelectionBackup = window.getSelection;
        window.getSelection = () => {
            return {
                toString: () => {},
            };
        };
        mockMatchMedia();
    });

    afterAll(() => {
        window.getSelection = getSelectionBackup;
    });

    it('renders a translation correctly', () => {
        const wrapper = createTranslation(DEFAULT_TRANSLATION);

        expect(
            wrapper.find('.original').find('GenericTranslation'),
        ).toHaveLength(1);
        expect(
            wrapper.find('.suggestion').find('GenericTranslation').props()
                .content,
        ).toContain('Un cheval, un cheval !');

        // No quality.
        expect(wrapper.find('.quality')).toHaveLength(0);
    });

    it('shows quality when possible', () => {
        const translation = {
            ...DEFAULT_TRANSLATION,
            quality: 100,
        };
        const wrapper = createTranslation(translation);

        expect(wrapper.find('.quality')).toHaveLength(1);
        expect(wrapper.find('.quality').text()).toEqual('100%');
    });
});
