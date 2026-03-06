# API 调用示例

本文档提供各种编程语言的 API 调用示例。

## 基础端点

```
POST /api/chat           - 发送消息并获取回答
POST /api/session/reset  - 重置会话
GET  /api/stats          - 获取统计信息
GET  /docs              - Swagger API 文档
```

---

## cURL 示例

### 发送消息

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "理博基金是一家什么样的公司？",
    "session_id": "optional-uuid"
  }'
```

**响应：**
```json
{
  "reply": "您好，理博基金全称是杭州理博私募基金管理有限公司...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 多轮对话（保留会话）

```bash
# 第一条消息
SESSION=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你们有哪些策略？"}' | jq -r '.session_id')

# 第二条消息（使用同一 session）
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"那个策略的收益怎么样？\",
    \"session_id\": \"$SESSION\"
  }"
```

### 重置会话

```bash
curl -X POST http://localhost:8000/api/session/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

### 获取统计

```bash
curl http://localhost:8000/api/stats
```

---

## Python 示例

### 基础调用

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def ask(message, session_id=None):
    """发送消息并获取回答"""
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": message,
            "session_id": session_id
        }
    )
    data = response.json()
    return data["reply"], data["session_id"]

# 单次查询
reply, session = ask("理博基金是一家什么样的公司？")
print(f"AI: {reply}\n")

# 多轮对话
reply2, _ = ask("那你们的AI选股策略是怎样的？", session)
print(f"AI: {reply2}\n")
```

### 使用 requests 库的完整示例

```python
import requests
import time

class LiboAIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None

    def chat(self, message):
        """发送消息"""
        payload = {"message": message}
        if self.session_id:
            payload["session_id"] = self.session_id

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        self.session_id = data["session_id"]
        return data["reply"]

    def reset(self):
        """重置会话"""
        if self.session_id:
            requests.post(
                f"{self.base_url}/api/session/reset",
                json={"session_id": self.session_id}
            )
            self.session_id = None

    def get_stats(self):
        """获取统计信息"""
        response = requests.get(f"{self.base_url}/api/stats")
        response.raise_for_status()
        return response.json()

# 使用示例
if __name__ == "__main__":
    client = LiboAIClient()

    # 发送消息
    reply1 = client.chat("理博基金有哪些产品？")
    print(f"Q: 理博基金有哪些产品？\nA: {reply1}\n")

    # 后续问题
    reply2 = client.chat("万象7号今年收益怎么样？")
    print(f"Q: 万象7号今年收益怎么样？\nA: {reply2}\n")

    # 查看统计
    stats = client.get_stats()
    print(f"统计: {stats}")

    # 重置会话
    client.reset()
```

---

## JavaScript / Node.js 示例

### 基础调用

```javascript
const baseUrl = "http://localhost:8000";

async function askAI(message, sessionId = null) {
  const response = await fetch(`${baseUrl}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: message,
      session_id: sessionId
    })
  });

  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
}

// 单次查询
(async () => {
  const { reply, session_id } = await askAI("理博基金是一家什么样的公司？");
  console.log(`AI: ${reply}\n`);

  // 多轮对话
  const { reply: reply2 } = await askAI("那你们的策略有什么优势？", session_id);
  console.log(`AI: ${reply2}\n`);
})();
```

### 完整客户端类

```javascript
class LiboAIClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }

  async chat(message) {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        session_id: this.sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    this.sessionId = data.session_id;
    return data.reply;
  }

  async reset() {
    if (this.sessionId) {
      await fetch(`${this.baseUrl}/api/session/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: this.sessionId })
      });
      this.sessionId = null;
    }
  }

  async getStats() {
    const response = await fetch(`${this.baseUrl}/api/stats`);
    return await response.json();
  }
}

// 使用示例
(async () => {
  const client = new LiboAIClient();

  const reply1 = await client.chat("理博基金有哪些产品？");
  console.log(`Q: 理博基金有哪些产品？\nA: ${reply1}\n`);

  const reply2 = await client.chat("万象7号是什么产品？");
  console.log(`Q: 万象7号是什么产品？\nA: ${reply2}\n`);

  const stats = await client.getStats();
  console.log("统计:", stats);
})();
```

---

## PHP 示例

```php
<?php

class LiboAIClient {
    private $baseUrl = "http://localhost:8000";
    private $sessionId = null;

    public function chat($message) {
        $url = $this->baseUrl . "/api/chat";

        $data = [
            "message" => $message,
            "session_id" => $this->sessionId
        ];

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ["Content-Type: application/json"]);

        $response = curl_exec($ch);
        curl_close($ch);

        $result = json_decode($response, true);
        $this->sessionId = $result["session_id"];

        return $result["reply"];
    }

    public function getStats() {
        $url = $this->baseUrl . "/api/stats";
        $response = json_decode(file_get_contents($url), true);
        return $response;
    }
}

// 使用示例
$client = new LiboAIClient();

$reply = $client->chat("理博基金是一家什么样的公司？");
echo "AI: " . $reply . "\n\n";

$stats = $client->getStats();
echo "知识库: " . $stats["total_documents"] . " 条\n";
?>
```

---

## Java 示例

```java
import okhttp3.*;
import com.google.gson.*;

public class LiboAIClient {
    private static final String BASE_URL = "http://localhost:8000";
    private static final OkHttpClient client = new OkHttpClient();
    private String sessionId = null;

    public String chat(String message) throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("message", message);
        if (sessionId != null) {
            body.addProperty("session_id", sessionId);
        }

        RequestBody requestBody = RequestBody.create(
            body.toString(),
            MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
            .url(BASE_URL + "/api/chat")
            .post(requestBody)
            .build();

        try (Response response = client.newCall(request).execute()) {
            String responseBody = response.body().string();
            JsonObject json = JsonParser.parseString(responseBody).getAsJsonObject();

            sessionId = json.get("session_id").getAsString();
            return json.get("reply").getAsString();
        }
    }

    public static void main(String[] args) throws IOException {
        LiboAIClient client = new LiboAIClient();

        String reply = client.chat("理博基金是一家什么样的公司？");
        System.out.println("AI: " + reply);
    }
}
```

---

## Go 示例

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
)

type ChatRequest struct {
    Message   string `json:"message"`
    SessionID string `json:"session_id,omitempty"`
}

type ChatResponse struct {
    Reply     string `json:"reply"`
    SessionID string `json:"session_id"`
}

func askAI(message, sessionID string) (ChatResponse, error) {
    req := ChatRequest{
        Message:   message,
        SessionID: sessionID,
    }

    body, _ := json.Marshal(req)

    resp, err := http.Post(
        "http://localhost:8000/api/chat",
        "application/json",
        bytes.NewBuffer(body),
    )
    if err != nil {
        return ChatResponse{}, err
    }
    defer resp.Body.Close()

    var result ChatResponse
    respBody, _ := ioutil.ReadAll(resp.Body)
    json.Unmarshal(respBody, &result)

    return result, nil
}

func main() {
    result, _ := askAI("理博基金是一家什么样的公司？", "")
    fmt.Printf("AI: %s\n", result.Reply)
    fmt.Printf("Session: %s\n", result.SessionID)
}
```

---

## 常见问题

### Q: 如何在生产环境中使用？
A: 建议：
1. 添加身份验证（API Key）
2. 使用 CORS 中间件
3. 部署到云服务（AWS Lambda, GCP Cloud Run 等）
4. 使用负载均衡

### Q: 如何处理长连接？
A: 考虑使用 WebSocket：
```python
# 需要修改 server.py 添加 WebSocket 支持
from fastapi import WebSocket
```

### Q: 超时时间？
A: 默认 LLM 调用超时 30 秒，可在 `rag_engine.py` 中修改

### Q: 支持流式响应吗？
A: 目前返回完整响应，可扩展为 Server-Sent Events（SSE）支持流式输出

---

更多问题？查看主 README.md 或启动服务后访问 `/docs` 查看完整 API 文档。
