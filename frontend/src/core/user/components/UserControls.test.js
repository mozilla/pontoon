import React from 'react';
import { shallow } from 'enzyme';

import SignIn from './SignIn';
import { UserControlsBase } from './UserControls';

describe('<UserControlsBase>', () => {
    it('shows a Sign in link when user is logged out', () => {
        const wrapper = shallow(
            <UserControlsBase user={{ isAuthenticated: false }} />,
        );

        expect(wrapper.find(SignIn)).toHaveLength(1);
    });

    it('hides a Sign in link when user is logged in', () => {
        const wrapper = shallow(
            <UserControlsBase user={{ isAuthenticated: true }} />,
        );

        expect(wrapper.find(SignIn)).toHaveLength(0);
    });
});
