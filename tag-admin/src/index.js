import React from 'react';
import ReactDOM from 'react-dom';

import { TagResourcesButton } from './button.js';

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.js-tag-resources').forEach((node) => {
        const { api, project, tag } = node.dataset;
        ReactDOM.render(
            <TagResourcesButton api={api} project={project} tag={tag} />,
            node,
        );
    });
});
