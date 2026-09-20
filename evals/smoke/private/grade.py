#!/usr/bin/env python3
"""Private outcome graders. Do not include this file in a model's task input."""
from __future__ import annotations

import ast
import builtins
from contextlib import closing
import copy
import json
from pathlib import Path
import sqlite3
import sys


def limited_function(source: str, name: str):
    tree = ast.parse(source, filename="solution.py")
    forbidden = (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.ClassDef,
                 ast.With, ast.AsyncWith, ast.AsyncFunctionDef, ast.Await,
                 ast.Yield, ast.YieldFrom)
    for node in ast.walk(tree):
        if isinstance(node, forbidden):
            raise ValueError("artifact uses syntax outside the no-import task contract")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise ValueError("private attributes are outside the task contract")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("private names are outside the task contract")
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            raise ValueError("decorators are outside the task contract")
    names = ("dict list tuple set len range enumerate zip sorted min max sum str int "
             "float bool isinstance all any Exception TimeoutError RuntimeError "
             "ValueError KeyError").split()
    namespace = {"__builtins__": {key: getattr(builtins, key) for key in names}}
    exec(compile(tree, "solution.py", "exec"), namespace)
    function = namespace.get(name)
    if not callable(function):
        raise ValueError(f"artifact must define {name}")
    return function


def sql_cases(source: str):
    datasets = [
        {
            "customers": [(7, "Same"), (19, "Same"), (23, "Empty"), (88, "Other")],
            "orders": [(10, 7, "paid"), (11, 7, "paid"), (12, 7, "open"),
                       (13, 19, "paid"), (14, 88, "cancelled")],
            "order_items": [(1, 10, 3, 120), (2, 10, 2, 15), (3, 12, 8, 900),
                            (4, 13, 0, 300), (5, 13, 4, 25), (6, 14, 10, 70)],
        },
        {"customers": [(101, "A"), (105, "A")], "orders": [], "order_items": []},
    ]
    for index, data in enumerate(datasets):
        def check(data=data):
            with closing(sqlite3.connect(":memory:", isolation_level=None)) as database:
                database.executescript(
                    "CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL);"
                    "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, status TEXT NOT NULL);"
                    "CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, quantity INTEGER NOT NULL, unit_price_cents INTEGER NOT NULL);"
                )
                for table, rows in data.items():
                    columns = {"customers": 2, "orders": 3, "order_items": 4}[table]
                    database.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in range(columns))})", rows)
                allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                           sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
                database.set_authorizer(lambda action, *unused:
                                        sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
                steps = [0]
                def limit():
                    steps[0] += 1
                    return int(steps[0] > 1000)
                database.set_progress_handler(limit, 1000)
                cursor = database.execute(source)
                assert [column[0] for column in cursor.description] == [
                    "customer_id", "paid_order_count", "revenue_cents"], "wrong output columns"
                actual = cursor.fetchmany(len(data["customers"]) + 1)
                expected = []
                for customer, unused_name in sorted(data["customers"]):
                    paid = {order for order, owner, status in data["orders"]
                            if owner == customer and status == "paid"}
                    revenue = sum(quantity * price for unused_id, order, quantity, price
                                  in data["order_items"] if order in paid)
                    expected.append((customer, len(paid), revenue))
                assert actual == expected, "customer grain, zero rows, order count or revenue differs"
        yield f"dataset-{index + 1}", check


def pipeline_cases(source: str):
    events = [
        {"sequence": 2, "id": "evt-z", "value": {"cents": 80}},
        {"sequence": 5, "id": "evt-a", "value": {"cents": 210}},
        {"sequence": 9, "id": "evt-q", "value": {"cents": 0}},
    ]
    faults = [(f"{operation}-{event['sequence']}-{boundary}",
               [(operation, event["sequence"], boundary)])
              for event in events for operation in ("put", "save")
              for boundary in ("before", "after")]
    faults += [("success", []), ("multiple-restarts", [
        ("put", 2, "after"), ("save", 2, "before"),
        ("save", 5, "after"), ("put", 9, "before")])]

    def check_case(fault_plan, feed=events, starting=0):
        function = limited_function(source, "sync")
        pending = list(fault_plan)
        ledger = {event["id"]: copy.deepcopy(event["value"])
                  for event in feed if event["sequence"] <= starting}
        durable = [starting]
        calls = [0]
        def fail(operation, sequence, boundary):
            if pending and pending[0] == (operation, sequence, boundary):
                pending.pop(0)
                raise TimeoutError("injected ambiguous write")
        class Sink:
            def put(self, event_id, value):
                calls[0] += 1
                event = next((event for event in feed if event["id"] == event_id), None)
                assert event is not None and event["value"] == value, "sink ID/value changed"
                fail("put", event["sequence"], "before")
                ledger[event_id] = copy.deepcopy(value)
                fail("put", event["sequence"], "after")
        class Checkpoints:
            def load(self):
                return durable[0]
            def save(self, sequence):
                calls[0] += 1
                assert sequence in [event["sequence"] for event in feed], "invalid checkpoint"
                assert sequence >= durable[0], "checkpoint moved backwards"
                assert all(ledger.get(event["id"]) == event["value"]
                           for event in feed if event["sequence"] <= sequence), "acknowledged missing data"
                fail("save", sequence, "before")
                durable[0] = sequence
                fail("save", sequence, "after")
        sink, checkpoints = Sink(), Checkpoints()
        for attempt in range(len(fault_plan) + 2):
            supplied = copy.deepcopy(feed)
            try:
                result = function(supplied, sink, checkpoints)
            except TimeoutError:
                assert supplied == feed, "input mutated during crash"
                continue
            assert supplied == feed, "input mutated"
            assert result is None, "sync must return None"
            break
        else:
            raise AssertionError("recovery did not complete")
        assert ledger == {event["id"]: event["value"] for event in feed}, "lost or extra records"
        assert durable[0] == (feed[-1]["sequence"] if feed else starting), "wrong final checkpoint"
        previous_calls = calls[0]
        assert function(copy.deepcopy(feed), sink, checkpoints) is None
        assert calls[0] == previous_calls, "fully acknowledged feed was written again"
        # Intermediate checkpoints are optional. A valid implementation may save
        # only the final sequence, so report which proposed faults were reached.
        return {"injected_faults": len(fault_plan) - len(pending),
                "unreached_faults": len(pending)}

    for label, fault_plan in faults:
        yield label, lambda fault_plan=fault_plan: check_case(fault_plan)
    yield "already-partially-delivered", lambda: check_case([], starting=5)
    yield "empty-feed", lambda: check_case([], feed=[])


def tool_cases(source: str):
    scenarios = [
        ("direct-success", ["success"], False, "succeeded"),
        ("committed-then-timeout", ["after-success"], False, "succeeded"),
        ("absent-then-retry", ["before", "success"], False, "succeeded"),
        ("pending-then-timeout", ["after-pending"], False, "pending"),
        ("direct-pending", ["pending"], False, "pending"),
        ("status-unavailable", ["after-success"], True, "unknown"),
        ("retry-committed-then-timeout", ["before", "after-success"], False, "succeeded"),
        ("retry-still-absent", ["before", "before"], False, "unknown"),
    ]
    for index, (label, modes, unavailable, expected_state) in enumerate(scenarios):
        def check(index=index, modes=modes, unavailable=unavailable, expected_state=expected_state):
            function = limited_function(source, "submit")
            payload = {"account": f"account-{index + 7}", "items": [index, 17], "amount_cents": 913 + index}
            original = copy.deepcopy(payload)
            key = f"stable-key-{index + 31}"
            receipt = {"receipt": f"receipt-{index + 99}", "amount": original["amount_cents"]}
            state = ["absent"]
            submissions, queries = [], []
            reconciled = [True]
            effects = [0]
            class Remote:
                def submit(self, supplied_payload, supplied_key):
                    assert supplied_payload == original and supplied_key == key, "retry parameters/key changed"
                    assert reconciled[0] and state[0] == "absent", "retried without confirmed absence"
                    submissions.append((copy.deepcopy(supplied_payload), supplied_key))
                    assert len(submissions) <= 2, "submit budget exceeded"
                    mode = modes[min(len(submissions) - 1, len(modes) - 1)]
                    if mode == "before":
                        reconciled[0] = False
                        raise TimeoutError("request outcome unavailable")
                    state[0] = "pending" if "pending" in mode else "succeeded"
                    effects[0] += 1
                    if mode.startswith("after"):
                        reconciled[0] = False
                        raise TimeoutError("request outcome unavailable")
                    return {"state": state[0], **({"result": copy.deepcopy(receipt)}
                            if state[0] == "succeeded" else {})}
                def status(self, supplied_key):
                    assert supplied_key == key, "status used a different key"
                    queries.append(supplied_key)
                    assert len(queries) <= 2, "status budget exceeded"
                    if unavailable:
                        raise TimeoutError("status unavailable")
                    reconciled[0] = True
                    return {"state": state[0], **({"result": copy.deepcopy(receipt)}
                            if state[0] == "succeeded" else {})}
            result = function(Remote(), payload, key)
            expected = {"state": expected_state, **({"result": receipt}
                        if expected_state == "succeeded" else {"key": key})}
            assert result == expected, "wrong reconciled result"
            assert payload == original, "input payload mutated"
            assert effects[0] <= 1, "duplicate logical effect"
            assert len(submissions) == len(modes), "unexpected number of writes"
            if "after" in modes[-1] or "before" in modes:
                assert queries, "ambiguous outcome was not queried"
        yield label, check


def grade_source(task: str, source: str) -> dict:
    generators = {"sql-grain": sql_cases, "pipeline-replay": pipeline_cases,
                  "tool-write-recovery": tool_cases}
    checks = []
    for name, check in generators[task](source):
        try:
            detail = check()
        except Exception as error:
            checks.append({"case": name, "passed": False,
                           "error": f"{type(error).__name__}: {str(error)[:200]}"})
        else:
            checks.append({"case": name, "passed": True, **(detail or {})})
    return {"task": task, "success": all(check["passed"] for check in checks), "checks": checks}


if __name__ == "__main__":
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (4, 4))
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    except (ImportError, OSError, ValueError):
        pass
    print(json.dumps(grade_source(sys.argv[1], Path(sys.argv[2]).read_text(encoding="utf-8-sig"))))
