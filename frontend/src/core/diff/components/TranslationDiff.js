/* @flow */

import * as React from 'react';

import './TranslationDiff.css';

import { getDiff } from '../withDiff';

type Props = {|
    base: string,
    target: string,
|};

/**
 * Render diff between the base and the target string.
 *
 * Unchanged slices are wrapped in <span>.
 * Added slices are wrapped in <ins>.
 * Removed slices are wrapped in <del>.
 */
export default class TranslationDiff extends React.Component<Props> {
    render() {
        const { base, target } = this.props;
        return getDiff(base, target);
    }
}
