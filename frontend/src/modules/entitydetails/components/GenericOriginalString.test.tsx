import React from 'react';
import { shallow } from 'enzyme';

import GenericOriginalString from './GenericOriginalString';

const ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
};

const LOCALE = {
    code: 'kg',
    cldrPlurals: [1, 3, 5],
};

function createGenericOriginalString(pluralForm = -1) {
    return shallow(
        <GenericOriginalString
            entity={ENTITY}
            locale={LOCALE}
            pluralForm={pluralForm}
            terms={{}}
        />,
    );
}

describe('<GenericOriginalString>', () => {
    it('renders correctly', () => {
        const wrapper = createGenericOriginalString();

        const originalContent = wrapper.find('ContentMarker').props().children;
        expect(originalContent).toContain(ENTITY.original);
    });

    it('renders the selected plural form as original string', () => {
        const wrapper = createGenericOriginalString(2);

        expect(
            wrapper.find('#entitydetails-GenericOriginalString--plural'),
        ).toHaveLength(1);

        const originalContent = wrapper.find('ContentMarker').props().children;
        expect(originalContent).toContain(ENTITY.original_plural);
    });

    it('renders the selected singular form as original string', () => {
        const wrapper = createGenericOriginalString(0);

        expect(
            wrapper.find('#entitydetails-GenericOriginalString--singular'),
        ).toHaveLength(1);

        const originalContent = wrapper.find('ContentMarker').props().children;
        expect(originalContent).toContain(ENTITY.original);
    });
});
