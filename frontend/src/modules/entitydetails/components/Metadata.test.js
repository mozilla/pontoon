import React from 'react';
import { shallow } from 'enzyme';

import Metadata from './Metadata';


const ENTITY = {
    pk: 42,
    original: 'le test',
    comment: 'my comment',
    path: 'path/to/RESOURCE',
    source: [
        ['file_source.rs', '31'],
    ],
    translation: [{string: 'the test'}],
    project: {
        slug: 'callme',
        name: 'CallMe',
    },
};


function createShallowMetadata(entity = ENTITY) {
    return shallow(<Metadata
        entity={ entity }
        locale="kg"
    />);
}


describe('<Metadata>', () => {
    it('renders correctly', () => {
        const wrapper = createShallowMetadata();

        const content = wrapper.text();
        expect(content).toContain(ENTITY.original);
        expect(content).toContain(ENTITY.comment);
        expect(content).toContain(ENTITY.source[0][0]);

        expect(wrapper.find('Link').props().to).toContain(ENTITY.path);
    });

    it('does not require a comment', () => {
        const wrapper = createShallowMetadata({ ...ENTITY, ...{ comment: '' } });

        const content = wrapper.text();
        expect(content).toContain(ENTITY.original);
        expect(content).not.toContain(ENTITY.comment);
        expect(content).toContain(ENTITY.source[0][0]);
    });

    it('does not require a source', () => {
        const wrapper = createShallowMetadata({ ...ENTITY, ...{ source: [] } });

        const content = wrapper.text();
        expect(content).toContain(ENTITY.original);
        expect(content).toContain(ENTITY.comment);
        expect(content).not.toContain(ENTITY.source[0][0]);
    });
});
