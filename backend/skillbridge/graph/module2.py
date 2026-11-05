from __future__ import annotations

import csv
import random
from collections import deque
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

import networkx as nx

from graph.knowledge_graph import SEED_DIR, DataValidationError, KnowledgeGraph, load_seed_tables

MODULE2_NODE_TYPES = (
    "student",
    "skill",
    "career_role",
    "course",
    "project",
    "opportunity",
)
MODULE2_EDGE_TYPES = (
    "has_skill",
    "requires",
    "prerequisite_of",
    "teaches",
    "uses_skill",
    "targets_role",
)
ALLOWED_VERIFICATION = {"synthetic", "unverified", "verified", "expired", "independently_verified"}


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _validate_date(value: str, *, field_name: str, record_id: str) -> None:
    if not value:
        return
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{record_id} has invalid {field_name} date {value!r}") from exc


def _validate_url(value: str, *, field_name: str, record_id: str) -> None:
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{record_id} has invalid {field_name} URL {value!r}")


def generate_demo_students(
    seed_dir: Path = SEED_DIR,
    count: int = 120,
    *,
    seed: int = 2026,
) -> dict[str, list[dict[str, str]]]:
    """Create deterministic demo student rows with valid references to the curated seed data."""
    if count < 100:
        raise ValueError("Demo student generation requires at least 100 profiles")

    tables = load_seed_tables(seed_dir)
    role_ids = [row["career_id"] for row in tables["careers.csv"]]
    skill_ids = [row["skill_id"] for row in tables["skills.csv"]]
    if not role_ids or not skill_ids:
        raise DataValidationError(["demo generation requires at least one role and skill in the seed data"])

    rng = random.Random(seed)
    academic_years = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate Student"]
    names = [
        "Avery", "Jordan", "Morgan", "Taylor", "Riley", "Quinn", "Harper", "Skyler",
        "Emerson", "Parker", "Cameron", "Drew", "Sage", "Casey", "Brooklyn", "Jamie",
        "Alex", "Blake", "Charlie", "Dakota", "Jules", "Lee", "Robin", "Remy",
    ]
    student_rows: list[dict[str, str]] = []
    skill_rows: list[dict[str, str]] = []
    role_rows: list[dict[str, str]] = []

    for index in range(1, count + 1):
        student_id = f"student-demo-{index:03d}"
        role_id = rng.choice(role_ids)
        student_name = f"{rng.choice(names)} {index:03d}"
        academic_year = rng.choice(academic_years)
        student_rows.append({
            "student_id": student_id,
            "student_name": student_name,
            "academic_year": academic_year,
            "target_role_id": role_id,
            "provenance": "synthetic_demo",
            "is_synthetic": "true",
        })
        role_rows.append({
            "student_id": student_id,
            "career_id": role_id,
            "provenance": "synthetic_demo",
        })

        selected_skill_ids = sorted(rng.sample(skill_ids, k=min(5, len(skill_ids))))
        for skill_id in selected_skill_ids:
            skill_rows.append({
                "student_id": student_id,
                "skill_id": skill_id,
                "proficiency": rng.choice(["Beginner", "Intermediate", "Advanced"]),
                "provenance": "synthetic_demo",
            })

    return {
        "students_demo.csv": student_rows,
        "student_roles_demo.csv": role_rows,
        "student_skills_demo.csv": skill_rows,
    }


def _write_demo_csv(path: Path, fieldnames: list[str], rows: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def generate_demo_opportunities(
    seed_dir: Path = SEED_DIR,
    count: int = 25,
    *,
    seed: int = 2027,
) -> dict[str, list[dict[str, str]]]:
    """Generate clearly synthetic opportunity fixtures without claiming authenticity."""
    tables = load_seed_tables(seed_dir)
    role_ids = [row["career_id"] for row in tables["careers.csv"]]
    skill_ids = [row["skill_id"] for row in tables["skills.csv"]]
    rng = random.Random(seed)

    opportunity_rows: list[dict[str, str]] = []
    role_rows: list[dict[str, str]] = []
    skill_rows: list[dict[str, str]] = []

    for index in range(1, count + 1):
        opportunity_id = f"opportunity-demo-{index:03d}"
        role_id = rng.choice(role_ids)
        selected_skills = sorted(rng.sample(skill_ids, k=min(3, len(skill_ids))))
        opportunity_rows.append({
            "opportunity_id": opportunity_id,
            "opportunity_name": f"Synthetic Opportunity {index:03d}",
            "organization": "Synthetic Example Organization",
            "opportunity_type": rng.choice(["internship", "project", "apprenticeship", "mentor_event"]),
            "location": rng.choice(["Remote", "Hybrid", "On-site"]),
            "application_url": f"https://example.invalid/{opportunity_id}/apply",
            "source_url": f"https://example.invalid/{opportunity_id}/source",
            "deadline": "",
            "verification_status": "synthetic",
            "provenance": "synthetic_demo",
            "is_synthetic": "true",
        })
        role_rows.append({
            "opportunity_id": opportunity_id,
            "career_id": role_id,
            "provenance": "synthetic_demo",
        })
        for skill_id in selected_skills:
            skill_rows.append({
                "opportunity_id": opportunity_id,
                "skill_id": skill_id,
                "provenance": "synthetic_demo",
            })

    return {
        "opportunities_demo.csv": opportunity_rows,
        "opportunity_roles_demo.csv": role_rows,
        "opportunity_skills_demo.csv": skill_rows,
    }


def ensure_demo_seed_files(seed_dir: Path = SEED_DIR, *, count: int = 120, seed: int = 2026) -> dict[str, list[dict[str, str]]]:
    demo_students = generate_demo_students(seed_dir, count=count, seed=seed)
    demo_opportunities = generate_demo_opportunities(seed_dir, count=max(25, min(25, count // 4)), seed=seed + 1)
    demo_data = {
        **demo_students,
        **demo_opportunities,
    }
    fieldnames = {
        "students_demo.csv": ["student_id", "student_name", "academic_year", "target_role_id", "provenance", "is_synthetic"],
        "student_roles_demo.csv": ["student_id", "career_id", "provenance"],
        "student_skills_demo.csv": ["student_id", "skill_id", "proficiency", "provenance"],
        "opportunities_demo.csv": ["opportunity_id", "opportunity_name", "organization", "opportunity_type", "location", "application_url", "source_url", "deadline", "verification_status", "provenance", "is_synthetic"],
        "opportunity_roles_demo.csv": ["opportunity_id", "career_id", "provenance"],
        "opportunity_skills_demo.csv": ["opportunity_id", "skill_id", "provenance"],
    }
    for filename, rows in demo_data.items():
        _write_demo_csv(seed_dir / filename, fieldnames[filename], rows)
    return demo_data


def import_opportunity_records(records: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for record in records:
        candidate = dict(record)
        opportunity_id = str(candidate.get("opportunity_id", "")).strip()
        opportunity_name = str(candidate.get("opportunity_name", "")).strip()
        if not opportunity_id or not opportunity_name:
            raise ValueError("Opportunity record requires opportunity_id and opportunity_name")
        if opportunity_id in seen:
            raise ValueError(f"Duplicate opportunity_id {opportunity_id!r}")
        seen.add(opportunity_id)

        organization = str(candidate.get("organization", "")).strip()
        opportunity_type = str(candidate.get("opportunity_type", "")).strip()
        location = str(candidate.get("location", "")).strip()
        application_url = str(candidate.get("application_url", "")).strip()
        source_url = str(candidate.get("source_url", "")).strip()
        deadline = str(candidate.get("deadline", "")).strip()
        verification_status = str(candidate.get("verification_status", "")).strip()
        provenance = str(candidate.get("provenance", "")).strip() or "manual_import"
        is_synthetic = str(candidate.get("is_synthetic", "")).strip().lower()

        required_fields = [
            ("opportunity_id", opportunity_id),
            ("opportunity_name", opportunity_name),
            ("organization", organization),
            ("opportunity_type", opportunity_type),
            ("location", location),
            ("application_url", application_url),
            ("source_url", source_url),
            ("verification_status", verification_status),
            ("provenance", provenance),
        ]
        missing = [field for field, value in required_fields if not value]
        if missing:
            raise ValueError(f"Opportunity {opportunity_id!r} is missing required field(s): {', '.join(missing)}")

        if verification_status not in ALLOWED_VERIFICATION:
            raise ValueError(f"Opportunity {opportunity_id!r} has unsupported verification_status {verification_status!r}")
        if verification_status in {"verified", "independently_verified", "expired"} and not source_url:
            raise ValueError(f"Opportunity {opportunity_id!r} requires source_url when verified")
        if is_synthetic in {"1", "true", "yes"} and verification_status not in {"synthetic", "unverified"}:
            raise ValueError(f"Synthetic opportunity {opportunity_id!r} must be marked synthetic or unverified")
        _validate_url(application_url, field_name="application_url", record_id=opportunity_id)
        _validate_url(source_url, field_name="source_url", record_id=opportunity_id)
        if deadline:
            _validate_date(deadline, field_name="deadline", record_id=opportunity_id)

        normalized.append({
            "opportunity_id": opportunity_id,
            "opportunity_name": opportunity_name,
            "organization": organization,
            "opportunity_type": opportunity_type,
            "location": location,
            "application_url": application_url,
            "source_url": source_url,
            "deadline": deadline,
            "verification_status": verification_status,
            "provenance": provenance,
            "is_synthetic": is_synthetic,
        })
    return normalized


class Module2Graph:
    """NetworkX-backed graph for students, skills, roles, resources, and opportunities."""

    def __init__(self, graph: nx.MultiDiGraph | None = None):
        self.graph = graph or nx.MultiDiGraph()
        self.nodes_by_id = {node_id: dict(attrs) for node_id, attrs in self.graph.nodes(data=True)}

    @classmethod
    def from_seed_dir(cls, seed_dir: Path = SEED_DIR, *, include_demo: bool = False) -> "Module2Graph":
        base = KnowledgeGraph.from_seed_dir(seed_dir, include_demo=include_demo)
        tables = load_seed_tables(seed_dir, include_demo=include_demo)
        student_proficiencies = {
            (row["student_id"], row["skill_id"]): row["proficiency"]
            for row in tables.get("student_skills_demo.csv", [])
        }
        graph = nx.MultiDiGraph()

        for node in base.nodes:
            graph.add_node(node["id"], **{key: value for key, value in node.items()})

        for edge in base.edges:
            relation = edge["relation"]
            source_id = edge["source"]
            target_id = edge["target"]
            payload = {
                "provenance": edge.get("provenance", ""),
            }

            if relation == "required_for":
                graph.add_edge(target_id, source_id, **payload, relation="requires")
                continue
            if relation == "prerequisite_for":
                graph.add_edge(source_id, target_id, **payload, relation="prerequisite_of")
                continue
            if relation == "demonstrates":
                graph.add_edge(source_id, target_id, **payload, relation="uses_skill")
                continue
            if relation == "has_skill":
                payload["proficiency"] = student_proficiencies.get((source_id, target_id), "")
                graph.add_edge(source_id, target_id, **payload, relation="has_skill")
                continue
            if relation == "requires":
                graph.add_edge(source_id, target_id, **payload, relation="requires")
                continue
            graph.add_edge(source_id, target_id, **payload, relation=relation)

        return cls(graph)

    def _node(self, identifier: str) -> dict[str, Any] | None:
        if not isinstance(identifier, str):
            return None
        candidate = identifier.strip()
        if not candidate:
            return None
        if candidate in self.graph.nodes:
            return dict(self.graph.nodes[candidate])
        normalized = candidate.casefold()
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("name", "").casefold() == normalized:
                return dict(attrs)
        return None

    def get_node(self, identifier: str, node_type: str | None = None) -> dict[str, Any] | None:
        node = self._node(identifier)
        if node is None:
            return None
        if node_type is not None and node.get("type") != node_type:
            return None
        return node

    def get_student_skills(self, student_id: str) -> list[dict[str, Any]]:
        student = self.get_node(student_id, "student")
        if student is None:
            raise KeyError(f"Unknown student {student_id!r}")
        results: list[dict[str, Any]] = []
        for _, target, data in self.graph.out_edges(student["id"], data=True):
            if data.get("relation") == "has_skill":
                skill = self.get_node(target, "skill")
                if skill is not None:
                    results.append({
                        "skill_id": target,
                        "skill_name": skill["name"],
                        "proficiency": data.get("proficiency", ""),
                    })
        return sorted(results, key=lambda item: item["skill_name"].casefold())

    def get_role_skills(self, role_identifier: str) -> list[dict[str, Any]]:
        role = self.get_node(role_identifier, "career_role")
        if role is None:
            raise KeyError(f"Unknown role {role_identifier!r}")
        results: list[dict[str, Any]] = []
        for _, target, data in self.graph.out_edges(role["id"], data=True):
            if data.get("relation") == "requires":
                skill = self.get_node(target, "skill")
                if skill is not None:
                    results.append({
                        "skill_id": target,
                        "skill_name": skill["name"],
                    })
        return sorted(results, key=lambda item: item["skill_name"].casefold())

    def get_courses_for_skill(self, skill_identifier: str) -> list[dict[str, Any]]:
        skill = self.get_node(skill_identifier, "skill")
        if skill is None:
            raise KeyError(f"Unknown skill {skill_identifier!r}")
        results: list[dict[str, Any]] = []
        for source, _, data in self.graph.in_edges(skill["id"], data=True):
            if data.get("relation") == "teaches":
                course = self.get_node(source, "course")
                if course is not None:
                    results.append({
                        "course_id": source,
                        "course_name": course["name"],
                    })
        return sorted(results, key=lambda item: item["course_name"].casefold())

    def shortest_path(
        self,
        start_identifier: str,
        end_identifier: str,
        *,
        relation: str | None = None,
        reverse: bool = False,
    ) -> list[str]:
        start = self.get_node(start_identifier)
        end = self.get_node(end_identifier)
        if start is None or end is None:
            raise KeyError("Unknown graph node")

        if relation is None:
            candidate = self.graph
        else:
            candidate = nx.MultiDiGraph()
            for source, target, key, attrs in self.graph.edges(keys=True, data=True):
                if attrs.get("relation") == relation:
                    candidate.add_edge(source, target, **attrs)

        if reverse:
            candidate = candidate.reverse(copy=True)

        try:
            return nx.shortest_path(candidate, start["id"], end["id"])
        except nx.NetworkXNoPath:
            return []

    def skill_gap_analysis(
        self,
        student_identifier: str,
        target_role_identifier: str,
        existing_skill_identifiers: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        student = self.get_node(student_identifier, "student")
        if student is None:
            raise KeyError(f"Unknown student {student_identifier!r}")
        role = self.get_node(target_role_identifier, "career_role")
        if role is None:
            raise KeyError(f"Unknown role {target_role_identifier!r}")

        if existing_skill_identifiers is None:
            known_skill_ids = {
                item["skill_id"] for item in self.get_student_skills(student["id"])
            }
        else:
            known_skill_ids = set(existing_skill_identifiers)
        analysis = self.skill_gap_for_skills(
            target_role_identifier,
            known_skill_ids,
        )
        analysis["student"] = student
        return analysis

    def skill_gap_for_skills(
        self,
        target_role_identifier: str,
        existing_skill_identifiers: Iterable[str],
    ) -> dict[str, Any]:
        """Calculate a role gap from supplied skills without persisting a student node."""
        role = self.get_node(target_role_identifier, "career_role")
        if role is None:
            raise KeyError(f"Unknown role {target_role_identifier!r}")

        known_skill_ids: set[str] = set()
        for identifier in existing_skill_identifiers:
            skill = self.get_node(identifier, "skill")
            if skill is None:
                raise ValueError(f"Unknown skill {identifier!r}")
            known_skill_ids.add(skill["id"])

        required_ids: set[str] = set()
        for _, target, data in self.graph.out_edges(role["id"], data=True):
            if data.get("relation") == "requires":
                required_ids.add(target)

        closure: list[str] = []
        seen: set[str] = set()
        queue: deque[str] = deque(sorted(required_ids))
        while queue:
            skill_id = queue.popleft()
            if skill_id in seen:
                continue
            seen.add(skill_id)
            closure.append(skill_id)
            for source, _, data in self.graph.in_edges(skill_id, data=True):
                if data.get("relation") == "prerequisite_of":
                    queue.append(source)

        missing = [skill_id for skill_id in closure if skill_id not in known_skill_ids]
        return {
            "target_role": role,
            "required_skill_ids": sorted(required_ids),
            "missing_skill_ids": missing,
            "missing_skills": [
                {
                    "skill_id": skill_id,
                    "skill_name": self.get_node(skill_id, "skill")["name"],
                }
                for skill_id in missing
            ],
            "coverage": {
                "known": sorted(known_skill_ids),
                "missing": missing,
            },
        }

    def bridge_courses_for_missing(
        self,
        missing_skill_identifiers: Iterable[str],
    ) -> list[dict[str, Any]]:
        """Rank courses by direct coverage of the supplied missing-skill IDs."""
        missing = set(missing_skill_identifiers)
        ranked: list[dict[str, Any]] = []
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("type") != "course":
                continue
            covered = [
                skill_id
                for _, skill_id, data in self.graph.out_edges(node_id, data=True)
                if data.get("relation") == "teaches" and skill_id in missing
            ]
            if not covered:
                continue
            ranked.append({
                "course_id": node_id,
                "course_name": attrs["name"],
                "covered_skill_ids": sorted(set(covered)),
                "coverage_count": len(set(covered)),
            })
        ranked.sort(
            key=lambda item: (
                -item["coverage_count"],
                item["course_name"].casefold(),
                item["course_id"],
            )
        )
        return ranked

    def bridge_course_recommendations(
        self,
        student_identifier: str,
        target_role_identifier: str,
        existing_skill_identifiers: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        analysis = self.skill_gap_analysis(
            student_identifier,
            target_role_identifier,
            existing_skill_identifiers,
        )
        return self.bridge_courses_for_missing(analysis["missing_skill_ids"])


def build_module2_graph(seed_dir: Path = SEED_DIR, *, include_demo: bool = False) -> Module2Graph:
    return Module2Graph.from_seed_dir(seed_dir, include_demo=include_demo)
