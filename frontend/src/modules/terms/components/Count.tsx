import * as React from 'react';

import type { TermState } from 'core/term';

type Props = {
    terms: TermState;
};

export default function TermCount(
    props: Props,
): null | React.ReactElement<'span'> {
    const { terms } = props;

    if (terms.fetching || !terms.terms) {
        return null;
    }

    const termCount = terms.terms.length;

    return <span className='count'>{termCount}</span>;
}
