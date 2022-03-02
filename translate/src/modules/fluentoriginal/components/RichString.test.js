import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import RichString from './RichString';

const ORIGINAL = `
song-title = Hello
    .genre = Pop
    .album = Hello and Good Bye`;

const ENTITY = {
    original: ORIGINAL,
};

describe('<RichString>', () => {
    it('renders value and each attribute correctly', () => {
        const wrapper = shallow(<RichString entity={ENTITY} terms={{}} />);

        expect(wrapper.find('ContentMarker')).toHaveLength(3);

        expect(wrapper.find('label').at(0).html()).toContain('Value');
        expect(wrapper.find('ContentMarker').at(0).html()).toContain('Hello');

        expect(wrapper.find('label').at(1).html()).toContain('genre');
        expect(wrapper.find('ContentMarker').at(1).html()).toContain('Pop');

        expect(wrapper.find('label').at(2).html()).toContain('album');
        expect(wrapper.find('ContentMarker').at(2).html()).toContain(
            'Hello and Good Bye',
        );
    });

    it('renders select expression correctly', () => {
        const input = `
user-entry =
    { PLATFORM() ->
        [variant-1] Hello!
       *[variant-2] Good Bye!
    }`;

        const entity = {
            original: input,
        };

        const wrapper = shallow(<RichString entity={entity} terms={{}} />);

        expect(wrapper.find('ContentMarker')).toHaveLength(2);

        expect(wrapper.find('label').at(0).html()).toContain('variant-1');
        expect(wrapper.find('ContentMarker').at(0).html()).toContain('Hello!');

        expect(wrapper.find('label').at(1).html()).toContain('variant-2');
        expect(wrapper.find('ContentMarker').at(1).html()).toContain(
            'Good Bye!',
        );
    });

    it('renders select expression in attributes properly', () => {
        const input = `
my-entry =
    .label =
        { PLATFORM() ->
            [macosx] Preferences
           *[other] Options
        }
    .accesskey =
        { PLATFORM() ->
            [macosx] e
           *[other] s
        }`;

        const entity = {
            original: input,
        };

        const wrapper = shallow(<RichString entity={entity} terms={{}} />);

        expect(wrapper.find('ContentMarker')).toHaveLength(4);

        expect(wrapper.find('label .attribute-label').at(0).html()).toContain(
            'label',
        );
        expect(wrapper.find('label').at(0).html()).toContain('macosx');
        expect(wrapper.find('ContentMarker').at(0).html()).toContain(
            'Preferences',
        );

        expect(wrapper.find('label .attribute-label').at(1).html()).toContain(
            'label',
        );
        expect(wrapper.find('label').at(1).html()).toContain('other');
        expect(wrapper.find('ContentMarker').at(1).html()).toContain('Options');

        expect(wrapper.find('label .attribute-label').at(2).html()).toContain(
            'accesskey',
        );
        expect(wrapper.find('label').at(2).html()).toContain('macosx');
        expect(wrapper.find('ContentMarker').at(2).html()).toContain('e');

        expect(wrapper.find('label .attribute-label').at(3).html()).toContain(
            'accesskey',
        );
        expect(wrapper.find('label').at(3).html()).toContain('other');
        expect(wrapper.find('ContentMarker').at(3).html()).toContain('s');
    });

    it('calls the handleClickOnPlaceable function on click on .original', () => {
        const handleClickOnPlaceable = sinon.spy();
        const wrapper = shallow(
            <RichString
                entity={ENTITY}
                terms={{}}
                handleClickOnPlaceable={handleClickOnPlaceable}
            />,
        );

        wrapper.find('.original').simulate('click');
        expect(handleClickOnPlaceable.called).toEqual(true);
    });
});
