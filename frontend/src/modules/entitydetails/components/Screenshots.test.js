import * as lightbox from '~/core/lightbox';

import Screenshots from './Screenshots';
import { createReduxStore, mountComponentWithStore } from 'test/store';
import sinon from 'sinon';

describe('<Screenshots>', () => {
    it('shows a Lightbox on image click', () => {
        const store = createReduxStore();
        const stub = sinon.stub(store, 'dispatch');
        const source = 'That is an image URL: http://link.to/image.png';
        const wrapper = mountComponentWithStore(Screenshots, store, {
            locale: 'kg',
            source,
        });
        wrapper.find('img').simulate('click');
        expect(
            stub.calledOnceWith(
                lightbox.actions.open('http://link.to/image.png'),
            ),
        ).toBeTruthy();
        store.dispatch.restore();
    });
});
