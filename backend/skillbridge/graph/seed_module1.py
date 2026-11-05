"""One-time, reproducible initialization of curated Module 1 relationship seed data."""

from __future__ import annotations

import csv
import hashlib
import os
import re
import shutil
import tempfile
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from graph.knowledge_graph import DATASET_SCHEMAS, SEED_DIR, load_seed_tables


BACKEND_DIR = Path(__file__).resolve().parents[1]
ONET_DIR = BACKEND_DIR / "db_31_0_csv" / "db_31_0_csv"
ONET_DATABASE_URL = "https://www.onetcenter.org/database.html"
OCCUPATION_ALIASES = {
    "Software Developer": ("Software Developers", "exact"),
    "Frontend Developer": ("Web Developers", "related"),
    "Backend Developer": ("Software Developers", "related"),
    "Full Stack Developer": ("Software Developers", "related"),
    "Web Developer": ("Web Developers", "exact"),
    "Mobile App Developer": ("Software Developers", "related"),
    "Android Developer": ("Software Developers", "related"),
    "iOS Developer": ("Software Developers", "related"),
    "Game Developer": ("Software Developers", "related"),
    "Software Test Engineer": (
        "Software Quality Assurance Analysts and Testers", "related",
    ),
    "Automation Test Engineer": (
        "Software Quality Assurance Analysts and Testers", "related",
    ),
    "QA Engineer": (
        "Software Quality Assurance Analysts and Testers", "related",
    ),
    "Business Intelligence Analyst": ("Business Intelligence Analysts", "exact"),
    "Data Scientist": ("Data Scientists", "exact"),
    "Cloud Security Engineer": ("Information Security Engineers", "related"),
    "Cybersecurity Analyst": ("Information Security Analysts", "related"),
    "Security Engineer": ("Information Security Engineers", "related"),
    "Penetration Tester": ("Penetration Testers", "exact"),
    "Application Security Engineer": ("Information Security Engineers", "related"),
    "Digital Forensics Analyst": ("Digital Forensics Analysts", "exact"),
    "Database Administrator": ("Database Administrators", "exact"),
    "Database Developer": ("Database Architects", "related"),
    "Solutions Architect": ("Computer Systems Engineers/Architects", "related"),
    "Systems Architect": ("Computer Systems Engineers/Architects", "related"),
    "Robotics Software Engineer": ("Robotics Engineers", "related"),
    "Blockchain Developer": ("Blockchain Engineers", "related"),
    "Network Security Engineer": ("Information Security Engineers", "related"),
    "IT Support Engineer": ("Computer User Support Specialists", "related"),
    "Research Software Engineer": ("Software Developers", "related"),
}

RATED_SKILL_CATEGORIES = {
    "active listening": "Communication Skills",
    "instructing": "Communication Skills",
    "negotiation": "Communication Skills",
    "persuasion": "Communication Skills",
    "reading comprehension": "Communication Skills",
    "speaking": "Communication Skills",
    "writing": "Communication Skills",
    "active learning": "Cognitive Skills",
    "complex problem solving": "Cognitive Skills",
    "critical thinking": "Cognitive Skills",
    "judgment and decision making": "Cognitive Skills",
    "learning strategies": "Cognitive Skills",
    "mathematics": "Cognitive Skills",
    "monitoring": "Cognitive Skills",
    "operations analysis": "Cognitive Skills",
    "science": "Cognitive Skills",
    "systems analysis": "Cognitive Skills",
    "systems evaluation": "Cognitive Skills",
    "coordination": "Interpersonal Skills",
    "service orientation": "Interpersonal Skills",
    "social perceptiveness": "Interpersonal Skills",
    "management of financial resources": "Management Skills",
    "management of material resources": "Management Skills",
    "management of personnel resources": "Management Skills",
    "equipment maintenance": "Technical Skills",
    "equipment selection": "Technical Skills",
    "installation": "Technical Skills",
    "operation and control": "Technical Skills",
    "operations monitoring": "Technical Skills",
    "programming": "Technical Skills",
    "quality control analysis": "Technical Skills",
    "repairing": "Technical Skills",
    "technology design": "Technical Skills",
    "troubleshooting": "Technical Skills",
}

ROLE_SKILLS = {
    "Software Developer": ["Python", "Data Structures and Algorithms", "Software Engineering", "Software Testing", "Object Oriented Programming"],
    "Frontend Developer": ["JavaScript", "HTML", "CSS", "React", "Responsive Web Design", "Accessibility"],
    "Backend Developer": ["Python", "SQL", "REST APIs", "Database Design", "Authentication and Authorization"],
    "Full Stack Developer": ["JavaScript", "HTML", "CSS", "React", "Node.js", "SQL"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Responsive Web Design", "Accessibility"],
    "Mobile App Developer": ["Java", "Kotlin", "REST APIs", "Git"],
    "Android Developer": ["Java", "Kotlin", "REST APIs"],
    "iOS Developer": ["Swift", "UI UX Design", "REST APIs"],
    "Game Developer": ["C++ Programming", "C#", "Data Structures and Algorithms", "Object Oriented Programming"],
    "Software Test Engineer": ["Software Testing", "Unit Testing", "Debugging"],
    "Automation Test Engineer": ["Python", "Software Testing", "Unit Testing", "API Testing"],
    "QA Engineer": ["Software Testing", "API Testing", "Agile and Scrum"],
    "Data Analyst": ["SQL", "Data Analysis", "Microsoft Excel", "Power BI", "Statistics"],
    "Business Intelligence Analyst": ["SQL", "Power BI", "Tableau", "Data Warehousing"],
    "Data Scientist": ["Python", "Statistics", "Pandas", "NumPy", "Machine Learning", "Data Analysis"],
    "Data Engineer": ["Python", "SQL", "ETL", "Apache Spark", "Data Warehousing"],
    "Big Data Engineer": ["Apache Spark", "Apache Kafka", "Data Warehousing", "SQL"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Scikit-learn", "Statistics", "Model Evaluation", "Model Deployment"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "Large Language Models", "REST APIs"],
    "Deep Learning Engineer": ["Python", "Deep Learning", "PyTorch", "Linear Algebra", "Model Deployment"],
    "NLP Engineer": ["Python", "Natural Language Processing", "Deep Learning", "Large Language Models", "RAG"],
    "Computer Vision Engineer": ["Python", "Computer Vision", "Deep Learning", "PyTorch", "NumPy"],
    "Generative AI Engineer": ["Python", "Generative AI", "Large Language Models", "Prompt Engineering", "RAG"],
    "AI Research Engineer": ["Python", "Linear Algebra", "Statistics", "Machine Learning", "Deep Learning"],
    "Recommendation Systems Engineer": ["Python", "Recommendation Systems", "Machine Learning", "Statistics"],
    "Cloud Engineer": ["AWS", "Linux", "Docker", "Kubernetes", "Computer Networks"],
    "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "CI CD", "Bash Scripting", "Infrastructure as Code"],
    "Site Reliability Engineer": ["Linux", "Docker", "Kubernetes", "System Design", "Computer Networks"],
    "Platform Engineer": ["Linux", "Docker", "Kubernetes", "Infrastructure as Code", "CI CD"],
    "Cloud Security Engineer": ["AWS", "Linux", "Cybersecurity Fundamentals", "Web Application Security", "Network Security"],
    "Cybersecurity Analyst": ["Cybersecurity Fundamentals", "Network Security", "Linux", "Security Auditing", "Web Application Security"],
    "Security Engineer": ["Cybersecurity Fundamentals", "Web Application Security", "OAuth 2.0", "Cryptography"],
    "Penetration Tester": ["Cybersecurity Fundamentals", "Web Application Security", "Ethical Hacking", "Penetration Testing"],
    "Application Security Engineer": ["Web Application Security", "OAuth 2.0", "Software Testing", "Cryptography"],
    "Digital Forensics Analyst": ["Linux", "Computer Networks", "Cybersecurity Fundamentals", "Security Auditing"],
    "Database Administrator": ["SQL", "Database Design", "Database Indexing", "Database Transactions", "PostgreSQL"],
    "Database Developer": ["SQL", "Database Design", "PostgreSQL", "ORM"],
    "Solutions Architect": ["System Design", "Software Architecture", "AWS", "Microservices"],
    "Systems Architect": ["System Design", "Software Architecture", "Operating Systems", "Computer Networks", "Distributed Systems"],
    "Embedded Software Engineer": ["C Programming", "C++ Programming", "Operating Systems", "Computer Networks"],
    "IoT Software Engineer": ["C Programming", "C++ Programming", "Computer Networks", "AWS"],
    "Robotics Software Engineer": ["C++ Programming", "Python", "Linear Algebra", "Data Structures and Algorithms"],
    "Blockchain Developer": ["C++ Programming", "Cryptography", "Web Application Security", "Database Transactions"],
    "AR VR Developer": ["C#", "AR/VR Development", "Linear Algebra", "UI UX Design"],
    "Network Engineer": ["Computer Networks", "Linux", "Network Security"],
    "Network Security Engineer": ["Computer Networks", "Network Security", "Cryptography", "Cybersecurity Fundamentals"],
    "IT Support Engineer": ["Operating Systems", "Linux", "Computer Networks", "Cybersecurity Fundamentals"],
    "Technical Consultant": ["Software Engineering", "System Design", "Agile and Scrum"],
    "Research Software Engineer": ["Python", "Software Engineering", "Data Structures and Algorithms", "Statistics"],
    "MLOps Engineer": ["Python", "Model Deployment", "Docker", "Kubernetes", "MLflow", "CI CD"],
}

COURSES = [
    ["course-cs50x", "CS50's Introduction to Computer Science", "Harvard University",
     "Harvard's introductory computer science course covering C, algorithms, data structures, Python, SQL, and web development.",
     "https://cs50.harvard.edu/x/", "authoritative_source", "independently_verified", "2026-10-16"],
    ["course-full-stack-open", "Full Stack Open", "University of Helsinki",
     "Open course in modern web development with React, Node.js, REST APIs, testing, and related technologies.",
     "https://fullstackopen.com/en/", "authoritative_source", "independently_verified", "2026-10-16"],
    ["course-machine-learning-specialization", "Machine Learning Specialization", "DeepLearning.AI and Stanford Online",
     "Three-course introduction to supervised and unsupervised learning, recommender systems, and model evaluation.",
     "https://www.coursera.org/specializations/machine-learning-introduction",
     "authoritative_source", "independently_verified", "2026-10-16"],
    ["course-react-quick-start", "React Learn: Quick Start", "React documentation",
     "Official React documentation introducing components, UI, events, and state.",
     "https://react.dev/learn", "authoritative_source", "independently_verified", "2026-10-16"],
]

COURSE_SKILLS = {
    "course-cs50x": ["C Programming", "Data Structures and Algorithms", "Python", "SQL"],
    "course-full-stack-open": ["React", "Node.js", "REST APIs", "Software Testing"],
    "course-machine-learning-specialization": ["Machine Learning", "Statistics", "Python", "Model Evaluation"],
    "course-react-quick-start": ["React"],
}

PROJECTS = [
    ["project-data-analysis-dashboard", "Data Analysis Dashboard",
     "Build a small dashboard that cleans a public dataset, documents analysis choices, and presents findings.",
     "", "curated_seed", "unverified"],
    ["project-accessible-portfolio", "Accessible Portfolio Website",
     "Create a responsive portfolio with semantic HTML, CSS, keyboard navigation, and accessible interaction.",
     "", "curated_seed", "unverified"],
    ["project-recommendation-engine", "Learning Resource Recommendation Prototype",
     "Build a small content-based recommender and explain how its feature and ranking choices work.",
     "", "curated_seed", "unverified"],
    ["project-containerized-api", "Containerized REST API",
     "Implement a documented API, add tests, and package it as a reproducible Docker deployment.",
     "", "curated_seed", "unverified"],
    ["project-knowledge-graph-roadmap", "Knowledge Graph Learning Roadmap",
     "Represent skills and prerequisites as a graph, validate links, and generate an ordered learning path.",
     "", "curated_seed", "unverified"],
]

PROJECT_SKILLS = {
    "project-data-analysis-dashboard": ["Python", "Data Cleaning", "Data Analysis", "Power BI"],
    "project-accessible-portfolio": ["HTML", "CSS", "JavaScript", "Responsive Web Design", "Accessibility"],
    "project-recommendation-engine": ["Python", "Machine Learning", "Recommendation Systems", "Statistics"],
    "project-containerized-api": ["Python", "REST APIs", "Docker", "Software Testing"],
    "project-knowledge-graph-roadmap": ["Python", "Knowledge Graphs", "Graph Algorithms", "Data Structures and Algorithms"],
}

CERTIFICATIONS = [
    ["cert-aws-cloud-practitioner", "AWS Certified Cloud Practitioner", "Amazon Web Services",
     "Foundational AWS cloud credential; review the current exam guide and requirements on the official certification page.",
     "https://aws.amazon.com/certification/certified-cloud-practitioner/",
     "authoritative_source", "independently_verified", "2026-10-16"],
    ["cert-azure-fundamentals", "Microsoft Certified: Azure Fundamentals", "Microsoft",
     "Foundational credential covering cloud concepts, core Azure services, and Azure management and governance.",
     "https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/",
     "authoritative_source", "independently_verified", "2026-10-16"],
]

PREREQUISITES = [
    ("Machine Learning", "Python"), ("Machine Learning", "Statistics"),
    ("Deep Learning", "Machine Learning"), ("Deep Learning", "Linear Algebra"),
    ("Natural Language Processing", "Python"),
    ("Natural Language Processing", "Machine Learning"),
    ("Computer Vision", "Python"), ("Computer Vision", "Deep Learning"),
    ("React", "JavaScript"), ("React", "HTML"), ("React", "CSS"),
    ("Node.js", "JavaScript"), ("Django", "Python"),
    ("Kubernetes", "Docker"), ("Kubernetes", "Linux"),
    ("RAG", "Large Language Models"), ("RAG", "Python"),
    ("System Design", "Data Structures and Algorithms"),
]


def _write_csv(filename: str, header: list[str], rows: list[list[str]]) -> None:
    with (SEED_DIR / filename).open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(header)
        writer.writerows(rows)


def _read_csv(filename: str) -> tuple[list[str], list[dict[str, str]]]:
    with (SEED_DIR / filename).open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), list(reader)


def _read_source_csv(path: Path, expected_header: tuple[str, ...]) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            if tuple(reader.fieldnames or ()) != expected_header:
                raise ValueError(
                    f"{path}: expected CSV header {expected_header}, "
                    f"found {tuple(reader.fieldnames or ())}"
                )
            return [
                {key: (value or "").strip() for key, value in row.items()}
                for row in reader
            ]
    except (OSError, UnicodeError, csv.Error) as error:
        raise ValueError(f"Cannot read O*NET source file {path}: {error}") from error


def _merge_provenance(existing: str, additions: list[str]) -> str:
    tokens = [token.strip() for token in existing.split(";") if token.strip()]
    for token in additions:
        if token not in tokens:
            tokens.append(token)
    return "; ".join(tokens)


def _stable_onet_skill_id(skill_name: str, existing_ids: set[str]) -> str:
    normalized = skill_name.casefold()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    candidate = f"skill-onet-{slug}"
    if candidate not in existing_ids:
        return candidate
    suffix = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:10]
    return f"{candidate}-{suffix}"


def _write_rows(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=header, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _backup_path(path: Path) -> Path:
    while True:
        backup = path.with_name(f"{path.name}.backup-{uuid.uuid4().hex}")
        if not backup.exists():
            return backup


def integrate_onet_data(
    seed_dir: Path = SEED_DIR,
    onet_dir: Path = ONET_DIR,
) -> dict[str, Any]:
    """Merge traceable O*NET records into existing Module 1 CSVs without replacing data."""
    occupation_header = ("O*NET-SOC Code", "Title", "Description")
    rated_skill_header = (
        "O*NET-SOC Code", "Title", "Element ID", "Element Name", "Scale ID",
        "Scale Name", "Data Value", "N", "Standard Error", "Lower CI Bound",
        "Upper CI Bound", "Recommend Suppress", "Not Relevant", "Date",
        "Domain Source",
    )
    software_skill_header = (
        "O*NET-SOC Code", "Title", "Workplace Example", "Element ID",
        "Element Name", "Hot Technology", "In Demand",
    )
    occupations = _read_source_csv(onet_dir / "occupation_data.csv", occupation_header)
    titles_by_name = {row["Title"].casefold(): row for row in occupations}

    careers_path = seed_dir / "careers.csv"
    skills_path = seed_dir / "skills.csv"
    relationships_path = seed_dir / "career_skills.csv"
    career_header, careers = _read_seed_csv(careers_path)
    skill_header, skills = _read_seed_csv(skills_path)
    relationship_header, relationships = _read_seed_csv(relationships_path)
    if tuple(career_header) != DATASET_SCHEMAS["careers.csv"]:
        raise ValueError(f"{careers_path}: unexpected careers.csv header")
    if tuple(skill_header) != DATASET_SCHEMAS["skills.csv"]:
        raise ValueError(f"{skills_path}: unexpected skills.csv header")
    if tuple(relationship_header) != DATASET_SCHEMAS["career_skills.csv"]:
        raise ValueError(f"{relationships_path}: unexpected career_skills.csv header")

    careers_by_code: dict[str, list[str]] = defaultdict(list)
    career_match_types: dict[str, str] = {}
    unmatched_career_names = []
    career_mappings_removed = 0
    for career in careers:
        mapping = OCCUPATION_ALIASES.get(career["career_name"])
        if mapping is None:
            unmatched_career_names.append(career["career_name"])
            retained_provenance = [
                token.strip()
                for token in career["provenance"].split(";")
                if token.strip()
                and not token.strip().startswith("onet_database_31.0 occupation=")
            ]
            if len(retained_provenance) != len([
                token for token in career["provenance"].split(";") if token.strip()
            ]):
                career["provenance"] = "; ".join(retained_provenance)
                if career["source_url"].startswith(
                    "https://www.onetonline.org/link/summary/"
                ):
                    career["source_url"] = ""
                    career["verification_status"] = "unverified"
                    career["source_verified_at"] = ""
                career_mappings_removed += 1
            continue
        occupation_title, match_type = mapping
        occupation = titles_by_name.get(occupation_title.casefold())
        if occupation is None:
            raise ValueError(
                f"O*NET occupation title {occupation_title!r} is missing for "
                f"career {career['career_name']!r}"
            )
        code = occupation["O*NET-SOC Code"]
        careers_by_code[code].append(career["career_id"])
        career_match_types[career["career_id"]] = match_type
        occupation_token = (
            f"onet_database_31.0 occupation={code} "
            f"match={match_type} title={occupation['Title']}"
        )
        retained_provenance = [
            token.strip()
            for token in career["provenance"].split(";")
            if token.strip()
            and not token.strip().startswith("onet_database_31.0 occupation=")
        ]
        career["provenance"] = _merge_provenance(
            "; ".join(retained_provenance), [occupation_token]
        )
        career["source_url"] = f"https://www.onetonline.org/link/summary/{code}"
        career["verification_status"] = "unverified"
        career["source_verified_at"] = ""
        if match_type == "exact":
            career["description"] = occupation["Description"]

    skill_ids_by_name = {row["skill_name"].casefold(): row["skill_id"] for row in skills}
    skill_rows_by_id = {row["skill_id"]: row for row in skills}
    existing_skill_names = set(skill_ids_by_name)
    reused_skill_names: set[str] = set()
    existing_skill_ids = {row["skill_id"] for row in skills}
    link_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    skill_descriptions: dict[str, dict[str, str]] = {}
    skill_rows_skipped = 0
    software_rows_skipped = 0

    def add_source_skill(
        career_id: str,
        skill_name: str,
        category: str,
        proficiency: str,
        description: str,
        provenance: str,
    ) -> None:
        normalized_name = skill_name.casefold()
        skill_id = skill_ids_by_name.get(normalized_name)
        if skill_id is None:
            skill_id = _stable_onet_skill_id(skill_name, existing_skill_ids)
            existing_skill_ids.add(skill_id)
            skill_ids_by_name[normalized_name] = skill_id
            skill_descriptions[normalized_name] = {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "category": category,
                "proficiency": proficiency,
                "description": description,
                "provenance": "onet_database_31.0",
                "source_url": ONET_DATABASE_URL,
                "verification_status": "unverified",
            }
        else:
            existing_row = skill_rows_by_id.get(skill_id)
            if existing_row and "onet_database_31.0" in existing_row.get("provenance", ""):
                existing_row["verification_status"] = "unverified"
                existing_row["category"] = category
                existing_row["description"] = description
                if not existing_row.get("source_url"):
                    existing_row["source_url"] = ONET_DATABASE_URL
            if normalized_name in existing_skill_names:
                reused_skill_names.add(normalized_name)
        link_sources[(career_id, skill_id)].add(provenance)

    def consume_rated_skills(filename: str) -> None:
        nonlocal skill_rows_skipped
        records: dict[tuple[str, str], dict[str, str]] = {}
        for row in _read_source_csv(onet_dir / filename, rated_skill_header):
            code = row["O*NET-SOC Code"]
            if code not in careers_by_code:
                continue
            if row["Scale ID"] in {"IM", "LV"}:
                records.setdefault((code, row["Element ID"]), {})[row["Scale ID"]] = row
        for (code, _), scales in records.items():
            importance_row = scales.get("IM")
            if importance_row is None:
                continue
            if (
                importance_row["Recommend Suppress"].upper() == "Y"
                or importance_row["Not Relevant"].upper() == "Y"
            ):
                skill_rows_skipped += len(careers_by_code[code])
                continue
            try:
                importance = float(importance_row["Data Value"])
            except ValueError as error:
                raise ValueError(
                    f"{filename}: invalid importance rating "
                    f"{importance_row['Data Value']!r} for {code}/{importance_row['Element ID']}"
                ) from error
            if importance < 3.0:
                skill_rows_skipped += len(careers_by_code[code])
                continue
            level_row = scales.get("LV")
            level = ""
            if level_row and (
                level_row["Recommend Suppress"].upper() != "Y"
                and level_row["Not Relevant"].upper() != "Y"
            ):
                level = level_row["Data Value"]
            skill_name = importance_row["Element Name"]
            source_category = RATED_SKILL_CATEGORIES.get(
                importance_row["Element Name"].casefold(),
                "Other Skills",
            )
            description = "O*NET occupation skill."
            for career_id in careers_by_code[code]:
                provenance = (
                    f"onet_database_31.0 {filename.removesuffix('.csv')} "
                    f"soc={code} element={importance_row['Element ID']} "
                    f"mapping={career_match_types[career_id]} "
                    f"importance_IM={importance_row['Data Value']} "
                    f"level_LV={level or 'not-reported'} "
                    f"record_date={importance_row['Date']} "
                    f"source=https://www.onetonline.org/link/summary/{code}"
                )
                add_source_skill(
                    career_id, skill_name, source_category,
                    "Not specified by source", description, provenance,
                )

    consume_rated_skills("essential_skills.csv")
    consume_rated_skills("transferable_skills.csv")
    for row in _read_source_csv(onet_dir / "software_skills.csv", software_skill_header):
        code = row["O*NET-SOC Code"]
        if code not in careers_by_code:
            continue
        if row["Hot Technology"].upper() != "Y" and row["In Demand"].upper() != "Y":
            software_rows_skipped += len(careers_by_code[code])
            continue
        technology = row["Workplace Example"]
        if not technology:
            software_rows_skipped += len(careers_by_code[code])
            continue
        detail = "O*NET software technology workplace example."
        for career_id in careers_by_code[code]:
            provenance = (
                f"onet_database_31.0 software_skills soc={code} "
                f"mapping={career_match_types[career_id]} "
                f"element={row['Element ID']} element_name={row['Element Name']} "
                f"hot={row['Hot Technology'] or 'N'} "
                f"in_demand={row['In Demand'] or 'N'} "
                f"source=https://www.onetonline.org/link/summary/{code}"
            )
            add_source_skill(
                career_id, technology, "Software Technology",
                "Not specified by source", detail, provenance,
            )

    new_skills = list(skill_descriptions.values())
    skills.extend(new_skills)
    retained_relationships = []
    career_skill_links_removed = 0
    for row in relationships:
        pair = (row["career_id"], row["skill_id"])
        tokens = [token.strip() for token in row["provenance"].split(";") if token.strip()]
        retained_tokens = [
            token for token in tokens
            if not token.startswith("onet_database_31.0 ")
        ]
        row["provenance"] = "; ".join(retained_tokens)
        if not retained_tokens and pair not in link_sources:
            career_skill_links_removed += 1
            continue
        retained_relationships.append(row)
    relationships = retained_relationships
    relationships_by_pair = {
        (row["career_id"], row["skill_id"]): row for row in relationships
    }
    new_relationships = 0
    reused_relationships = 0
    for (career_id, skill_id), sources in sorted(link_sources.items()):
        pair = (career_id, skill_id)
        existing = relationships_by_pair.get(pair)
        if existing is None:
            relationships.append({
                "career_id": career_id,
                "skill_id": skill_id,
                "provenance": "; ".join(sorted(sources)),
            })
            relationships_by_pair[pair] = relationships[-1]
            new_relationships += 1
        else:
            merged = _merge_provenance(existing["provenance"], sorted(sources))
            if merged != existing["provenance"]:
                existing["provenance"] = merged
                reused_relationships += 1

    changed_tables = {
        "careers.csv": (career_header, careers),
        "skills.csv": (skill_header, skills),
        "career_skills.csv": (relationship_header, relationships),
    }
    changed_tables = {
        filename: table for filename, table in changed_tables.items()
        if table[1] != _read_seed_csv(seed_dir / filename)[1]
    }

    backups: dict[str, Path] = {}
    if changed_tables:
        with tempfile.TemporaryDirectory(dir=seed_dir, prefix=".onet-stage-") as staging:
            staging_dir = Path(staging)
            for filename in DATASET_SCHEMAS:
                shutil.copy2(seed_dir / filename, staging_dir / filename)
            for filename, (header, rows) in changed_tables.items():
                _write_rows(staging_dir / filename, header, rows)
            load_seed_tables(staging_dir)
            for filename in changed_tables:
                source_path = seed_dir / filename
                backup = _backup_path(source_path)
                shutil.copy2(source_path, backup)
                backups[filename] = backup
            committed: list[str] = []
            try:
                for filename in changed_tables:
                    os.replace(staging_dir / filename, seed_dir / filename)
                    committed.append(filename)
            except OSError:
                for filename in committed:
                    shutil.copy2(backups[filename], seed_dir / filename)
                raise

    return {
        "careers_matched": sum(len(ids) for ids in careers_by_code.values()),
        "careers_unmatched": len(unmatched_career_names),
        "unmatched_career_names": sorted(unmatched_career_names, key=str.casefold),
        "career_mappings_removed": career_mappings_removed,
        "skills_added": len(new_skills),
        "skills_reused": len(reused_skill_names),
        "skill_source_rows_skipped": skill_rows_skipped,
        "software_source_rows_skipped": software_rows_skipped,
        "career_skill_links_added": new_relationships,
        "career_skill_links_removed": career_skill_links_removed,
        "career_skill_links_reused": reused_relationships,
        "backup_files": [str(path) for path in backups.values()],
    }


def _read_seed_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            if not reader.fieldnames:
                raise ValueError(f"{path}: missing CSV header")
            rows = [
                {key: (value or "").strip() for key, value in row.items()}
                for row in reader
            ]
            return list(reader.fieldnames), rows
    except (OSError, UnicodeError, csv.Error) as error:
        raise ValueError(f"Cannot read seed CSV {path}: {error}") from error


def _ensure_deep_learning() -> None:
    header, rows = _read_csv("skills.csv")
    if any(row["skill_name"] == "Deep Learning" for row in rows):
        return
    rows.append({
        "skill_id": "skill-deep-learning",
        "skill_name": "Deep Learning",
        "category": "AI and Data Science",
        "proficiency": "Advanced",
        "description": "Machine-learning methods based on multi-layer neural networks.",
        "provenance": "curated_seed",
        "source_url": "",
        "verification_status": "unverified",
    })
    _write_csv("skills.csv", header, [[row[column] for column in header] for row in rows])


def seed_module1() -> None:
    _ensure_deep_learning()
    _, careers = _read_csv("careers.csv")
    _, skills = _read_csv("skills.csv")
    career_ids = {row["career_name"]: row["career_id"] for row in careers}
    skill_ids = {row["skill_name"]: row["skill_id"] for row in skills}
    if set(career_ids) != set(ROLE_SKILLS):
        raise ValueError("The curated career-skill map does not match careers.csv")
    unknown = {
        name for names in ROLE_SKILLS.values() for name in names
        if name not in skill_ids
    }
    unknown.update(
        name for pairs in PREREQUISITES for name in pairs if name not in skill_ids
    )
    unknown.update(
        name for names in COURSE_SKILLS.values() for name in names
        if name not in skill_ids
    )
    unknown.update(
        name for names in PROJECT_SKILLS.values() for name in names
        if name not in skill_ids
    )
    if unknown:
        raise ValueError(f"Skill mappings refer to undefined skills: {sorted(unknown)}")

    _write_csv("career_skills.csv", ["career_id", "skill_id", "provenance"], [
        [career_ids[role], skill_ids[skill], "curated_seed"]
        for role, names in ROLE_SKILLS.items() for skill in names
    ])
    _write_csv(
        "courses.csv",
        ["course_id", "course_name", "provider", "description", "source_url",
         "provenance", "verification_status", "source_verified_at"],
        COURSES,
    )
    _write_csv("course_skills.csv", ["course_id", "skill_id", "provenance"], [
        [course_id, skill_ids[skill], "curated_seed"]
        for course_id, names in COURSE_SKILLS.items() for skill in names
    ])
    _write_csv(
        "projects.csv",
        ["project_id", "project_name", "description", "source_url",
         "provenance", "verification_status"],
        PROJECTS,
    )
    _write_csv("project_skills.csv", ["project_id", "skill_id", "provenance"], [
        [project_id, skill_ids[skill], "curated_seed"]
        for project_id, names in PROJECT_SKILLS.items() for skill in names
    ])
    _write_csv(
        "certifications.csv",
        ["certification_id", "certification_name", "provider", "description",
         "source_url", "provenance", "verification_status", "source_verified_at"],
        CERTIFICATIONS,
    )
    _write_csv("certification_skills.csv", [
        "certification_id", "skill_id", "provenance",
    ], [
        ["cert-aws-cloud-practitioner", skill_ids["AWS"], "curated_seed"],
        ["cert-azure-fundamentals", skill_ids["Microsoft Azure"], "curated_seed"],
    ])
    _write_csv("skill_prerequisites.csv", [
        "skill_id", "prerequisite_skill_id", "provenance",
    ], [
        [skill_ids[target], skill_ids[prerequisite], "curated_seed"]
        for target, prerequisite in PREREQUISITES
    ])
    _write_csv("opportunities.csv", [
        "opportunity_id", "opportunity_name", "provider", "description",
        "source_url", "eligibility_criteria", "deadline", "source_verified_at",
        "provenance", "verification_status",
    ], [])
    _write_csv("opportunity_skills.csv", [
        "opportunity_id", "skill_id", "provenance",
    ], [])
    _write_csv("students.csv", ["student_id", "student_name", "provenance"], [])
    _write_csv("student_skills.csv", ["student_id", "skill_id", "provenance"], [])
    print(f"Initialized Module 1 CSV seeds: {len(careers)} careers, {len(skills)} skills.")


if __name__ == "__main__":
    import json
    import sys

    if sys.argv[1:] == ["--integrate-onet"]:
        print(json.dumps(integrate_onet_data(), indent=2))
    elif not sys.argv[1:]:
        seed_module1()
    else:
        raise SystemExit("Usage: python -m graph.seed_module1 [--integrate-onet]")
