#!/bin/bash
# ============================================================
# AI技术门户 - 后端启动脚本（直接使用系统Python）
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== AI技术门户 - 后端启动 ===${NC}"

# 1. 检查Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}错误: 未找到Python3${NC}"
    exit 1
fi
echo -e "${YELLOW}[1/4]${NC} Python: $($PYTHON_CMD --version 2>&1)"

# 2. 检查依赖（首次自动安装）
echo -e "${YELLOW}[2/4]${NC} 检查依赖..."
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo "  首次运行，安装依赖（可能需要几分钟）..."
    $PYTHON_CMD -m pip install -r requirements.txt --quiet --break-system-packages
    if [ $? -ne 0 ]; then
        echo -e "${RED}依赖安装失败，请手动执行: pip install -r requirements.txt --break-system-packages${NC}"
        exit 1
    fi
    echo "  ✅ 依赖安装完成"
else
    echo "  ✅ 依赖已就绪"
fi

# 3. 检查.env
echo -e "${YELLOW}[3/4]${NC} 检查配置..."
if [ ! -f ".env" ]; then
    echo "  ⚠️ 未找到.env，从.env.example复制"
    cp .env.example .env
    echo "  请编辑.env填入API密钥"
fi
mkdir -p ./data/uploads ./data/chroma

# 4. 启动
echo -e "${YELLOW}[4/4]${NC} 启动服务..."
echo -e "${GREEN}✅ http://localhost:8000 | Docs: http://localhost:8000/docs${NC}"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --timeout-keep-alive 300
