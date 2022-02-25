import React, { useState } from 'react';

import { TagResourceManager } from './manager.js';

export function TagResourcesButton(props) {
    const [open, setOpen] = useState(false);
    const message = open
        ? 'Hide the resource manager for this tag'
        : 'Manage resources for this tag';

    const toggle = (ev) => {
        ev.preventDefault();
        setOpen((open) => !open);
    };

    return (
        <div>
            <button onClick={toggle}>{message}</button>
            {open ? <TagResourceManager {...props} /> : null}
        </div>
    );
}
