# API 说明

基础地址：`http://127.0.0.1:8000`。时间使用本地时间字符串 `YYYY-MM-DDTHH:MM`。

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/labs` | 返回示例实验室列表 |
| GET | `/api/bookings` | 返回预约列表 |
| POST | `/api/bookings` | 创建预约；冲突时返回 409 |
| DELETE | `/api/bookings/{id}` | 取消预约 |

创建请求示例：

```json
{
  "lab_id": 1,
  "requester": "张同学",
  "purpose": "课程实验",
  "participants": 12,
  "start": "2026-11-09T09:00",
  "end": "2026-11-09T10:00"
}
```

此 API 仅绑定本地地址用于课程演示，没有身份认证。不能直接对公网开放。

