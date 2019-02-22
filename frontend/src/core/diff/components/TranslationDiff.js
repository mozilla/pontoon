/* @flow */

import * as React from 'react';
import DiffMatchPatch from 'diff-match-patch';

import './TranslationDiff.css';


type Props = {|
    base: string,
    target: string,
|};


const dmp = new DiffMatchPatch();


/**
 * Render diff between the base and the target string.
 * 
 * Unchanged slices are wrapped in <span>.
 * Added slices are wrapped in <ins>.
 * Removed slices are wrapped in <del>.
 */
export default class TranslationDiff extends React.Component<Props> {
    getDiff(base: string, target: string) {
        const diff = dmp.diff_main(base, target);
    
        dmp.diff_cleanupSemantic(diff);
        dmp.diff_cleanupEfficiency(diff);
    
        return diff;
    }    

    render() {
        const { base, target } = this.props;
        const diff = this.getDiff(base, target)

        return diff.map((item, index) => {
            let type = item[0];
            let slice = item[1];
    
            switch(type) {
                case DiffMatchPatch.DIFF_INSERT:
                    return <ins key={ index }>{ slice }</ins>;
    
                case DiffMatchPatch.DIFF_DELETE:
                    return <del key={ index }>{ slice }</del>;
    
                default:
                    return <span key={ index }>{ slice }</span>;
            }
        });    
    }
}
