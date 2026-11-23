## Question
![](/assets/q_data_format.png)
## Response Section

### ภาพรวม

| | **JSON** (JavaScript Object Notation) | **Protocol Buffers (Protobuf)** |
|---|---|---|
| ผู้พัฒนา | มาตรฐานเปิด (RFC 8259) | Google |
| รูปแบบข้อมูล | **Text** (UTF-8) อ่านได้ด้วยตา | **Binary** อ่านด้วยตาไม่ได้ |
| Schema | ไม่บังคับ (schema-less) ใช้ JSON Schema / OpenAPI เสริมได้ | **บังคับ** ต้องประกาศใน `.proto` |
| ข้อมูล type | string, number, boolean, null, array, object | int32/int64/uint/sint, float/double, bool, string, bytes, enum, message, repeated, map, oneof |
| ขนาด payload | ใหญ่กว่า (มีชื่อ field ซ้ำทุก record, ตัวเลขเป็น text) | เล็กกว่ามาก (ใช้ field number + varint) โดยทั่วไปเล็กกว่า 3–10 เท่า |
| ความเร็ว serialize/parse | ช้ากว่า (ต้อง parse text) | เร็วกว่า (decode binary ตาม schema) |
| Code generation | ไม่ต้อง | ต้องใช้ `protoc` generate class ตามภาษา |
| การใช้งานบน Browser | รองรับ native (`JSON.parse`) | ต้องใช้ library / gRPC-Web |
| การใช้งานทั่วไป | REST API, config, public API, frontend ↔ backend | gRPC, microservice ภายใน, mobile ที่เน้นประหยัด bandwidth, event streaming |

### ตัวอย่างข้อมูลเดียวกัน

JSON:

```json
{
  "id": 1,
  "first_name": "Somchai",
  "gender": "M",
  "classroom_ids": [10, 11]
}
```

Protobuf schema (`student.proto`):

```proto
syntax = "proto3";

message Student {
  int64 id = 1;
  string first_name = 2;
  Gender gender = 3;
  repeated int64 classroom_ids = 4;
}

enum Gender {
  GENDER_UNSPECIFIED = 0;
  MALE = 1;
  FEMALE = 2;
}
```

บน wire Protobuf จะส่งเป็น byte เช่น `08 01 12 07 53 6f 6d ...` — ไม่มีชื่อ field ส่งไปเลย มีแค่ **field number + type + value**

ใช้งานใน Python:

```python
import json
from student_pb2 import Student, MALE   # generate ด้วย: protoc --python_out=. student.proto

# JSON
payload = json.dumps({"id": 1, "first_name": "Somchai", "gender": "M", "classroom_ids": [10, 11]})
data = json.loads(payload)

# Protobuf
student = Student(id=1, first_name="Somchai", gender=MALE, classroom_ids=[10, 11])
raw: bytes = student.SerializeToString()     # binary ขนาดเล็ก
decoded = Student.FromString(raw)
```

### JSON

**ข้อดี**
- มนุษย์อ่านและเขียนได้ง่าย debug ง่าย (ดูใน log, curl, browser DevTools ได้ทันที)
- รองรับทุกภาษา และ browser รองรับ native ไม่ต้องติดตั้งอะไรเพิ่ม
- ไม่ต้องมี schema/compile step เริ่มพัฒนาได้เร็ว ยืดหยุ่นในการเปลี่ยนโครงสร้าง
- เป็นมาตรฐานของ REST API และ ecosystem ใหญ่ (OpenAPI/Swagger, Postman, JSON Schema)
- เหมาะกับ public API ที่ client หลากหลาย

**ข้อเสีย**
- payload ใหญ่ ใช้ bandwidth มาก (ชื่อ field ซ้ำทุก object)
- parse ช้ากว่าและใช้ CPU มากกว่า
- type system จำกัด: ไม่มี int vs float, ไม่มี date/decimal/binary ต้องตกลงรูปแบบเอง (เช่น ISO 8601, ส่งเงินเป็น string, binary เป็น base64)
- ตัวเลขใหญ่เกิน 2^53 อาจเสียความแม่นยำใน JavaScript
- ไม่มี schema บังคับ → ต้อง validate เองทุกฝั่ง เสี่ยง field หาย/พิมพ์ผิดแล้วรู้ตอน runtime

### Protocol Buffers

**ข้อดี**
- ขนาดเล็กและ serialize/parse เร็ว เหมาะกับ traffic สูง, latency ต่ำ, mobile/IoT
- **Strongly typed + schema เป็น contract** ระหว่าง service, generate code ได้หลายภาษา จับ error ได้ตั้งแต่ compile time
- **Backward / forward compatibility** ดีถ้าทำตามกฎ: เพิ่ม field ใหม่ได้โดย client เก่ายังทำงานได้ (ignore field ที่ไม่รู้จัก)
- เป็นพื้นฐานของ **gRPC** (HTTP/2, streaming, deadline)

**ข้อเสีย**
- อ่านด้วยตาไม่ได้ debug ยากกว่า ต้องมีไฟล์ `.proto` และ tool ช่วย decode
- ต้องมี build step (protoc) และแชร์/จัดการ version ไฟล์ `.proto` ระหว่างทีม
- browser ไม่รองรับ native (ต้องใช้ gRPC-Web + proxy)
- ต้องระวังกฎการเปลี่ยน schema: **ห้ามเปลี่ยน/นำ field number กลับมาใช้ใหม่** (ใช้ `reserved`), เปลี่ยน type ไม่ได้
- proto3 แยก "ไม่ได้ส่ง" กับ "ค่า default" (0, "", false) ไม่ได้ ถ้าไม่ใช้ `optional`/wrapper types
- ecosystem/tooling สำหรับ public API น้อยกว่า JSON

### ควรเลือกอะไร

- **JSON** → public REST API, frontend/web, third-party integration, ระบบที่ให้ความสำคัญกับความง่ายและ debug ได้
- **Protobuf** → การสื่อสารระหว่าง microservice ภายใน (gRPC), ระบบ throughput สูง/latency ต่ำ, mobile ที่ต้องประหยัด bandwidth, event streaming ที่ต้องการ schema ชัดเจน
- หลายระบบใช้ **ทั้งสองแบบ**: JSON ที่ API Gateway ฝั่งภายนอก และ Protobuf/gRPC ระหว่าง service ภายใน
