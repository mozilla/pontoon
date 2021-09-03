import * as React from 'react';

type Props = {
    getUserData: () => void;
};

/**
 * Regularly fetch user data to keep it up-to-date with the server.
 */
export default class UserAutoUpdater extends React.Component<Props> {
    timer: number | null;

    fetchUserData: () => void = () => {
        this.props.getUserData();
    };

    componentDidMount() {
        this.fetchUserData();
        this.timer = window.setInterval(this.fetchUserData, 2 * 60 * 1000);
    }

    componentWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    render(): null {
        return null;
    }
}
