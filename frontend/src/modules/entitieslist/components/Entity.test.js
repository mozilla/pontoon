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
                errors: [],
                warnings: [],
            },
        ],
    };

    const ENTITY_B = {
        original: 'string b',
        translation: [
            {
                string: 'chaine b',
                fuzzy: true,
                errors: [],
                warnings: [],
            },
        ],
    };

    const ENTITY_C = {
        original: 'string c',
        translation: [
            {
                string: 'chaine c',
                errors: [],
                warnings: [],
            },
        ],
    };

    const ENTITY_D = {
        original: 'string d',
        translation: [
            {
                string: 'chaine d',
                approved: true,
                errors: ['error'],
                warnings: [],
            },
        ],
    };

    const ENTITY_E = {
        original: 'string e',
        translation: [
            {
                string: 'chaine e',
                fuzzy: true,
                errors: [],
                warnings: ['warning'],
            },
        ],
    };

    const ENTITY_F = {
        original: 'string f',
        translation: [
            {
                string: 'chaine f1',
                approved: true,
                errors: [],
                warnings: [],
            },
            {
                string: 'chaine f2',
                fuzzy: true,
                errors: [],
                warnings: [],
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

        const contents = wrapper.find('ContentMarker');
        expect(contents.first().props().children).toContain(ENTITY_A.original);
        expect(contents.last().props().children).toContain(ENTITY_A.translation[0].string);
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

        wrapper = shallow(<Entity
            entity={ ENTITY_D }
            locale={ DEFAULT_LOCALE }
        />);
        expect(wrapper.instance().status).toEqual('errors');

        wrapper = shallow(<Entity
            entity={ ENTITY_E }
            locale={ DEFAULT_LOCALE }
        />);
        expect(wrapper.instance().status).toEqual('warnings');

        wrapper = shallow(<Entity
            entity={ ENTITY_F }
            locale={ DEFAULT_LOCALE }
        />);
        expect(wrapper.instance().status).toEqual('partial');
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
