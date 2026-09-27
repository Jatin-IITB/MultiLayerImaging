"""Class schemes: group the stage labels of sims.csv into the classes actually compared."""
from __future__ import annotations

AD_STAGES = {"MCI", "Mild", "Moderate", "Severe"}


def scheme_groups(cfg: dict, scheme: str) -> dict[str, list[str]]:
    return {g: list(stages) for g, stages in cfg["classes"]["schemes"][scheme].items()}


def schemes_to_run(cfg: dict, include_moderate: bool = False) -> list[str]:
    s = list(cfg["classes"]["class_scheme"])
    return s + ["four"] if include_moderate and "four" not in s else s


def scheme_label(cfg: dict, scheme: str) -> str:
    """Value for the metrics.csv `classes` column, e.g. 'binary:Normal|AD(Mild+Moderate+Severe)'."""
    parts = []
    for g, st in scheme_groups(cfg, scheme).items():
        parts.append(g if st == [g] else f"{g}({'+'.join(st)})")
    return f"{scheme}:" + "|".join(parts)


def pair_is_ad_only(groups: dict[str, list[str]], a: str, b: str) -> bool:
    """True if both groups contain only AD stages (needs the mesh-noise caveat)."""
    return set(groups[a]) <= AD_STAGES and set(groups[b]) <= AD_STAGES
