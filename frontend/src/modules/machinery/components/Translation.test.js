import sinon from 'sinon';

import {
    createDefaultUser,
    createReduxStore,
    mountComponentWithStore,
} from 'test/store';

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

function createTranslation(translation, updateMachinerySources) {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(Translation, store, {
        translation,
        updateMachinerySources,
        updateEditorTranslation: sinon.mock(),
        addTextToEditorTranslation: sinon.mock(),
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

    it('calls updateMachinerySources when clicking a translation', () => {
        const machineryMock = sinon.stub();
        const wrapper = createTranslation(DEFAULT_TRANSLATION, machineryMock);

        expect(machineryMock.calledOnce).toBeFalsy();
        expect(wrapper.find('li.translation')).toHaveLength(1);
        wrapper.find('li.translation').simulate('click');

        expect(machineryMock.calledOnce).toBeTruthy();
        expect(
            machineryMock.calledWith(
                DEFAULT_TRANSLATION.sources,
                DEFAULT_TRANSLATION.translation,
            ),
        ).toBeTruthy();
    });
});
