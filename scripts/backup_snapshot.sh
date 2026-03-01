#!/usr/bin/env bash
set -euo pipefail

########################################
# 固定配置
########################################

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"

PROJECT_NAME="ai_research_studio"
PROJECT_DIR="$HOME/studio/projects/$PROJECT_NAME"

BACKUP_BASE_DIR="$HOME/backups/${PROJECT_NAME}_snapshots"
SNAPSHOT_DIR="$BACKUP_BASE_DIR/${PROJECT_NAME}_snapshot_${TIMESTAMP}"
ARCHIVE_FILE="$BACKUP_BASE_DIR/${PROJECT_NAME}_snapshot_${TIMESTAMP}.tar.gz"

OPENCLAW_DIR="$HOME/.openclaw"
OPENCLAW_PLIST="$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"

########################################
# 工具函数
########################################

log() {
  echo "[INFO] $*"
}

warn() {
  echo "[WARN] $*" >&2
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

safe_run_to_file() {
  # 用法: safe_run_to_file "输出文件" 命令 参数...
  local outfile="$1"
  shift
  {
    echo ">>> COMMAND: $*"
    echo
    "$@"
  } >"$outfile" 2>&1 || true
}

safe_copy_if_exists() {
  local src="$1"
  local dst="$2"
  if [[ -e "$src" ]]; then
    cp -av "$src" "$dst" >/dev/null 2>&1 || true
  else
    warn "不存在，跳过: $src"
  fi
}

########################################
# 前置检查
########################################

mkdir -p "$BACKUP_BASE_DIR"
mkdir -p "$SNAPSHOT_DIR"

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "[ERROR] 项目目录不存在: $PROJECT_DIR" >&2
  exit 1
fi

log "备份根目录: $BACKUP_BASE_DIR"
log "本次快照目录: $SNAPSHOT_DIR"

########################################
# 目录结构
########################################

mkdir -p "$SNAPSHOT_DIR/project"
mkdir -p "$SNAPSHOT_DIR/openclaw"
mkdir -p "$SNAPSHOT_DIR/env"
mkdir -p "$SNAPSHOT_DIR/shell"
mkdir -p "$SNAPSHOT_DIR/meta"

########################################
# 1) 备份项目代码
########################################

log "备份项目代码..."

rsync -a \
  --exclude=".DS_Store" \
  --exclude="__pycache__" \
  --exclude=".pytest_cache" \
  --exclude=".mypy_cache" \
  --exclude=".ruff_cache" \
  --exclude=".venv" \
  --exclude="venv" \
  --exclude="node_modules" \
  --exclude=".git/objects" \
  "$PROJECT_DIR/" \
  "$SNAPSHOT_DIR/project/$PROJECT_NAME/"

########################################
# 2) 备份 OpenClaw 配置与状态
########################################

log "备份 OpenClaw 配置..."

if [[ -d "$OPENCLAW_DIR" ]]; then
  rsync -a "$OPENCLAW_DIR/" "$SNAPSHOT_DIR/openclaw/.openclaw/"
else
  warn "OpenClaw 目录不存在: $OPENCLAW_DIR"
fi

safe_copy_if_exists "$OPENCLAW_PLIST" "$SNAPSHOT_DIR/openclaw/"

########################################
# 3) 导出系统与环境信息
########################################

log "导出环境信息..."

{
  echo "===== BACKUP META ====="
  echo "Timestamp: $TIMESTAMP"
  echo "Project: $PROJECT_NAME"
  echo "Project Dir: $PROJECT_DIR"
  echo "Snapshot Dir: $SNAPSHOT_DIR"
  echo

  echo "===== DATE ====="
  date
  echo

  echo "===== OS ====="
  sw_vers || true
  uname -a || true
  echo

  echo "===== PATH ====="
  echo "$PATH"
  echo
} > "$SNAPSHOT_DIR/env/system_report.txt"

safe_run_to_file "$SNAPSHOT_DIR/env/node_info.txt" bash -lc '
  which node || true
  node -v || true
  which npm || true
  npm -v || true
  which pnpm || true
  pnpm -v || true
'

safe_run_to_file "$SNAPSHOT_DIR/env/python_info.txt" bash -lc '
  which python3 || true
  python3 -V || true
  which pip3 || true
  pip3 -V || true
'

safe_run_to_file "$SNAPSHOT_DIR/env/git_info.txt" bash -lc '
  which git || true
  git --version || true
'

safe_run_to_file "$SNAPSHOT_DIR/env/openclaw_version.txt" bash -lc '
  which openclaw || true
  openclaw --version || true
'

safe_run_to_file "$SNAPSHOT_DIR/env/openclaw_gateway_status.txt" bash -lc '
  openclaw gateway status
'

safe_run_to_file "$SNAPSHOT_DIR/env/openclaw_models_status.txt" bash -lc '
  openclaw models status
'

safe_run_to_file "$SNAPSHOT_DIR/env/openclaw_channels_status.txt" bash -lc '
  openclaw channels status --probe
'

########################################
# 4) 导出包管理清单
########################################

log "导出包管理清单..."

if have_cmd brew; then
  safe_run_to_file "$SNAPSHOT_DIR/env/brew_list.txt" brew list --versions
  safe_run_to_file "$SNAPSHOT_DIR/env/brew_info_installed.txt" brew info --installed
else
  warn "brew 不存在，跳过"
fi

if have_cmd npm; then
  safe_run_to_file "$SNAPSHOT_DIR/env/npm_global.txt" npm list -g --depth=0
else
  warn "npm 不存在，跳过"
fi

########################################
# 5) 项目关键配置文件
########################################

log "备份项目关键配置文件..."

safe_copy_if_exists "$PROJECT_DIR/pyproject.toml" "$SNAPSHOT_DIR/env/"
safe_copy_if_exists "$PROJECT_DIR/poetry.lock" "$SNAPSHOT_DIR/env/"
safe_copy_if_exists "$PROJECT_DIR/requirements.txt" "$SNAPSHOT_DIR/env/"
safe_copy_if_exists "$PROJECT_DIR/package.json" "$SNAPSHOT_DIR/env/"
safe_copy_if_exists "$PROJECT_DIR/pnpm-lock.yaml" "$SNAPSHOT_DIR/env/"
safe_copy_if_exists "$PROJECT_DIR/.env" "$SNAPSHOT_DIR/env/project.env"

########################################
# 6) shell 配置
########################################

log "备份 shell 配置..."

safe_copy_if_exists "$HOME/.zshrc" "$SNAPSHOT_DIR/shell/"
safe_copy_if_exists "$HOME/.bashrc" "$SNAPSHOT_DIR/shell/"
safe_copy_if_exists "$HOME/.bash_profile" "$SNAPSHOT_DIR/shell/"
safe_copy_if_exists "$HOME/.gitconfig" "$SNAPSHOT_DIR/shell/"
safe_copy_if_exists "$HOME/.npmrc" "$SNAPSHOT_DIR/shell/"

########################################
# 7) 导出 git 状态
########################################

log "导出 git 状态..."

safe_run_to_file "$SNAPSHOT_DIR/env/git_status.txt" bash -lc "
  cd '$PROJECT_DIR' && git status
"

safe_run_to_file "$SNAPSHOT_DIR/env/git_log_last20.txt" bash -lc "
  cd '$PROJECT_DIR' && git log --oneline -n 20
"

########################################
# 8) 写入备份说明
########################################

cat > "$SNAPSHOT_DIR/meta/README_BACKUP.txt" <<EOF
这是自动生成的项目快照备份。

生成时间:
  $TIMESTAMP

项目目录:
  $PROJECT_DIR

包含内容:
  - project/        项目代码快照
  - openclaw/       OpenClaw 配置与状态
  - env/            环境信息、版本信息、状态导出
  - shell/          shell 与工具配置
  - meta/           备份说明

压缩包:
  $ARCHIVE_FILE

注意:
  该备份可能包含敏感信息（API Key、Token、.env 等）。
  建议:
  1. 不要上传到公开仓库
  2. 如需云端保存，请额外加密
EOF

########################################
# 9) 生成压缩包
########################################

log "生成 tar.gz 压缩包..."

tar -czf "$ARCHIVE_FILE" -C "$BACKUP_BASE_DIR" "$(basename "$SNAPSHOT_DIR")"

########################################
# 10) 输出结果
########################################

log "备份完成"
echo
echo "快照目录:"
echo "  $SNAPSHOT_DIR"
echo
echo "压缩包:"
echo "  $ARCHIVE_FILE"
echo
log "你可以用下面命令查看:"
echo "  ls -lh \"$BACKUP_BASE_DIR\""