#!/usr/bin/env bash
# scripts/credential-lint.sh — L3 机器门禁：凭证泄露硬拦截
#
# 为什么存在：六大红线第 1 条的「硬约束」实现。LLM 的自觉不可靠，
#   且只有 Claude Code 有运行时 hook——git hook 是唯一对所有 agent
#   （Codex / Cursor / Aider / 人类）等效的拦截点。
#
# 用法：
#   独立跑：    bash scripts/credential-lint.sh            # 扫描暂存区（git add 过的内容）
#   挂 hook：   ln -sf ../../scripts/credential-lint.sh .git/hooks/pre-commit
#   扫全目录：  bash scripts/credential-lint.sh --all      # 不依赖 git，扫当前目录所有文本文件
#
# 退出码：0 = 干净；1 = 发现疑似凭证（拦截 commit）
set -uo pipefail

# 凭证特征库（按误报率从低到高排列；新特征往这里加，一行一个）
PATTERNS=(
  'sk-[A-Za-z0-9_-]{20,}'                 # OpenAI / Anthropic 风格 API key
  'ghp_[A-Za-z0-9]{36}'                   # GitHub personal access token
  'gho_[A-Za-z0-9]{36}'                   # GitHub OAuth token
  'AKIA[0-9A-Z]{16}'                      # AWS Access Key ID
  'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY' # 私钥文件块
  'xoxb-[0-9A-Za-z-]{20,}'                # Slack bot token
  '(password|passwd|secret)\s*[:=]\s*["'"'"'][^"'"'"']{8,}' # 明文密码赋值
)

# 这些路径不扫（特征库自身 / 文档里的脱敏示例）
EXCLUDE_RE='(scripts/credential-lint\.sh|docs/research/|\.git/)'

MODE="${1:-staged}"
FOUND=0

scan_content() {
  # $1 = 文件标签（报告用），stdin = 内容
  local label="$1" hits
  for p in "${PATTERNS[@]}"; do
    hits=$(grep -nE "$p" - 2>/dev/null || true)
    if [ -n "$hits" ]; then
      echo "⛔ 疑似凭证：$label"
      echo "$hits" | head -3 | sed 's/^/     /'
      FOUND=1
    fi
  done
}

if [ "$MODE" = "--all" ]; then
  # 全目录模式：扫所有 1MB 以下文本文件
  while IFS= read -r f; do
    echo "$f" | grep -qE "$EXCLUDE_RE" && continue
    scan_content "$f" < "$f"
  done < <(find . -type f -size -1M ! -path './.git/*' ! -path './node_modules/*' -exec grep -Il '' {} \; 2>/dev/null)
else
  # 暂存区模式（pre-commit 默认）：只扫 git add 过的增量内容
  while IFS= read -r f; do
    echo "$f" | grep -qE "$EXCLUDE_RE" && continue
    # 用进程替换而不是管道：管道右侧是子 shell，FOUND=1 会丢失（bash 3.2 实测踩坑）
    scan_content "$f" < <(git show ":$f" 2>/dev/null)
  done < <(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
fi

if [ "$FOUND" -eq 1 ]; then
  cat <<'MSG'

🔒 凭证 lint 拦截了本次操作（六大红线第 1 条）。
   处理方式：
   1. 真凭证 → 移到私有层（用户级 MCP / ~/.ssh/config / Keychain），文件里只留别名
   2. 误报   → 确认是脱敏示例后，把该路径加进本脚本 EXCLUDE_RE
   绝不建议用 --no-verify 绕过——绕过一次，红线就名存实亡。
MSG
  exit 1
fi

echo "✅ 凭证 lint 通过（模式：${MODE}）"
exit 0
