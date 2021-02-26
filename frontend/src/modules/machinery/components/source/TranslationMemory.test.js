import React from 'react';
import { shallow } from 'enzyme';

import TranslationMemory from './TranslationMemory';

const PROPS = {
    itemCount: 2,
};

describe('<TranslationMemory>', () => {
    it('renders the component without number of occurrences properly', () => {
        const wrapper = shallow(<TranslationMemory />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').at(0).props().id).toEqual(
            'machinery-TranslationMemory--pontoon-homepage',
        );
        expect(wrapper.find('li a').props().title).toContain(
            'Pontoon Homepage',
        );

        expect(wrapper.find('Localized').at(1).props().id).toEqual(
            'machinery-TranslationMemory--translation-memory',
        );
        expect(wrapper.find('li a span').text()).toEqual('TRANSLATION MEMORY');

        expect(wrapper.find('Localized')).toHaveLength(2);
    });

    it('renders the component with number of occurrences properly', () => {
        const wrapper = shallow(
            <TranslationMemory itemCount={PROPS.itemCount} />,
        );

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized')).toHaveLength(3);

        expect(wrapper.find('Localized').at(2).props().id).toEqual(
            'machinery-TranslationMemory--number-occurrences',
        );
        expect(wrapper.find('sup').props().title).toEqual(
            'Number of translation occurrences',
        );
        expect(wrapper.find('sup').text()).toContain(PROPS.itemCount);
    });
});
