## Question
![](/assets/q_indexing.png)
## Response Section

**Database index** คือโครงสร้างข้อมูลเสริม (ส่วนใหญ่เป็น **B-Tree / B+Tree**, บางกรณีเป็น Hash, GIN, GiST, BRIN) ที่เก็บค่าของคอลัมน์ที่เลือกไว้แบบเรียงลำดับ พร้อม pointer ไปยังแถวจริง
เหมือน "สารบัญท้ายหนังสือ" — แทนที่จะต้องอ่านทุกหน้า (full table scan, `O(n)`) ก็กระโดดไปหน้าที่ต้องการได้เลย (`O(log n)`)

### ข้อดี

1. **ค้นหาเร็วขึ้นมาก** — `WHERE`, `JOIN ... ON`, lookup ด้วย PK/FK จาก `O(n)` เหลือ `O(log n)`
2. **ช่วย `ORDER BY` / `GROUP BY` / `MIN()` / `MAX()`** — index เรียงลำดับไว้แล้ว ไม่ต้อง sort ใหม่
3. **บังคับความถูกต้องของข้อมูล** — `UNIQUE` index ป้องกันข้อมูลซ้ำ (เช่น email, username)
4. **Covering index / index-only scan** — ถ้า index มีทุกคอลัมน์ที่ query ต้องใช้ DB ไม่ต้องไปอ่าน table เลย
5. **ลดการ lock และ I/O** — อ่านเฉพาะ page ที่จำเป็น ทำให้ระบบรองรับ concurrency ได้ดีขึ้น
6. **JOIN เร็วขึ้น** — index บนคอลัมน์ FK ทำให้ nested loop / merge join มีประสิทธิภาพ

### ข้อจำกัด / ข้อเสีย

1. **เขียนช้าลง** — ทุก `INSERT / UPDATE / DELETE` ต้องอัปเดตทุก index ที่เกี่ยวข้องด้วย ยิ่งมี index มาก write ยิ่งช้า (write amplification)
2. **ใช้พื้นที่เพิ่ม** — ทั้งบน disk และใน memory (buffer pool) บางครั้ง index รวมกันใหญ่กว่า table
3. **ไม่ได้ช่วยทุก query**
   - คอลัมน์ที่ **selectivity ต่ำ** (เช่น gender, boolean) — DB มักเลือก full scan อยู่ดี
   - ใช้ function กับคอลัมน์ เช่น `WHERE LOWER(email) = ...` → ต้องใช้ functional/expression index
   - `LIKE '%abc'` (wildcard ข้างหน้า) ใช้ B-Tree ไม่ได้ → ต้องใช้ trigram / full-text index
   - type ไม่ตรง ทำให้เกิด implicit cast แล้ว index ไม่ถูกใช้
4. **Composite index ขึ้นกับลำดับคอลัมน์ (leftmost prefix)** — index `(school_id, last_name)` ช่วย `WHERE school_id = ?` ได้ แต่ไม่ช่วย `WHERE last_name = ?` อย่างเดียว
5. **ต้องดูแลรักษา** — index bloat / fragmentation, statistics ล้าสมัยทำให้ planner เลือกแผนผิด ต้อง `ANALYZE`, `REINDEX`
6. **การสร้าง index บน table ใหญ่อาจ lock table** — ต้องใช้ `CREATE INDEX CONCURRENTLY` (PostgreSQL) ในระบบ production
7. **Index ซ้ำซ้อน/ไม่ถูกใช้** — เปลืองทรัพยากรโดยไม่มีประโยชน์ และทำให้ query planner มีตัวเลือกมากเกินจำเป็น

### แนวทางการใช้ index ให้เหมาะสม

- สร้าง index ตาม **query pattern จริง** (คอลัมน์ใน `WHERE`, `JOIN`, `ORDER BY` ที่ถูกใช้บ่อย) ไม่ใช่ทุกคอลัมน์
- ใช้ **`EXPLAIN` / `EXPLAIN ANALYZE`** ตรวจว่า query ใช้ index จริงหรือไม่
- เรียงลำดับคอลัมน์ใน composite index: คอลัมน์ที่ใช้ equality / selectivity สูงไว้ก่อน
- พิจารณา **partial index** (เช่น `WHERE is_active = true`) เพื่อลดขนาด
- ตารางที่ write หนัก (log, event) ควรมี index น้อยที่สุดเท่าที่จำเป็น
- ตรวจหา index ที่ไม่ได้ใช้ (เช่น `pg_stat_user_indexes`) แล้วลบออก

ตัวอย่างใน Django:

```python
class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)  # FK มี index อัตโนมัติ

    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name"]),  # composite index สำหรับค้นหาชื่อ
        ]
```

**สรุป:** Index คือการ **แลกพื้นที่และความเร็วในการเขียน เพื่อความเร็วในการอ่าน** ควรออกแบบจาก workload จริงและวัดผลด้วย query plan เสมอ
