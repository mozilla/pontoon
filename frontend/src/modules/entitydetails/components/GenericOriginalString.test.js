import React from 'react';
import { shallow } from 'enzyme';

import OriginalString from './OriginalString';


const ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
};

const LOCALE = {
    code: 'kg',
    cldrPlurals: [1, 3, 5],
};


function createOriginalString(pluralForm = -1) {
    return shallow(<OriginalString
        entity={ ENTITY }
        locale={ LOCALE }
        pluralForm={ pluralForm }
    />);
}


describe('<OriginalString>', () => {
    it('renders correctly', () => {
        const wrapper = createOriginalString();

        const originalContent = wrapper.find('ContentMarker').props().children;
        expect(originalContent).toContain(ENTITY.original);
    });

    it('renders the selected plural form as original string', () => {
        const wrapper = createOriginalString(2);

        expect(wrapper.find('#entitydetails-OriginalString--plural')).toHaveLength(1);

        const originalContent = wrapper.find('ContentMarker').props().children;
        expect(originalContent).toContain(ENTITY.original_plural);
    });

    it('renders the selected singular form as original string', () => {
        const wrapper = createOriginalString(0);

        expect(wrapper.find('#entitydetails-OriginalString--singular')).toHaveLength(1);

        const originalContent = wrapper.find('ContentMarker').props().children;
        expect(originalContent).toContain(ENTITY.original);
    });
});
