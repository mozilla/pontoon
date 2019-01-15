import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import Entity from './Entity';


describe('<Entity>', () => {
    const ENTITY_A = {
        original: 'string a',
        translation: [
            {
                string: 'chaine a',
                approved: true,
            },
        ],
    };

    const ENTITY_B = {
        original: 'string b',
        translation: [
            {
                string: 'chaine b',
                fuzzy: true,
            },
        ],
    };

    const ENTITY_C = {
        original: 'string c',
        translation: [
            {
                string: 'chaine c',
            },
        ],
    };

    const DEFAULT_LOCALE = {
        direction: 'ltr',
        code: 'kg',
        script: 'Latin',
    };

    it('renders the source string and the first translation', () => {
        const wrapper = shallow(<Entity
            entity={ ENTITY_A }
            locale={ DEFAULT_LOCALE }
        />);

        expect(wrapper.text()).toContain(ENTITY_A.original);
        expect(wrapper.text()).toContain(ENTITY_A.translation[0].string);
    });

    it('shows the correct status class', () => {
        let wrapper = shallow(<Entity
            entity={ ENTITY_A }
            locale={ DEFAULT_LOCALE }
        />);
        expect(wrapper.instance().status).toEqual('approved');

        wrapper = shallow(<Entity
            entity={ ENTITY_B }
            locale={ DEFAULT_LOCALE }
        />);
        expect(wrapper.instance().status).toEqual('fuzzy');

        wrapper = shallow(<Entity
            entity={ ENTITY_C }
            locale={ DEFAULT_LOCALE }
        />);
        expect(wrapper.instance().status).toEqual('missing');
    });

    it('calls the selectEntity function on click', () => {
        const selectEntityFn = sinon.spy();
        const wrapper = mount(<Entity
            entity={ ENTITY_A }
            selectEntity={ selectEntityFn }
            locale={ DEFAULT_LOCALE }
        />);
        wrapper.find('li').simulate('click');
        expect(selectEntityFn.calledOnce).toEqual(true);
    });
});
