import * as React from 'react';
import { Localized } from '@fluent/react';

import type { BatchActionsState } from 'modules/batchactions';

type Props = {
    rejectAll: () => void;
    batchactions: BatchActionsState;
};

type State = {
    isConfirmationVisible: boolean;
};

/**
 * Renders Reject All batch action button.
 */
export default class RejectAll extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);

        this.state = {
            isConfirmationVisible: false,
        };
    }

    rejectAll: () => void = () => {
        if (!this.state.isConfirmationVisible) {
            this.setState({
                isConfirmationVisible: true,
            });
        } else {
            this.props.rejectAll();
            this.setState({
                isConfirmationVisible: false,
            });
        }
    };

    renderConfirmation(): React.ReactElement<React.ElementType> {
        return (
            <Localized id='batchactions-RejectAll--confirmation'>
                {'ARE YOU SURE?'}
            </Localized>
        );
    }

    renderDefault(): React.ReactElement<React.ElementType> {
        return (
            <Localized id='batchactions-RejectAll--default'>
                {'REJECT ALL SUGGESTIONS'}
            </Localized>
        );
    }

    renderError(): React.ReactElement<React.ElementType> {
        return (
            <Localized id='batchactions-RejectAll--error'>
                {'OOPS, SOMETHING WENT WRONG'}
            </Localized>
        );
    }

    renderInvalid(): null | React.ReactElement<React.ElementType> {
        const { response } = this.props.batchactions;

        if (!response) {
            return null;
        }

        return (
            <Localized
                id='batchactions-RejectAll--invalid'
                vars={{ invalidCount: response.invalidCount }}
            >
                {'{ $invalidCount } FAILED'}
            </Localized>
        );
    }

    renderSuccess(): null | React.ReactElement<React.ElementType> {
        const { response } = this.props.batchactions;

        if (!response) {
            return null;
        }

        return (
            <Localized
                id='batchactions-RejectAll--success'
                vars={{ changedCount: response.changedCount }}
            >
                {'{ $changedCount } STRINGS REJECTED'}
            </Localized>
        );
    }

    renderTitle(): null | React.ReactNode {
        const { response } = this.props.batchactions;

        if (response && response.action === 'reject') {
            if (response.error) {
                return this.renderError();
            } else if (response.invalidCount) {
                return (
                    <>
                        {this.renderSuccess()}
                        {' · '}
                        {this.renderInvalid()}
                    </>
                );
            } else {
                return this.renderSuccess();
            }
        } else if (this.state.isConfirmationVisible) {
            return this.renderConfirmation();
        } else {
            return this.renderDefault();
        }
    }

    render(): React.ReactElement<'button'> {
        return (
            <button className='reject-all' onClick={this.rejectAll}>
                {this.renderTitle()}
                {this.props.batchactions.requestInProgress !==
                'reject' ? null : (
                    <i className='fa fa-2x fa-circle-notch fa-spin'></i>
                )}
            </button>
        );
    }
}
