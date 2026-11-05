"""CSV-backed SkillBridge knowledge graph and explainable learning recommendations."""

from __future__ import annotations

import csv
import json
from collections import defaultdict, deque
from datetime import date
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


BACKEND_DIR = Path(__file__).resolve().parents[1]
SEED_DIR = BACKEND_DIR / "data_seed"
GRAPH_FILE = BACKEND_DIR / "graph_data.json"

DATASET_SCHEMAS: dict[str, tuple[str, ...]] = {
    "skills.csv": (
        "skill_id", "skill_name", "category", "proficiency", "description",
        "provenance", "source_url", "verification_status",
    ),
    "careers.csv": (
        "career_id", "career_name", "domain", "description", "entry_level",
        "provenance", "source_url", "verification_status", "source_verified_at",
    ),
    "courses.csv": (
        "course_id", "course_name", "provider", "description", "source_url",
        "provenance", "verification_status", "source_verified_at",
    ),
    "projects.csv": (
        "project_id", "project_name", "description", "source_url", "provenance",
        "verification_status",
    ),
    "certifications.csv": (
        "certification_id", "certification_name", "provider", "description",
        "source_url", "provenance", "verification_status", "source_verified_at",
    ),
    "opportunities.csv": (
        "opportunity_id", "opportunity_name", "provider", "description",
        "source_url", "eligibility_criteria", "deadline", "source_verified_at",
        "provenance", "verification_status",
    ),
    "students.csv": (
        "student_id", "student_name", "provenance",
    ),
    "career_skills.csv": ("career_id", "skill_id", "provenance"),
    "course_skills.csv": ("course_id", "skill_id", "provenance"),
    "project_skills.csv": ("project_id", "skill_id", "provenance"),
    "certification_skills.csv": ("certification_id", "skill_id", "provenance"),
    "opportunity_skills.csv": ("opportunity_id", "skill_id", "provenance"),
    "student_skills.csv": ("student_id", "skill_id", "provenance"),
    "skill_prerequisites.csv": ("skill_id", "prerequisite_skill_id", "provenance"),
}

DEMO_DATASET_SCHEMAS: dict[str, tuple[str, ...]] = {
    "students_demo.csv": (
        "student_id", "student_name", "academic_year", "target_role_id",
        "provenance", "is_synthetic",
    ),
    "student_skills_demo.csv": (
        "student_id", "skill_id", "proficiency", "provenance",
    ),
    "student_roles_demo.csv": (
        "student_id", "career_id", "provenance",
    ),
    "opportunities_demo.csv": (
        "opportunity_id", "opportunity_name", "organization", "opportunity_type",
        "location", "application_url", "source_url", "deadline",
        "verification_status", "provenance", "is_synthetic",
    ),
    "opportunity_roles_demo.csv": (
        "opportunity_id", "career_id", "provenance",
    ),
    "opportunity_skills_demo.csv": (
        "opportunity_id", "skill_id", "provenance",
    ),
}

ENTITY_FILES = {
    "skill": ("skills.csv", "skill_id", "skill_name"),
    "career_role": ("careers.csv", "career_id", "career_name"),
    "course": ("courses.csv", "course_id", "course_name"),
    "project": ("projects.csv", "project_id", "project_name"),
    "certification": (
        "certifications.csv", "certification_id", "certification_name",
    ),
    "opportunity": ("opportunities.csv", "opportunity_id", "opportunity_name"),
    "student": ("students.csv", "student_id", "student_name"),
}

RELATION_FILES = (
    ("career_skills.csv", "career_id", "career_role", "skill_id", "skill", "required_for"),
    ("course_skills.csv", "course_id", "course", "skill_id", "skill", "teaches"),
    ("project_skills.csv", "project_id", "project", "skill_id", "skill", "demonstrates"),
    (
        "certification_skills.csv", "certification_id", "certification",
        "skill_id", "skill", "validates",
    ),
    (
        "opportunity_skills.csv", "opportunity_id", "opportunity",
        "skill_id", "skill", "requires",
    ),
    ("student_skills.csv", "student_id", "student", "skill_id", "skill", "has_skill"),
)

DEMO_RELATION_FILES = (
    ("student_skills_demo.csv", "student_id", "student", "skill_id", "skill", "has_skill"),
    ("student_roles_demo.csv", "student_id", "student", "career_id", "career_role", "targets_role"),
    ("opportunity_roles_demo.csv", "opportunity_id", "opportunity", "career_id", "career_role", "targets_role"),
    ("opportunity_skills_demo.csv", "opportunity_id", "opportunity", "skill_id", "skill", "requires"),
)

REQUIRED_NONEMPTY_FIELDS = {
    "skills.csv": ("skill_id", "skill_name", "category", "proficiency", "description", "provenance", "verification_status"),
    "careers.csv": ("career_id", "career_name", "domain", "description", "entry_level", "provenance", "verification_status"),
    "courses.csv": ("course_id", "course_name", "provider", "description", "source_url", "provenance", "verification_status", "source_verified_at"),
    "projects.csv": ("project_id", "project_name", "description", "provenance", "verification_status"),
    "certifications.csv": ("certification_id", "certification_name", "provider", "description", "source_url", "provenance", "verification_status", "source_verified_at"),
    "opportunities.csv": ("opportunity_id", "opportunity_name", "provider", "description", "source_url", "eligibility_criteria", "deadline", "source_verified_at", "provenance", "verification_status"),
    "students.csv": ("student_id", "student_name", "provenance"),
    "career_skills.csv": ("career_id", "skill_id", "provenance"),
    "course_skills.csv": ("course_id", "skill_id", "provenance"),
    "project_skills.csv": ("project_id", "skill_id", "provenance"),
    "certification_skills.csv": ("certification_id", "skill_id", "provenance"),
    "opportunity_skills.csv": ("opportunity_id", "skill_id", "provenance"),
    "student_skills.csv": ("student_id", "skill_id", "provenance"),
    "skill_prerequisites.csv": ("skill_id", "prerequisite_skill_id", "provenance"),
}

DEMO_REQUIRED_NONEMPTY_FIELDS = {
    "students_demo.csv": ("student_id", "student_name", "academic_year", "target_role_id", "provenance", "is_synthetic"),
    "student_skills_demo.csv": ("student_id", "skill_id", "proficiency", "provenance"),
    "student_roles_demo.csv": ("student_id", "career_id", "provenance"),
    "opportunities_demo.csv": ("opportunity_id", "opportunity_name", "organization", "opportunity_type", "location", "application_url", "source_url", "verification_status", "provenance", "is_synthetic"),
    "opportunity_roles_demo.csv": ("opportunity_id", "career_id", "provenance"),
    "opportunity_skills_demo.csv": ("opportunity_id", "skill_id", "provenance"),
}


class DataValidationError(ValueError):
    """Raised when a seed dataset cannot safely be used to build the graph."""

    def __init__(self, issues: Iterable[str]):
        self.issues = list(issues)
        super().__init__("; ".join(self.issues))


def _read_table(seed_dir: Path, filename: str) -> list[dict[str, str]]:
    schema_map = DATASET_SCHEMAS | DEMO_DATASET_SCHEMAS
    path = seed_dir / filename
    if not path.is_file():
        raise DataValidationError([f"{filename}: file is missing"])
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            expected_header = schema_map[filename]
            if tuple(reader.fieldnames or ()) != expected_header:
                raise DataValidationError(
                    [f"{filename}: expected header {expected_header}"]
                )
            rows = []
            for line_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise DataValidationError(
                        [f"{filename}: line {line_number} has the wrong number of fields"]
                    )
                rows.append({key: value.strip() for key, value in row.items()})
    except (OSError, UnicodeError, csv.Error) as error:
        raise DataValidationError([f"{filename}: cannot read CSV: {error}"]) from error
    return rows


def _validate_date(
    value: str,
    filename: str,
    record_id: str,
    field_name: str,
    issues: list[str],
) -> None:
    if value:
        try:
            date.fromisoformat(value)
        except ValueError:
            issues.append(
                f"{filename}: {record_id} has invalid {field_name} date {value!r}"
            )


def _validate_url(value: str, filename: str, record_id: str, issues: list[str]) -> None:
    parsed = urlparse(value)
    if value and (parsed.scheme not in {"http", "https"} or not parsed.netloc):
        issues.append(f"{filename}: {record_id} has invalid HTTP(S) source_url {value!r}")


def _all_dataset_schemas(include_demo: bool = False) -> dict[str, tuple[str, ...]]:
    schemas = dict(DATASET_SCHEMAS)
    if include_demo:
        schemas.update(DEMO_DATASET_SCHEMAS)
    return schemas


def _all_required_fields(include_demo: bool = False) -> dict[str, tuple[str, ...]]:
    fields = dict(REQUIRED_NONEMPTY_FIELDS)
    if include_demo:
        fields.update(DEMO_REQUIRED_NONEMPTY_FIELDS)
    return fields


def _all_entity_files() -> dict[str, tuple[str, str, str]]:
    return dict(ENTITY_FILES)


def _all_relation_files(include_demo: bool = False) -> tuple[tuple[str, str, str, str, str, str], ...]:
    relation_files = tuple(RELATION_FILES)
    if include_demo:
        relation_files = relation_files + tuple(DEMO_RELATION_FILES)
    return relation_files


def load_seed_tables(seed_dir: Path = SEED_DIR, include_demo: bool = False) -> dict[str, list[dict[str, str]]]:
    """Read and validate every active CSV, including demo records when explicitly enabled."""
    tables = {
        filename: _read_table(seed_dir, filename)
        for filename in _all_dataset_schemas(include_demo=include_demo)
        if (seed_dir / filename).exists()
    }
    issues: list[str] = []

    allowed_verification_statuses = {
        "independently_verified", "unverified", "verified", "expired", "synthetic"
    }
    required_fields = _all_required_fields(include_demo=include_demo)
    for filename, rows in tables.items():
        for line_number, row in enumerate(rows, start=2):
            missing = [
                field for field in required_fields.get(filename, ())
                if not row.get(field, "")
            ]
            if missing:
                issues.append(
                    f"{filename}: line {line_number} has blank required field(s): "
                    + ", ".join(missing)
                )
            status = row.get("verification_status")
            if status and status not in allowed_verification_statuses:
                issues.append(
                    f"{filename}: line {line_number} has unsupported verification_status {status!r}"
                )

    entity_ids: dict[str, set[str]] = {}
    for node_type, (filename, id_column, name_column) in _all_entity_files().items():
        identifiers: set[str] = set()
        names: set[str] = set()
        for row in tables.get(filename, []):
            identifier = row[id_column]
            name = row[name_column]
            if not identifier or not name:
                issues.append(f"{filename}: {id_column} and {name_column} are required")
                continue
            if identifier in identifiers:
                issues.append(f"{filename}: duplicate {id_column} {identifier!r}")
            identifiers.add(identifier)
            normalized_name = name.casefold()
            if normalized_name in names:
                issues.append(f"{filename}: duplicate {name_column} {name!r}")
            names.add(normalized_name)
        entity_ids[node_type] = identifiers

    if include_demo:
        for node_type, filename, id_column, name_column in (
            ("student", "students_demo.csv", "student_id", "student_name"),
            ("opportunity", "opportunities_demo.csv", "opportunity_id", "opportunity_name"),
        ):
            identifiers = entity_ids[node_type]
            names: set[str] = set()
            for row in tables.get(filename, []):
                identifier = row[id_column]
                name = row[name_column]
                if identifier in identifiers:
                    issues.append(
                        f"{filename}: duplicate {id_column} {identifier!r}"
                    )
                identifiers.add(identifier)
                normalized_name = name.casefold()
                if normalized_name in names:
                    issues.append(
                        f"{filename}: duplicate {name_column} {name!r}"
                    )
                names.add(normalized_name)

    for filename in tables:
        for row in tables[filename]:
            if "provenance" in row and not row["provenance"]:
                issues.append(f"{filename}: provenance must not be blank")
            if row.get("verification_status") == "independently_verified":
                if not row.get("source_url"):
                    issues.append(f"{filename}: independently verified record lacks source_url")
                if not row.get("source_verified_at"):
                    issues.append(f"{filename}: independently verified record lacks source_verified_at")
            if "source_url" in row:
                _validate_url(row["source_url"], filename, row.get("course_id", row.get(
                    "career_id", row.get("certification_id", row.get("opportunity_id", row.get(
                        "project_id", row.get("skill_id", "record")
                    )))
                )), issues)
            if "source_verified_at" in row:
                record_id = next(
                    (row[key] for key in row if key.endswith("_id") and row[key]),
                    "record",
                )
                _validate_date(
                    row["source_verified_at"], filename, record_id,
                    "source_verified_at", issues,
                )
            if filename in {"opportunities.csv", "opportunities_demo.csv"}:
                _validate_date(
                    row["deadline"], filename, row["opportunity_id"],
                    "deadline", issues,
                )

    for filename, source_column, source_type, target_column, target_type, _ in _all_relation_files(include_demo=include_demo):
        seen: set[tuple[str, str]] = set()
        for row in tables.get(filename, []):
            source_id = row[source_column]
            target_id = row[target_column]
            if not source_id or source_id not in entity_ids[source_type]:
                issues.append(f"{filename}: unknown {source_type} reference {source_id!r}")
            if not target_id or target_id not in entity_ids[target_type]:
                issues.append(f"{filename}: unknown {target_type} reference {target_id!r}")
            pair = (source_id, target_id)
            if pair in seen:
                issues.append(f"{filename}: duplicate mapping {pair!r}")
            seen.add(pair)

    prerequisites: dict[str, list[str]] = defaultdict(list)
    seen_prerequisites: set[tuple[str, str]] = set()
    for row in tables["skill_prerequisites.csv"]:
        skill_id = row["skill_id"]
        prerequisite_id = row["prerequisite_skill_id"]
        if skill_id not in entity_ids["skill"]:
            issues.append(f"skill_prerequisites.csv: unknown skill_id {skill_id!r}")
        if prerequisite_id not in entity_ids["skill"]:
            issues.append(
                f"skill_prerequisites.csv: unknown prerequisite_skill_id {prerequisite_id!r}"
            )
        if skill_id == prerequisite_id:
            issues.append(f"skill_prerequisites.csv: skill {skill_id!r} cannot require itself")
        pair = (prerequisite_id, skill_id)
        if pair in seen_prerequisites:
            issues.append(f"skill_prerequisites.csv: duplicate mapping {pair!r}")
        seen_prerequisites.add(pair)
        prerequisites[skill_id].append(prerequisite_id)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(skill_id: str) -> None:
        if skill_id in visiting:
            issues.append(f"skill_prerequisites.csv: prerequisite cycle includes {skill_id!r}")
            return
        if skill_id in visited:
            return
        visiting.add(skill_id)
        for prerequisite_id in prerequisites.get(skill_id, []):
            visit(prerequisite_id)
        visiting.remove(skill_id)
        visited.add(skill_id)

    for skill_id in entity_ids["skill"]:
        visit(skill_id)

    for spec in _all_relation_files(include_demo=include_demo):
        filename, source_column, source_type = spec[:3]
        if source_type == "career_role":
            mapped = {row[source_column] for row in tables.get(filename, [])}
            for career_id in entity_ids[source_type] - mapped:
                issues.append(f"{filename}: career {career_id!r} has no required skills")
        elif source_type in {"course", "project", "certification"}:
            mapped = {row[source_column] for row in tables.get(filename, [])}
            for entity_id in entity_ids[source_type] - mapped:
                issues.append(f"{filename}: {source_type} {entity_id!r} has no skill mapping")

    if issues:
        raise DataValidationError(issues)
    return tables


class KnowledgeGraph:
    """Validated directed graph with role-gap analysis and resource ranking."""

    def __init__(self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]):
        self.nodes = nodes
        self.edges = edges
        self.nodes_by_id = {node["id"]: node for node in nodes}
        self.nodes_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for node in nodes:
            self.nodes_by_type[node["type"]].append(node)
        for edge in edges:
            self._outgoing[edge["source"]].append(edge)
            self._incoming[edge["target"]].append(edge)
        self._skill_ids_by_name = {
            node["name"].casefold(): node["id"]
            for node in self.nodes_by_type["skill"]
        }
        self._role_ids_by_name = {
            node["name"].casefold(): node["id"]
            for node in self.nodes_by_type["career_role"]
        }

    @classmethod
    def from_seed_dir(cls, seed_dir: Path = SEED_DIR, include_demo: bool = False) -> "KnowledgeGraph":
        tables = load_seed_tables(seed_dir, include_demo=include_demo)
        nodes: list[dict[str, Any]] = []
        seen_nodes: set[tuple[str, str]] = set()
        for node_type, (filename, id_column, name_column) in ENTITY_FILES.items():
            for row in tables.get(filename, []):
                node_key = (row[id_column], node_type)
                if node_key in seen_nodes:
                    continue
                attributes = {
                    key: value for key, value in row.items()
                    if key not in {id_column, name_column} and value != ""
                }
                nodes.append({
                    "id": row[id_column],
                    "name": row[name_column],
                    "type": node_type,
                    **attributes,
                })
                seen_nodes.add(node_key)
        if include_demo:
            for row in tables.get("students_demo.csv", []):
                node_key = (row["student_id"], "student")
                if node_key in seen_nodes:
                    continue
                nodes.append({
                    "id": row["student_id"],
                    "name": row["student_name"],
                    "type": "student",
                    "academic_year": row.get("academic_year", ""),
                    "target_role_id": row.get("target_role_id", ""),
                    "provenance": row.get("provenance", ""),
                    "is_synthetic": row.get("is_synthetic", "false"),
                })
                seen_nodes.add(node_key)
            for row in tables.get("opportunities_demo.csv", []):
                node_key = (row["opportunity_id"], "opportunity")
                if node_key in seen_nodes:
                    continue
                nodes.append({
                    "id": row["opportunity_id"],
                    "name": row["opportunity_name"],
                    "type": "opportunity",
                    "organization": row.get("organization", ""),
                    "opportunity_type": row.get("opportunity_type", ""),
                    "location": row.get("location", ""),
                    "application_url": row.get("application_url", ""),
                    "source_url": row.get("source_url", ""),
                    "deadline": row.get("deadline", ""),
                    "verification_status": row.get("verification_status", ""),
                    "provenance": row.get("provenance", ""),
                    "is_synthetic": row.get("is_synthetic", "false"),
                })
                seen_nodes.add(node_key)

        edges: list[dict[str, Any]] = []
        seen_edges: set[tuple[str, str, str]] = set()
        for spec in _all_relation_files(include_demo=include_demo):
            filename, source_column, target_column, relation = (
                spec[0], spec[1], spec[3], spec[5]
            )
            for row in tables.get(filename, []):
                source_id = row[source_column]
                target_id = row[target_column]
                if relation == "required_for":
                    source_id, target_id = target_id, source_id
                edge_key = (source_id, target_id, relation)
                if edge_key in seen_edges:
                    continue
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "relation": relation,
                    "provenance": row.get("provenance", ""),
                })
                seen_edges.add(edge_key)
        for row in tables.get("skill_prerequisites.csv", []):
            edge_key = (row["prerequisite_skill_id"], row["skill_id"], "prerequisite_for")
            if edge_key in seen_edges:
                continue
            edges.append({
                "source": row["prerequisite_skill_id"],
                "target": row["skill_id"],
                "relation": "prerequisite_for",
                "provenance": row.get("provenance", ""),
            })
            seen_edges.add(edge_key)
        return cls(nodes, edges)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": {
                "project": "SkillBridge",
                "dataset_type": "csv_backed_knowledge_graph",
                "provenance_note": "Curated seed records are not independently verified unless explicitly marked.",
                "geographic_scope_note": (
                    "O*NET occupations and skill ratings are US-focused and are not "
                    "Indian labor-market data."
                ),
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
            },
            "nodes": self.nodes,
            "edges": self.edges,
        }

    def get_node(self, identifier_or_name: str, node_type: str | None = None) -> dict[str, Any] | None:
        if not isinstance(identifier_or_name, str):
            return None
        candidate = identifier_or_name.strip()
        if not candidate:
            return None
        node = self.nodes_by_id.get(candidate)
        if node and (node_type is None or node["type"] == node_type):
            return node
        normalized = candidate.casefold()
        if node_type == "skill":
            resolved_id = self._skill_ids_by_name.get(normalized)
        elif node_type == "career_role":
            resolved_id = self._role_ids_by_name.get(normalized)
        else:
            resolved_id = next(
                (
                    item["id"] for item in self.nodes
                    if item["name"].casefold() == normalized
                    and (node_type is None or item["type"] == node_type)
                ),
                None,
            )
        return self.nodes_by_id.get(resolved_id) if resolved_id else None

    def traverse(
        self,
        start_id: str,
        relations: set[str] | None = None,
        max_depth: int = 1,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        """Return reachable nodes breadth-first, excluding the starting node."""
        if start_id not in self.nodes_by_id:
            raise KeyError(f"Unknown graph node {start_id!r}")
        if max_depth < 1:
            return []
        adjacency = self._incoming if reverse else self._outgoing
        visited = {start_id}
        queue = deque([(start_id, 0)])
        found: list[dict[str, Any]] = []
        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in adjacency[current_id]:
                if relations is not None and edge["relation"] not in relations:
                    continue
                next_id = edge["source"] if reverse else edge["target"]
                if next_id not in visited:
                    visited.add(next_id)
                    found.append(self.nodes_by_id[next_id])
                    queue.append((next_id, depth + 1))
        return found

    def _related_nodes(self, node_id: str, relation: str, outgoing: bool = True) -> list[dict[str, Any]]:
        edges = self._outgoing[node_id] if outgoing else self._incoming[node_id]
        return [
            self.nodes_by_id[edge["target"] if outgoing else edge["source"]]
            for edge in edges if edge["relation"] == relation
        ]

    def _skill_closure(self, target_skill_ids: Iterable[str]) -> list[str]:
        prerequisites: dict[str, list[str]] = defaultdict(list)
        for edge in self.edges:
            if edge["relation"] == "prerequisite_for":
                prerequisites[edge["target"]].append(edge["source"])
        ordered: list[str] = []
        visited: set[str] = set()

        def visit(skill_id: str) -> None:
            if skill_id in visited:
                return
            visited.add(skill_id)
            for prerequisite_id in sorted(
                prerequisites.get(skill_id, []),
                key=lambda item: self.nodes_by_id[item]["name"].casefold(),
            ):
                visit(prerequisite_id)
            ordered.append(skill_id)

        for skill_id in target_skill_ids:
            visit(skill_id)
        return ordered

    def _rank_resources(
        self,
        relation: str,
        missing_skill_ids: set[str],
    ) -> list[dict[str, Any]]:
        ranked = []
        for resource in self.nodes_by_type[
            {
                "teaches": "course",
                "demonstrates": "project",
                "validates": "certification",
                "requires": "opportunity",
            }[relation]
        ]:
            covered = sorted(
                {
                    edge["target"] for edge in self._outgoing[resource["id"]]
                    if edge["relation"] == relation and edge["target"] in missing_skill_ids
                },
                key=lambda item: self.nodes_by_id[item]["name"].casefold(),
            )
            if not covered:
                continue
            ranked.append({
                **resource,
                "addresses_skill_ids": covered,
                "addresses_skills": [self.nodes_by_id[item]["name"] for item in covered],
                "reason": (
                    f"Directly linked to {len(covered)} currently missing "
                    f"skill{'s' if len(covered) != 1 else ''}."
                ),
            })
        ranked.sort(
            key=lambda item: (
                -len(item["addresses_skill_ids"]),
                item["name"].casefold(),
                item["id"],
            )
        )
        return ranked

    def get_student_skills(self, student_id: str) -> list[dict[str, Any]]:
        student = self.get_node(student_id, "student")
        if student is None:
            raise KeyError(f"Unknown student {student_id!r}")
        return self._related_nodes(student["id"], "has_skill", outgoing=True)

    def get_role_skills(self, role_identifier: str) -> list[dict[str, Any]]:
        role = self.get_node(role_identifier, "career_role")
        if role is None:
            raise KeyError(f"Unknown role {role_identifier!r}")
        return self._related_nodes(role["id"], "required_for", outgoing=False)

    def get_courses_for_skill(self, skill_identifier: str) -> list[dict[str, Any]]:
        skill = self.get_node(skill_identifier, "skill")
        if skill is None:
            raise KeyError(f"Unknown skill {skill_identifier!r}")
        return self._related_nodes(skill["id"], "teaches", outgoing=False)

    def shortest_path(
        self,
        start_id: str,
        end_id: str,
        relations: set[str] | None = None,
        reverse: bool = False,
    ) -> list[str]:
        if start_id not in self.nodes_by_id:
            raise KeyError(f"Unknown graph node {start_id!r}")
        if end_id not in self.nodes_by_id:
            raise KeyError(f"Unknown graph node {end_id!r}")
        adjacency = self._incoming if reverse else self._outgoing
        queue: deque[str] = deque([start_id])
        previous: dict[str, str | None] = {start_id: None}
        while queue:
            current = queue.popleft()
            if current == end_id:
                break
            for edge in adjacency[current]:
                if relations is not None and edge["relation"] not in relations:
                    continue
                next_id = edge["source"] if reverse else edge["target"]
                if next_id in previous:
                    continue
                previous[next_id] = current
                queue.append(next_id)
        if end_id not in previous:
            return []
        path: list[str] = []
        current: str | None = end_id
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path

    def create_roadmap(
        self,
        student_name: str,
        existing_skills: Iterable[str],
        target_role: str,
    ) -> dict[str, Any]:
        role = self.get_node(target_role, "career_role")
        if role is None:
            raise KeyError(f"Unknown target role {target_role!r}")

        known_skill_ids: set[str] = set()
        for skill in existing_skills:
            node = self.get_node(skill, "skill")
            if node is None:
                raise ValueError(f"Unknown skill {skill!r}")
            known_skill_ids.add(node["id"])

        required_ids = [
            node["id"] for node in self._related_nodes(role["id"], "required_for", outgoing=False)
        ]
        ordered_required_ids = self._skill_closure(required_ids)
        ordered_gap_ids = [item for item in ordered_required_ids if item not in known_skill_ids]
        required_set = set(required_ids)
        skill_gap = [
            {
                "skill_id": skill_id,
                "skill_name": self.nodes_by_id[skill_id]["name"],
                "is_role_requirement": skill_id in required_set,
                "prerequisite_for": [
                    self.nodes_by_id[item]["name"] for item in required_ids
                    if item != skill_id and skill_id in self._skill_closure([item])[:-1]
                ],
                "reason": (
                    "Required directly by the target role."
                    if skill_id in required_set
                    else "A prerequisite of a skill required by the target role."
                ),
            }
            for skill_id in ordered_gap_ids
        ]
        missing_set = set(ordered_gap_ids)
        recommendations = {
            "courses": self._rank_resources("teaches", missing_set),
            "projects": self._rank_resources("demonstrates", missing_set),
            "certifications": self._rank_resources("validates", missing_set),
            "opportunities": self._rank_resources("requires", missing_set),
        }
        prerequisite_names: dict[str, list[str]] = defaultdict(list)
        for edge in self.edges:
            if edge["relation"] == "prerequisite_for":
                prerequisite_names[edge["target"]].append(
                    self.nodes_by_id[edge["source"]]["name"]
                )
        roadmap_steps = [
            {
                "step": index,
                "skill_id": skill_id,
                "skill_name": self.nodes_by_id[skill_id]["name"],
                "required_before": sorted(
                    prerequisite_names.get(skill_id, []), key=str.casefold
                ),
                "resources": {
                    category: [
                        {
                            "id": item["id"],
                            "name": item["name"],
                            "source_url": item.get("source_url", ""),
                        }
                        for item in recommendations[category]
                        if skill_id in item["addresses_skill_ids"]
                    ]
                    for category in (
                        "courses", "projects", "certifications", "opportunities"
                    )
                },
            }
            for index, skill_id in enumerate(ordered_gap_ids, start=1)
        ]
        direct_missing = [item for item in skill_gap if item["is_role_requirement"]]
        return {
            "student": {
                "name": student_name,
                "existing_skills": [
                    {
                        "skill_id": skill_id,
                        "skill_name": self.nodes_by_id[skill_id]["name"],
                    }
                    for skill_id in sorted(
                        known_skill_ids,
                        key=lambda item: self.nodes_by_id[item]["name"].casefold(),
                    )
                ],
            },
            "target_role": {
                "career_id": role["id"],
                "career_name": role["name"],
                "description": role.get("description", ""),
            },
            "skill_gap": {
                "required_skill_count": len(required_ids),
                "missing_required_skill_count": len(direct_missing),
                "missing_prerequisite_count": len(ordered_gap_ids) - len(direct_missing),
                "missing_skills": skill_gap,
                "already_satisfied_skill_ids": [
                    item for item in ordered_required_ids if item in known_skill_ids
                ],
            },
            "recommendations": recommendations,
            "roadmap": roadmap_steps,
            "algorithm": "prerequisite-closure then deterministic graph-neighbor coverage ranking",
        }


def write_graph(graph: KnowledgeGraph, output_path: Path = GRAPH_FILE) -> None:
    output_path.write_text(
        json.dumps(graph.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_graph(seed_dir: Path = SEED_DIR, include_demo: bool = False) -> KnowledgeGraph:
    return KnowledgeGraph.from_seed_dir(seed_dir, include_demo=include_demo)
