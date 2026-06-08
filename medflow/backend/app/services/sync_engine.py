"""Placeholder for offline sync engine (Conflict-Aware)."""
from __future__ import annotations

from typing import Any


class OfflineSyncEngine:
    """Conflict-Aware offline sync engine.

    Rules:
    - Medical critical fields: present both versions for manual arbitration.
    - Administrative fields: Last Write Wins (timestamp ms).
    """

    MEDICAL_FIELDS = {"pas", "pad", "fc", "spo2", "temperature", "imc", "diagnostic_principal", "ordonnances"}

    @staticmethod
    def resolve(local: dict[str, Any], remote: dict[str, Any]) -> dict[str, Any]:
        """Return merged document with conflict flags for UI arbitration."""
        merged = dict(remote)
        conflicts: list[dict[str, Any]] = []
        for key, local_value in local.items():
            remote_value = remote.get(key)
            if key in OfflineSyncEngine.MEDICAL_FIELDS and local_value != remote_value:
                conflicts.append({"field": key, "local": local_value, "remote": remote_value})
                # Keep remote as default; UI must present arbitration dialog
                continue
            merged[key] = local_value
        merged["__conflicts__"] = conflicts
        return merged
