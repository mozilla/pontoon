/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from '@fluent/react';

import './KeyboardShortcuts.css';

type Props = null;

type State = {|
    visible: boolean,
|};

/*
 * Shows a list of keyboard shortcuts.
 */
export class KeyboardShortcutsBase extends React.Component<Props, State> {
    constructor() {
        super();
        this.state = {
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the keyboard shortcut overlay.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    };

    render() {
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

                {!this.state.visible ? null : (
                    <div className='overlay' onClick={this.toggleVisibility}>
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
                                            {
                                                '<mod1>Shift</mod1> + <accel>Enter</accel>'
                                            }
                                        </td>
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
                                        <td>
                                            {
                                                '<mod1>Alt</mod1> + <accel>Down</accel>'
                                            }
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
                                        <td>
                                            {
                                                '<mod1>Alt</mod1> + <accel>Up</accel>'
                                            }
                                        </td>
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
                                    <Localized id='editor-KeyboardShortcuts--copy-from-helpers'>
                                        <td>Copy From Helpers</td>
                                    </Localized>
                                    <Localized
                                        id='editor-KeyboardShortcuts--copy-from-helpers-shortcut'
                                        elems={{
                                            accel: <span />,
                                        }}
                                    >
                                        <td>{'<accel>Tab</accel>'}</td>
                                    </Localized>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        );
    }
}

export default onClickOutside(KeyboardShortcutsBase);
