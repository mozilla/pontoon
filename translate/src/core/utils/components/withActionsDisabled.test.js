import React from 'react';
import { shallow } from 'enzyme';

import withActionsDisabled from './withActionsDisabled';

describe('withActionsDisabled', () => {
    class FakeComp extends React.Component {}
    const WrappedComp = withActionsDisabled(FakeComp);

    it('passes internal props correctly', () => {
        const wrapper = shallow(<WrappedComp />);

        expect(wrapper.props().isActionDisabled).toEqual(false);
        expect(wrapper.props().disableAction).toBeInstanceOf(Function);
    });

    it('passes other props along', () => {
        const wrapper = shallow(<WrappedComp foo='bar' baz={42} />);

        expect(wrapper.props().foo).toEqual('bar');
        expect(wrapper.props().baz).toEqual(42);
    });

    it('turns action off until next render', () => {
        const wrapper = shallow(<WrappedComp />);

        expect(wrapper.props().isActionDisabled).toEqual(false);

        // Disable the action.
        wrapper.instance().disableAction();
        expect(wrapper.props().isActionDisabled).toEqual(true);

        // Trigger a render.
        wrapper.setProps({ foo: 'var' });
        expect(wrapper.props().isActionDisabled).toEqual(false);
    });
});
