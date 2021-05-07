/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import { useOnDiscard } from 'core/utils';

import './EditorSettings.css';

import type { Settings } from 'core/user';

type Props = {|
    settings: Settings,
    updateSetting: Function,
|};

type State = {|
    visible: boolean,
|};

type EditorSettingsProps = {
    settings: Settings,
    toggleSetting: Function,
    onDiscard: (e: MouseEvent) => void,
};

export function EditorSettings({
    settings,
    toggleSetting,
    onDiscard,
}: EditorSettingsProps): React.Element<'ul'> {
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);

    return (
        <ul ref={ref} className='menu'>
            <Localized
                id='editor-EditorSettings--toolkit-checks'
                attrs={{ title: true }}
                elems={{ glyph: <i className='fa fa-fw' /> }}
            >
                <li
                    className={
                        'check-box' +
                        (settings.runQualityChecks ? ' enabled' : '')
                    }
                    title='Run Translate Toolkit checks before submitting translations'
                    onClick={() => toggleSetting('runQualityChecks')}
                >
                    {'<glyph></glyph>Translate Toolkit Checks'}
                </li>
            </Localized>

            <Localized
                id='editor-EditorSettings--force-suggestions'
                attrs={{ title: true }}
                elems={{ glyph: <i className='fa fa-fw' /> }}
            >
                <li
                    className={
                        'check-box' +
                        (settings.forceSuggestions ? ' enabled' : '')
                    }
                    title='Save suggestions instead of translations'
                    onClick={() => toggleSetting('forceSuggestions')}
                >
                    {'<glyph></glyph>Make Suggestions'}
                </li>
            </Localized>

            <li className='horizontal-separator'></li>
            <li>
                <Localized id='editor-EditorSettings--change-all'>
                    <a href='/settings/'>{'Change All Settings'}</a>
                </Localized>
            </li>
        </ul>
    );
}

/*
 * Renders settings to be used to customize interactions with the Editor.
 */
export default class EditorSettingsBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility: () => void = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    handleDiscard: () => void = () => {
        this.setState({
            visible: false,
        });
    };

    toggleSetting(name: string) {
        this.props.updateSetting(name, !this.props.settings[name]);
        this.toggleVisibility();
    }

    render(): React.Element<'div'> {
        return (
            <div className='editor-settings'>
                <div
                    className='selector fa fa-cog'
                    title='Settings'
                    onClick={this.toggleVisibility}
                />

                {this.state.visible && (
                    <EditorSettings
                        settings={this.props.settings}
                        toggleSetting={this.toggleSetting.bind(this)}
                        onDiscard={this.handleDiscard}
                    />
                )}
            </div>
        );
    }
}
