// @ts-nocheck
// https://github.com/mozilla/pontoon/issues/2292
import { $Diff } from 'utility-types';
import * as React from 'react';

type Props = {
    isActionDisabled: boolean | void;
    disableAction: (() => void) | void;
};

type State = {
    isActionDisabled: boolean;
};

export default function withActionsDisabled<Config extends {}>(
    WrappedComponent: React.ComponentType<Config>,
): React.ComponentType<$Diff<Config, Props>> {
    class WithActionsDisabled extends React.Component<
        $Diff<Config, Props>,
        State
    > {
        constructor(props: $Diff<Config, Props>) {
            super(props);

            this.state = {
                isActionDisabled: false,
            };
        }

        componentDidUpdate(prevProps: $Diff<Config, Props>, prevState: State) {
            if (prevState.isActionDisabled) {
                this.setState({ isActionDisabled: false });
            }
        }

        disableAction = () => {
            this.setState({ isActionDisabled: true });
        };

        render() {
            return (
                <WrappedComponent
                    {...this.props}
                    isActionDisabled={this.state.isActionDisabled}
                    disableAction={this.disableAction}
                />
            );
        }
    }

    WithActionsDisabled.displayName = `WithActionsDisabled(${
        WrappedComponent.displayName || WrappedComponent.name || 'Component'
    })`;
    return WithActionsDisabled;
}
