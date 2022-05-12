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
  const query = `{
    project(slug: "${slug}") {
      slug
      name
      info
      tags {
        name
        slug
        priority
      }
    }
  }`;
  const search = new URLSearchParams({ query });
  const res = await GET('/graphql', search);
  return res.data.project;
}
