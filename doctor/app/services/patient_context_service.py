from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class Patient:
    """
    就诊中的病人信息（用于对接医院 HIS/EMR 的抽象层）。
    """

    user_id: str
    user_role: str = "customer"


@runtime_checkable
class IPatientContextService(Protocol):
    """
    对接医院系统的接口：根据医生身份获取“当前就诊病人”。
    """

    async def get_current_patient(self, *, doctor_user_id: str) -> Patient:
        ...


class MockPatientContextService(IPatientContextService):
    """
    Mock：随机返回一个“当前就诊病人”。

    说明：这里先用固定候选集合 + random 的方式占位，后续可以替换为真实 HIS/EMR API。
    """

    _candidate_patient_ids = (
        "customer_0001",
        "customer_0002",
        "customer_0003",
        "customer_0004",
    )

    async def get_current_patient(self, *, doctor_user_id: str) -> Patient:
        patient_id = random.choice(self._candidate_patient_ids)
        return Patient(user_id=patient_id, user_role="customer")


_patient_context_service_singleton: IPatientContextService = MockPatientContextService()


def get_patient_context_service() -> IPatientContextService:
    return _patient_context_service_singleton


__all__ = [
    "Patient",
    "IPatientContextService",
    "MockPatientContextService",
    "get_patient_context_service",
]
