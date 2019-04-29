/* @flow */

import * as React from 'react';


type Props = Object;

type State = {|
    isActionDisabled: boolean,
|};


export default function withActionsDisabled<Config: Object>(
    WrappedComponent: React.AbstractComponent<Config>
): React.AbstractComponent<Config> {
    return class extends React.Component<Props, State> {
        constructor(props: Props) {
            super(props);

            this.state = {
                isActionDisabled: false,
            };
        }

        componentDidUpdate(prevProps: Props, prevState: State) {
            if (prevState.isActionDisabled) {
                this.setState({ isActionDisabled: false });
            }
        }

        restoreAction() {
            this.setState({ isActionDisabled: true });
        }

        render() {
            return <WrappedComponent
                isActionDisabled={ this.state.isActionDisabled }
                restoreAction={ this.restoreAction }
                { ...this.props }
            />;
        }
    };
}
