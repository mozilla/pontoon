import { GET } from './utils/base';

export type Tag = {
  readonly slug: string;
  readonly name: string;
  readonly priority: number;
};

export type Project = {
  slug: string;
  name: string;
  info: string;
  tags: Tag[];
};

export async function fetchProject(slug: string): Promise<Project> {
  return GET(`/api/v2/projects/${slug}`);
}
