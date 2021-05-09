/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import { useOnDiscard } from 'core/utils';

import './KeyboardShortcuts.css';

type Props = {};

type State = {|
    visible: boolean,
|};

type KeyboardShortcutsProps = {
    onDiscard: (e: MouseEvent) => void,
};

function KeyboardShortcuts({ onDiscard }: KeyboardShortcutsProps) {
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);
    return (
        <div ref={ref} className='overlay' onClick={onDiscard}>
            <Localized id='editor-KeyboardShortcuts--overlay-title'>
                <h2>KEYBOARD SHORTCUTS</h2>
            </Localized>
            <table>
                <tbody>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--save-translation'>
                            <td>Save Translation</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--save-translation-shortcut'
                            elems={{
                                accel: <span />,
                            }}
                        >
                            <td>{'<accel>Enter</accel>'}</td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--cancel-translation'>
                            <td>Cancel Translation</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--cancel-translation-shortcut'
                            elems={{
                                accel: <span />,
                            }}
                        >
                            <td>{'<accel>Esc</accel>'}</td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--insert-a-new-line'>
                            <td>Insert A New Line</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--insert-a-new-line-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                            }}
                        >
                            <td>
                                {'<mod1>Shift</mod1> + <accel>Enter</accel>'}
                            </td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--go-to-previous-string'>
                            <td>Go To Previous String</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--go-to-previous-string-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                            }}
                        >
                            <td>{'<mod1>Alt</mod1> + <accel>Up</accel>'}</td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--go-to-next-string'>
                            <td>Go To Next String</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--go-to-next-string-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                            }}
                        >
                            <td>{'<mod1>Alt</mod1> + <accel>Down</accel>'}</td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--copy-from-source'>
                            <td>Copy From Source</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--copy-from-source-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                                mod2: <span />,
                            }}
                        >
                            <td>
                                {
                                    '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>C</accel>'
                                }
                            </td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--clear-translation'>
                            <td>Clear Translation</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--clear-translation-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                                mod2: <span />,
                            }}
                        >
                            <td>
                                {
                                    '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Backspace</accel>'
                                }
                            </td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--search-strings'>
                            <td>Search Strings</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--search-strings-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                                mod2: <span />,
                            }}
                        >
                            <td>
                                {
                                    '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>F</accel>'
                                }
                            </td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--select-all-strings'>
                            <td>Select All Strings</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--select-all-strings-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                                mod2: <span />,
                            }}
                        >
                            <td>
                                {
                                    '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>A</accel>'
                                }
                            </td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--copy-from-previous-helper'>
                            <td>Copy From Previous Helper</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--copy-from-previous-helper-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                                mod2: <span />,
                            }}
                        >
                            <td>
                                {
                                    '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Up</accel>'
                                }
                            </td>
                        </Localized>
                    </tr>
                    <tr>
                        <Localized id='editor-KeyboardShortcuts--copy-from-next-helper'>
                            <td>Copy From Next Helper</td>
                        </Localized>
                        <Localized
                            id='editor-KeyboardShortcuts--copy-from-next-helper-shortcut'
                            elems={{
                                accel: <span />,
                                mod1: <span />,
                                mod2: <span />,
                            }}
                        >
                            <td>
                                {
                                    '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Down</accel>'
                                }
                            </td>
                        </Localized>
                    </tr>
                </tbody>
            </table>
        </div>
    );
}

/*
 * Shows a list of keyboard shortcuts.
 */
export default class KeyboardShortcutsBase extends React.Component<
    Props,
    State,
> {
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

    render(): React.Element<'div'> {
        return (
            <div className='keyboard-shortcuts'>
                <Localized
                    id='editor-KeyboardShortcuts--button'
                    attrs={{ title: true }}
                >
                    <div
                        className='selector far fa-keyboard'
                        title='Keyboard Shortcuts'
                        onClick={this.toggleVisibility}
                    />
                </Localized>

                {this.state.visible && (
                    <KeyboardShortcuts onDiscard={this.handleDiscard} />
                )}
            </div>
        );
    }
}
