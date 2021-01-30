import React from 'react';
import { render, unmountComponentAtNode } from 'react-dom';
import { act } from 'react-dom/test-utils';
import sinon from 'sinon';

import useOnDiscard from './useOnDiscard';

function TestComponent({ onDiscard }) {
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);
    return (
        <div>
            <div id='js-outside'>Outside Content</div>
            {/* Discardable element */}
            <div ref={ref}>
                <button id='js-inside'>Inside Content</button>
            </div>
        </div>
    );
}

describe('useOnDiscard', () => {
    let root;

    beforeEach(async () => {
        root = document.createElement('div');
        document.body.appendChild(root);
    });

    afterEach(() => {
        unmountComponentAtNode(root);
        root.remove();
        root = null;
    });

    it('runs discard callback upon outside click', () => {
        const onDiscardSpy = sinon.spy();
        act(() => {
            render(<TestComponent onDiscard={onDiscardSpy} />, root);
        });

        const click = new Event('click', { bubbles: true });
        const outside = document.getElementById('js-outside');
        outside.dispatchEvent(click);

        expect(onDiscardSpy.calledOnce).toBe(true);
    });

    it('does not run discard callback upon inside click', () => {
        const onDiscardSpy = sinon.spy();
        act(() => {
            render(<TestComponent onDiscard={onDiscardSpy} />, root);
        });

        const click = new Event('click', { bubbles: true });
        const inside = document.getElementById('js-inside');
        inside.dispatchEvent(click);

        expect(onDiscardSpy.callCount).toBe(0);
    });
});
