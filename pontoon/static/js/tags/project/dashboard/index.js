
import ReactDOM from 'react-dom';
import React from 'react';

import ProjectTagsDashboard from './dashboard';


const node = document.getElementById('app');

ReactDOM.render(
        <ProjectTagsDashboard api={node.dataset.api} />,
    node);
