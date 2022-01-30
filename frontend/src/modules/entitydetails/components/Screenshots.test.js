import * as lightbox from 'core/lightbox';

import Screenshots from './Screenshots';
import { createReduxStore, mountComponentWithStore } from 'test/store';

describe('<Screenshots>', () => {
    it('shows a Lightbox on image click', () => {
        const store = createReduxStore();
        const source = 'That is an image URL: http://link.to/image.png';
        const wrapper = mountComponentWithStore(Screenshots, store, {
            locale: 'kg',
            source,
        });
        wrapper.find('img').simulate('click');

        const newState = store.getState()[lightbox.NAME];

        expect(newState.image).toEqual('http://link.to/image.png');
    });
});
