import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import SimpleEditor from './SimpleEditor';

const ENTITIES = [
    {
        pk: 1,
        original: 'my-message = Hello',
        translation: [
            {
                string: 'my-message = Salut',
            },
        ],
    },
    {
        pk: 2,
        original: 'my-message = Hello\n    .my-attr = World!',
        translation: [{ string: 'my-message = Salut\n    .my-attr = Monde !' }],
    },
];

function createSimpleEditor({ entityIndex = 0 } = {}) {
    const sendTranslationMock = sinon.stub();
    const updateTranslationMock = sinon.stub();
    const wrapper = shallow(
        <SimpleEditor
            editor={{ translation: 'Salut' }}
            entity={ENTITIES[entityIndex]}
            translation={ENTITIES[entityIndex].translation[0].string}
            sendTranslation={sendTranslationMock}
            updateTranslation={updateTranslationMock}
        />,
    );

    return [wrapper, sendTranslationMock, updateTranslationMock];
}

describe('<SimpleEditor>', () => {
    it('parses content that come from an external source', () => {
        const [wrapper, , updateTranslationMock] = createSimpleEditor();

        wrapper.setProps({
            editor: {
                changeSource: 'external',
                translation: 'my-message = Coucou',
            },
        });

        expect(updateTranslationMock.calledOnce).toBeTruthy();
        expect(updateTranslationMock.calledWith('Coucou', true)).toBeTruthy();
    });

    it('sends a reconstructed translation to sendTranslation', () => {
        const [wrapper, sendTranslationMock] = createSimpleEditor();
        wrapper.instance().sendTranslation(false, 'Coucou');
        expect(sendTranslationMock.calledOnce).toBeTruthy();
        expect(
            sendTranslationMock.calledWith(false, 'my-message = Coucou\n'),
        ).toBeTruthy();
    });
});
