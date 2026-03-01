from enum import Enum


class InterventionState(Enum):

    MONITOR = "MONITOR"
    PREVENTIVE = "PREVENTIVE"
    INTERVENTION = "INTERVENTION"
    CRITICAL = "CRITICAL"