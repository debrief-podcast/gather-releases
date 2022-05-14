import csv
import json
from typing import List

from sultan.api import Sultan

import model

import sys

repo="apache"
if len(sys.argv) > 1:
    repo=sys.argv[1]

query = '''query ($endCursor: String) {
  organization(login: "'''+repo+'''") {
    repositories(
      first: 100
      orderBy: {field: UPDATED_AT, direction: DESC}
      after: $endCursor
    ) {
      edges {
        node {
          name
          nameWithOwner
          refs(
            refPrefix: "refs/tags/"
            orderBy: {field: TAG_COMMIT_DATE, direction: DESC}
            first: 1
          ) {
            nodes {
              name
              target {
                ... on Commit {
                  id
                  committedDate
                }
                ... on Tag {
                  id
                  name
                  target {
                    ... on Commit {
                      committedDate
                    }
                  }
                }
              }
            }
          }
          latestRelease {
            createdAt
            name
            url
            tagName
            publishedAt
          }
        }
        cursor
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}'''
s = Sultan()
r = s.gh(
    "api", "graphql", "--paginate", "--cache", "5h", "-f", f"query='{query}'"
).run()
lines: List[str] = r.stdout[0].replace('{"data"', '\n{"data"').replace("\n", "", 1).splitlines()
whole = f'[{",".join(lines)}]'
with open(f"{repo}.csv", "w+", newline="") as target:
    field_names = [
        "name_with_owner",
        "name",
        "date",
        "release_date",
        "release_name",
        "release_url",
    ]
    writer = csv.DictWriter(
        target, field_names, dialect="unix", quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    for root_node in model.welcome_from_dict(json.loads(whole)):
        for edge in root_node.data.organization.repositories.edges:
            node = edge.node
            ref_node = node.refs.nodes[0] if len(node.refs.nodes) > 0 else None
            if ref_node is None:
                date = None
            else:
                date = (
                    ref_node.target.committed_date
                    if ref_node.target.committed_date is not None
                    else ref_node.target.target.committed_date
                )
            release = node.latest_release
            writer.writerow(
                {
                    "name_with_owner": node.name_with_owner,
                    "name": ref_node.name if ref_node is not None else None,
                    "date": date,
                    "release_date": release.created_at if release is not None else None,
                    "release_name": release.name if release is not None else None,
                    "release_url": release.url if release is not None else None,
                }
            )
