import React from 'react';
import ReactDOM from 'react-dom';

import TagResourcesButton from './button';

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.js-tag-resources').forEach((node) => {
        ReactDOM.render(
            <TagResourcesButton
                project={node.dataset.project}
                tag={node.dataset.tag}
                api={node.dataset.api}
            />,
            node,
        );
    });
});
