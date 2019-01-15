import React from 'react';
import { shallow } from 'enzyme';

import EditorProxy from './EditorProxy';
import FluentEditor from './FluentEditor';
import GenericEditor from './GenericEditor';


describe('<EditorProxy>', () => {
    it('returns null when the entity is empty', () => {
        const wrapper = shallow(<EditorProxy entity={ null } />);

        expect(wrapper.type()).toBeNull();
    });

    it('returns a FluentEditor when the format is ftl', () => {
        const wrapper = shallow(<EditorProxy entity={ { format: 'ftl' } } />);

        expect(wrapper.type()).toEqual(FluentEditor);
    });

    it('returns a GenericEditor when the format is not ftl', () => {
        const wrapper = shallow(<EditorProxy entity={ { format: 'po' } } />);

        expect(wrapper.type()).toEqual(GenericEditor);
    });
});
