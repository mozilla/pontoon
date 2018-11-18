import React from 'react';
import { shallow } from 'enzyme';

import Metadata from './Metadata';


const ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
    comment: 'my comment',
    path: 'path/to/RESOURCE',
    source: [
        ['file_source.rs', '31'],
    ],
    translation: [
        { string: 'the test' },
        { string: 'plural' },
    ],
    project: {
        slug: 'callme',
        name: 'CallMe',
    },
};
const LOCALE = {
    code: 'kg',
    cldrPlurals: [1, 3, 5],
};


function createShallowMetadata(entity = ENTITY, pluralForm = -1) {
    return shallow(<Metadata
        entity={ entity }
        locale={ LOCALE }
        pluralForm={ pluralForm }
    />);
}


describe('<Metadata>', () => {
    it('renders correctly', () => {
        const wrapper = createShallowMetadata();

        const text = wrapper.text();
        expect(text).toContain(ENTITY.original);
        expect(text).toContain(ENTITY.source[0][0]);

        // Comments are hidden in a Linkify component.
        const content = wrapper.find('Linkify').map(item => item.props().children);
        expect(content).toContain(ENTITY.comment);

        expect(wrapper.find('Link').props().to).toContain(ENTITY.path);
    });

    it('renders the selected plural form as original string', () => {
        const wrapper = createShallowMetadata(ENTITY, 2);

        const text = wrapper.text();
        expect(wrapper.find('#entitydetails-metadata-plural')).toHaveLength(1);
        expect(text).toContain(ENTITY.original_plural);
    });

    it('renders the selected singular form as original string', () => {
        const wrapper = createShallowMetadata(ENTITY, 0);

        const text = wrapper.text();
        expect(wrapper.find('#entitydetails-metadata-singular')).toHaveLength(1);
        expect(text).toContain(ENTITY.original);
    });

    it('does not require a comment', () => {
        const wrapper = createShallowMetadata({ ...ENTITY, ...{ comment: '' } });

        const text = wrapper.text();
        expect(text).toContain(ENTITY.original);
        expect(text).toContain(ENTITY.source[0][0]);

        // Comments are hidden in a Linkify component.
        const content = wrapper.find('Linkify').map(item => item.props().children);
        expect(content).not.toContain(ENTITY.comment);
    });

    it('does not require a source', () => {
        const wrapper = createShallowMetadata({ ...ENTITY, ...{ source: [] } });

        const text = wrapper.text();
        expect(text).toContain(ENTITY.original);
        expect(text).not.toContain(ENTITY.source[0][0]);

        // Comments are hidden in a Linkify component.
        const content = wrapper.find('Linkify').map(item => item.props().children);
        expect(content).toContain(ENTITY.comment);
    });

    it('handles sources as an object', () => {
        const withSourceAsObject = {
            source: {
                arg1: {
                    content: '',
                    example: 'example_1',
                },
                arg2: {
                    content: '',
                    example: 'example_2',
                },
            }
        };
        const wrapper = createShallowMetadata({ ...ENTITY, ...withSourceAsObject });

        const sourceContent = wrapper.find('Property[title="Placeholder Examples"] Linkify').props().children;
        expect(sourceContent).toContain('$ARG1$: example_1');
        expect(sourceContent).toContain('$ARG2$: example_2');
    });
});
