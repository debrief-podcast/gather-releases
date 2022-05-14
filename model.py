# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = welcome_from_dict(json.loads(json_string))

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, List, Optional, Type, TypeVar, cast

import dateutil.parser

T = TypeVar("T")


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


@dataclass
class LatestRelease:
    created_at: datetime
    url: str
    tag_name: str
    published_at: datetime
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> LatestRelease:
        assert isinstance(obj, dict)
        created_at = from_datetime(obj.get("createdAt"))
        url = from_str(obj.get("url"))
        tag_name = from_str(obj.get("tagName"))
        published_at = from_datetime(obj.get("publishedAt"))
        name = from_union([from_none, from_str], obj.get("name"))
        return LatestRelease(created_at, url, tag_name, published_at, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["createdAt"] = self.created_at.isoformat()
        result["url"] = from_str(self.url)
        result["tagName"] = from_str(self.tag_name)
        result["publishedAt"] = self.published_at.isoformat()
        result["name"] = from_union([from_none, from_str], self.name)
        return result


@dataclass
class TargetTarget:
    committed_date: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> TargetTarget:
        assert isinstance(obj, dict)
        committed_date = from_union([from_datetime, from_none], obj.get("committedDate"))
        return TargetTarget(committed_date)

    def to_dict(self) -> dict:
        result: dict = {}
        result["committedDate"] = from_union([lambda x: x.isoformat(), from_none], self.committed_date)
        return result


@dataclass
class NodeTarget:
    id: str
    name: Optional[str] = None
    target: Optional[TargetTarget] = None
    committed_date: Optional[datetime] = None

    @staticmethod
    def from_dict(obj: Any) -> NodeTarget:
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        target = from_union([TargetTarget.from_dict, from_none], obj.get("target"))
        committed_date = from_union([from_datetime, from_none], obj.get("committedDate"))
        return NodeTarget(id, name, target, committed_date)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        result["target"] = from_union([lambda x: to_class(TargetTarget, x), from_none], self.target)
        result["committedDate"] = from_union([lambda x: x.isoformat(), from_none], self.committed_date)
        return result


@dataclass
class NodeElement:
    name: str
    target: NodeTarget

    @staticmethod
    def from_dict(obj: Any) -> NodeElement:
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        target = NodeTarget.from_dict(obj.get("target"))
        return NodeElement(name, target)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["target"] = to_class(NodeTarget, self.target)
        return result


@dataclass
class Refs:
    nodes: List[NodeElement]

    @staticmethod
    def from_dict(obj: Any) -> Refs:
        assert isinstance(obj, dict)
        nodes = from_list(NodeElement.from_dict, obj.get("nodes"))
        return Refs(nodes)

    def to_dict(self) -> dict:
        result: dict = {}
        result["nodes"] = from_list(lambda x: to_class(NodeElement, x), self.nodes)
        return result


@dataclass
class EdgeNode:
    name: str
    name_with_owner: str
    refs: Refs
    latest_release: Optional[LatestRelease] = None

    @staticmethod
    def from_dict(obj: Any) -> EdgeNode:
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        name_with_owner = from_str(obj.get("nameWithOwner"))
        refs = Refs.from_dict(obj.get("refs"))
        latest_release = from_union([LatestRelease.from_dict, from_none], obj.get("latestRelease"))
        return EdgeNode(name, name_with_owner, refs, latest_release)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["nameWithOwner"] = from_str(self.name_with_owner)
        result["refs"] = to_class(Refs, self.refs)
        result["latestRelease"] = from_union([lambda x: to_class(LatestRelease, x), from_none], self.latest_release)
        return result


@dataclass
class Edge:
    node: EdgeNode
    cursor: str

    @staticmethod
    def from_dict(obj: Any) -> Edge:
        assert isinstance(obj, dict)
        node = EdgeNode.from_dict(obj.get("node"))
        cursor = from_str(obj.get("cursor"))
        return Edge(node, cursor)

    def to_dict(self) -> dict:
        result: dict = {}
        result["node"] = to_class(EdgeNode, self.node)
        result["cursor"] = from_str(self.cursor)
        return result


@dataclass
class PageInfo:
    end_cursor: str
    has_next_page: bool

    @staticmethod
    def from_dict(obj: Any) -> PageInfo:
        assert isinstance(obj, dict)
        end_cursor = from_str(obj.get("endCursor"))
        has_next_page = from_bool(obj.get("hasNextPage"))
        return PageInfo(end_cursor, has_next_page)

    def to_dict(self) -> dict:
        result: dict = {}
        result["endCursor"] = from_str(self.end_cursor)
        result["hasNextPage"] = from_bool(self.has_next_page)
        return result


@dataclass
class Repositories:
    edges: List[Edge]
    page_info: PageInfo

    @staticmethod
    def from_dict(obj: Any) -> Repositories:
        assert isinstance(obj, dict)
        edges = from_list(Edge.from_dict, obj.get("edges"))
        page_info = PageInfo.from_dict(obj.get("pageInfo"))
        return Repositories(edges, page_info)

    def to_dict(self) -> dict:
        result: dict = {}
        result["edges"] = from_list(lambda x: to_class(Edge, x), self.edges)
        result["pageInfo"] = to_class(PageInfo, self.page_info)
        return result


@dataclass
class Organization:
    repositories: Repositories

    @staticmethod
    def from_dict(obj: Any) -> Organization:
        assert isinstance(obj, dict)
        repositories = Repositories.from_dict(obj.get("repositories"))
        return Organization(repositories)

    def to_dict(self) -> dict:
        result: dict = {}
        result["repositories"] = to_class(Repositories, self.repositories)
        return result


@dataclass
class Data:
    organization: Organization

    @staticmethod
    def from_dict(obj: Any) -> Data:
        assert isinstance(obj, dict)
        organization = Organization.from_dict(obj.get("organization"))
        return Data(organization)

    def to_dict(self) -> dict:
        result: dict = {}
        result["organization"] = to_class(Organization, self.organization)
        return result


@dataclass
class WelcomeElement:
    data: Data

    @staticmethod
    def from_dict(obj: Any) -> WelcomeElement:
        assert isinstance(obj, dict)
        data = Data.from_dict(obj.get("data"))
        return WelcomeElement(data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = to_class(Data, self.data)
        return result


def welcome_from_dict(s: Any) -> List[WelcomeElement]:
    return from_list(WelcomeElement.from_dict, s)


def welcome_to_dict(x: List[WelcomeElement]) -> Any:
    return from_list(lambda x: to_class(WelcomeElement, x), x)
