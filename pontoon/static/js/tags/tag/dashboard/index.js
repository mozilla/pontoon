
import ReactDOM from 'react-dom';
import React from 'react';

import ProjectTagLocalesDashboard from './dashboard';


const node = document.getElementById('app');

ReactDOM.render(
        <ProjectTagLocalesDashboard api={node.dataset.api} />,
    node);
