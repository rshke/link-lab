"""Device-local repair rules, independent of HTTP and the SiLA SDK."""
from datetime import datetime, timezone
import uuid


RECIPES = {
    "channel_blockage": {
        "title": "检测通道堵塞", "inspection": "检查进样通道",
        "finding": "进样压力偏高，过滤器与通道存在堵塞。",
        "steps": [{"action": "flush_channel", "label": "冲洗检测通道"},
                  {"action": "replace_filter", "label": "更换过滤器"}],
    },
    "sensor_drift": {
        "title": "传感器漂移", "inspection": "检查标准参考值",
        "finding": "参考读数偏离基线，需要清洁后重新校准。",
        "steps": [{"action": "clean_sensor", "label": "清洁传感器"},
                  {"action": "calibrate_sensor", "label": "使用标准样校准"}],
    },
    "loose_cable": {
        "title": "内部线缆松动", "inspection": "检查内部传感器连接",
        "finding": "内部传感器接插件接触不良，SiLA 服务连接正常。",
        "steps": [{"action": "reseat_cable", "label": "重新插接线缆"},
                  {"action": "secure_connector", "label": "锁紧接插件"}],
    },
}


class Maintenance:
    """Caller serializes access with the device engine's lock."""
    def __init__(self):
        self.incident_id = None
        self.code = None
        self.state = "ready"
        self.revision = 0
        self.completed = []
        self.history = []
        self.requests = {}

    def _record(self, action, message):
        self.revision += 1
        self.history.append({"revision": self.revision, "incidentId": self.incident_id,
                             "action": action, "message": message,
                             "at": datetime.now(timezone.utc).isoformat()})

    def snapshot(self):
        recipe = RECIPES.get(self.code)
        return {"deviceId": "measurement-1", "state": self.state,
                "incidentId": self.incident_id, "faultCode": self.code,
                "revision": self.revision, "recipe": recipe,
                "completed": list(self.completed), "history": list(self.history)}

    def inject(self, code):
        if code not in RECIPES:
            raise ValueError("Unsupported persistent fault")
        if self.state != "ready":
            raise ValueError("An incident is already open")
        self.incident_id = str(uuid.uuid4())
        self.code, self.state, self.completed = code, "faulted", []
        self._record("fault_detected", RECIPES[code]["title"])
        return self.snapshot()

    def apply(self, request_id, incident_id, action, revision):
        signature = (incident_id, action, revision)
        if request_id in self.requests:
            old_signature, result = self.requests[request_id]
            if old_signature != signature:
                return {"accepted": False, "message": "请求 ID 已用于不同操作", "device": self.snapshot()}
            return result
        if incident_id != self.incident_id or revision != self.revision:
            return {"accepted": False, "message": "维护状态已变化，请刷新后重试", "device": self.snapshot()}
        accepted = False
        if self.state == "ready":
            message = "设备无需维护"
        elif action == "inspect":
            if self.state != "faulted":
                message = "本次故障已完成检查"
            else:
                self.state, accepted = "diagnosed", True
                message = RECIPES[self.code]["finding"]
        elif action == "self_test":
            if self.state != "awaiting_self_test":
                message = "自检未通过：维修步骤尚未完成"
            else:
                self.state, accepted = "ready", True
                message = "自检通过，设备恢复可用；原实验不会自动恢复"
        else:
            steps = RECIPES[self.code]["steps"]
            expected = steps[len(self.completed)] if len(self.completed) < len(steps) else None
            if self.state not in ("diagnosed", "repairing"):
                message = "请先检查故障，完成维修后再执行自检"
            elif expected is None or action != expected["action"]:
                message = "操作与当前故障或维修顺序不匹配，故障仍然存在"
            else:
                self.completed.append(action)
                self.state = "awaiting_self_test" if len(self.completed) == len(steps) else "repairing"
                accepted, message = True, expected["label"] + "已完成（模拟）"
        self._record(action, message)
        result = {"accepted": accepted, "message": message, "device": self.snapshot()}
        self.requests[request_id] = (signature, result)
        return result
