# 公开前自查台账（PUBLISH-AUDIT）

首次推送公开仓库前的一次性自查记录。**结论：可公开**，含两项已知特征（非缺陷，但读者应当知情）。

扫描对象：仓库工作区全部文件（排除 `.git`），共 **221 个跟踪文件**。

---

## 一、敏感信息扫描

| 检查项 | 手法 | 结果 |
|---|---|---|
| API Key / Token | `sk-…`、`ghp_…`、`github_pat_…`、`Bearer …`、`AKIA…`（AWS） | **0 命中** |
| 私钥 | `-----BEGIN … PRIVATE KEY-----` | **0 命中** |
| 键值式凭据 | `api_key\|secret\|password\|token\|authorization` 后跟 8 字符以上引号串 | **0 命中** |
| 邮箱 | 通用邮箱正则 | **0 命中**（提交身份用的 `…@users.noreply.github.com` 为 noreply，非真实邮箱） |
| 手机号 | `1[3-9]\d{9}` | **0 命中**（仅有 3 处落在 SHA256 十六进制串内的误报） |
| 身份证号 | 18 位身份证正则 | **0 命中** |

提交身份：`user.name = haiyu-zongdui`、`user.email = haiyu-zongdui@users.noreply.github.com`（仓库级配置，未使用真实邮箱）。

---

## 二、已知特征（如实记录）

### 特征 1：本机绝对路径（约 80 个文件）

脚本与报告里保留了开发当时的工作区绝对路径，形如
`C:\Users\D_A\WorkBuddy\<会话目录>\repo\haiyu-zongdui-tankuangjingniang\…`，
其中包含本机 Windows 用户名 `D_A`。

| 分布 | 数量 |
|---|---|
| `docs/tools/patches/*.py`（一次性补丁脚本） | 约 66 个，各 1–2 处 |
| `docs/tools/verifiers/*.js`（历史验收脚本） | 约 12 个，各 1–2 处 |
| `docs/reports/_pack2_manifest.json` | **1935 处**（46 个被清理文件的逐条 `src`/`dst` 绝对路径） |
| `docs/reports/_chain.json` | 9 处 |
| 其他报告 | 零星 |

**为何不清理**：这些文件是**历史证据**，记录的是当时真实执行过的动作。把路径改写掉等于篡改台账，会让"可复现校验"变成不可信。

**为何风险低**：泄露的只是本机用户名 `D_A` 与目录结构，不含任何凭据、邮箱、身份信息。

**已完成的收敛**：本轮新增的工具脚本（`release/`、`housekeeping/` 下的 6 个）全部改为**自解析路径**（`os.path.dirname(__file__)` 上溯），不再写死工作区。历史脚本保持原样。

### 特征 2：留底包不在仓库内

`.gitignore` 有意排除以下内容（见该文件注释"仅在本地存证，不进仓库"）：

```
archive/*.zip        # 整理前的留底包（本地共 15 个，其中两个 8.3 MB / 5.5 MB）
archive/journal.json # 删除记账
archive/ledger.json  # 归档台账（名字 / 字节 / sha256）
```

**影响**：公开仓库的读者无法下载留底包本体来复算哈希。

**补偿**：哈希证据本身已随仓库发布——

- `docs/reports/_zipcov.txt`：47 个条目逐一列出 `ledger` 记录的 SHA256 与归档包内实际算出的 SHA256，全部一致；
- `docs/reports/_vaultout.txt`：台账自洽性核对（归档数 vs 删除数）；
- `docs/reports/_clean4out.txt`、`_finishout.txt`：两轮清理的执行日志。

即"能被读者独立验证"的那部分证据是完整的，缺的只是原始压缩包。

---

## 三、仓库规模

| 指标 | 值 |
|---|---|
| 跟踪文件 | 221 |
| 提交数 | 7 |
| `.git` 体积 | 11.25 MB |
| 工作区体积 | 28.1 MB（含未入库的留底包） |
| 单文件最大 | `docs/versions/v0.4.11.user.js` 640,151 字节 |

体积主要来自 9 个版本快照与 `docs/bisect/` 下的候选构建。均在 GitHub 常规范围内。

---

## 四、行尾保证

`.gitattributes` 已钉死：`.user.js` 一律 `-text`（禁用转换）。已实测**四层一致**——
工作区、git 对象层（`git cat-file`）、`git archive` 导出层、9 个历史快照，同一 SHA256、零裸 LF。
复现：`python docs/tools/release/_gitverify.py`（报告见 `docs/reports/_eolout.txt`）。

---

## 五、自查后可公开项

- [x] 无凭据 / 密钥 / 私钥
- [x] 无邮箱 / 手机号 / 身份信息
- [x] 提交身份使用 noreply 邮箱
- [x] 交付脚本 `node --check` 通过、回归验收 `fail=0`
- [x] 哈希清单 12 项全部一致（`_verify_sums.py`）
- [x] 工作区干净，无未跟踪残留
- [ ] **已知**：约 80 个文件含本机绝对路径（见特征 1）
- [ ] **已知**：留底包未入库（见特征 2）
