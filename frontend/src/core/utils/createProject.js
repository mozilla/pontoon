/* flow */

import type { Project } from 'core/project/actions';

const DEFAULT: Project = {
    slug: null,
    name: null,
    info: null,
    tags: [],
};

export default function createProject(opts: $Shape<Project>): Project {
    const project = Object.create(DEFAULT);
    Object.assign(project, opts);
    return project;
}
