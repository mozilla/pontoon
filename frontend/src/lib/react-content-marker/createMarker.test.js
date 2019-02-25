import React from 'react';
import { shallow } from 'enzyme';

import createMarker from './createMarker';


describe('createMarker', () => {
    it('returns a correct component', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';
        const parsers = [
            { rule: 'horse', tag: x => <i>{x}</i> },
            { rule: /(a)/gi, tag: x => <b>{x}</b> },
            { rule: /king\w+/, tag: x => <u>{x}</u> },
        ];
        const ContentMarker = createMarker(parsers);

        const wrapper = shallow(<ContentMarker>{ content }</ContentMarker>);
        expect(wrapper.find('i')).toHaveLength(3);
        expect(wrapper.find('b')).toHaveLength(3);
        expect(wrapper.find('u')).toHaveLength(1);
    });
});
