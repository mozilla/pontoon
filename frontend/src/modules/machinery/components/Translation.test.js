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

function createTranslation(
    translation,
    updateMachinerySources,
    updateEditorTranslation,
    addTextToEditorTranslation,
    entity?,
) {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(Translation, store, {
        translation,
        updateMachinerySources,
        updateEditorTranslation,
        addTextToEditorTranslation,
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
        const updateEditorTranslationMock = sinon.spy();
        const addTextToEditorTranslationMock = sinon.spy();
        const wrapper = createTranslation(
            DEFAULT_TRANSLATION,
            machineryMock,
            updateEditorTranslationMock,
            addTextToEditorTranslationMock,
        );

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

    it('calls addTextToEditorTranslation when clicking on a search term', () => {
        const machineryMock = sinon.stub();
        const updateEditorTranslationMock = sinon.spy();
        const addTextToEditorTranslationMock = sinon.spy();
        const wrapper = createTranslation(
            DEFAULT_TRANSLATION,
            machineryMock,
            updateEditorTranslationMock,
            addTextToEditorTranslationMock,
        );

        expect(addTextToEditorTranslationMock.called).toBeFalsy();
        wrapper.find('li.translation').simulate('click');
        expect(addTextToEditorTranslationMock.called).toBeTruthy();
        expect(
            addTextToEditorTranslationMock.calledWith(
                DEFAULT_TRANSLATION.translation,
            ),
        ).toBeTruthy();
    });

    it('calls updateEditorTranslation when an entity is present', () => {
        const machineryMock = sinon.stub();
        const entity = 770;
        const updateEditorTranslationMock = sinon.spy();
        const addTextToEditorTranslationMock = sinon.spy();
        const wrapper = createTranslation(
            DEFAULT_TRANSLATION,
            machineryMock,
            updateEditorTranslationMock,
            addTextToEditorTranslationMock,
            entity,
        );

        expect(updateEditorTranslationMock.called).toBeFalsy();
        wrapper.find('li.translation').simulate('click');
        expect(updateEditorTranslationMock.called).toBeTruthy();
        expect(
            updateEditorTranslationMock.calledWith(
                DEFAULT_TRANSLATION.translation,
                'machinery',
            ),
        ).toBeTruthy();
    });
});
