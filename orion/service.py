from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .db import get_flag, init_db, upsert_flag

app = FastAPI(title="Orion Feature Flags")
init_db()


class Flag(BaseModel):
    key: str
    enabled: bool = True
    rules: list[dict] = []  # e.g., [{"if":{"country":"US"},"then":true}]


@app.put("/flags/{key}")
def put_flag(key: str, flag: Flag):
    if key != flag.key:
        raise HTTPException(400, "Key mismatch")
    upsert_flag(key, flag.model_dump())
    return {"ok": True}


class EvalRequest(BaseModel):
    key: str
    context: dict


@app.post("/eval")
def eval_flag(req: EvalRequest):
    flag = get_flag(req.key)
    if not flag:
        return {"value": False, "reason": "missing"}
    value = flag.get("enabled", False)
    for r in flag.get("rules", []):
        cond = r.get("if", {})
        then = r.get("then", value)
        if all(req.context.get(k) == v for k, v in cond.items()):
            value = then
    return {"value": value, "reason": "rule-match"}
