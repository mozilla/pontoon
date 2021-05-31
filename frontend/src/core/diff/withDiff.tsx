import * as React from 'react';
import DiffMatchPatch from 'diff-match-patch';

import './components/TranslationDiff.css';

const dmp = new DiffMatchPatch();

export function getDiff(base: string, target: string): React.ReactNode {
    const diff = dmp.diff_main(base, target);

    dmp.diff_cleanupSemantic(diff);
    dmp.diff_cleanupEfficiency(diff);

    return diff.map((item, index) => {
        let type = item[0];
        let slice = item[1];

        switch (type) {
            case DiffMatchPatch.DIFF_INSERT:
                return <ins key={index}>{slice}</ins>;

            case DiffMatchPatch.DIFF_DELETE:
                return <del key={index}>{slice}</del>;

            default:
                return slice;
        }
    });
}

type Props = {
    diffTarget: string;
};

export default function withDiff<Config extends Record<string, any>>(
    WrappedComponent: React.ComponentType<Config>,
): React.ComponentType<Config> {
    return React.memo(function WithDiff(props: Config & Props) {
        return (
            <WrappedComponent {...props}>
                {getDiff(props.diffTarget, props.children)}
            </WrappedComponent>
        );
    });
}
