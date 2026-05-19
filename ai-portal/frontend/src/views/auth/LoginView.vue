<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-header">
        <el-icon size="48" class="login-icon"><Cpu /></el-icon>
        <h1>AI技术门户</h1>
        <p>用户登录</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.rememberMe">记住我（30天）</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>首次登录请使用默认账号：admin / 你在.env中设置的密码</p>
        <p>还没有账号？<router-link to="/register" class="register-link">立即注册</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 登录页面
 * 简洁的登录表单，支持记住我功能
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Cpu, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  rememberMe: false,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  const result = await authStore.login(form.username, form.password, form.rememberMe)
  loading.value = false

  if (result.success) {
    ElMessage.success('登录成功')
    router.push('/')
  } else {
    ElMessage.error(result.error || '登录失败')
  }
}
</script>

<style scoped lang="scss">
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--app-bg) 0%, var(--app-bg-secondary) 100%);
}

.login-container {
  width: 400px;
  padding: 40px;
  background-color: var(--app-bg-card);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  box-shadow: var(--el-box-shadow);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;

  .login-icon {
    color: var(--app-accent);
    margin-bottom: 16px;
  }

  h1 {
    margin: 0 0 8px;
    font-size: 24px;
    color: var(--app-text);
  }

  p {
    margin: 0;
    color: var(--app-text-secondary);
    font-size: 14px;
  }
}

.login-form {
  .login-btn {
    width: 100%;
  }
}

.login-footer {
  margin-top: 24px;
  text-align: center;

  p {
    margin: 4px 0;
    font-size: 12px;
    color: var(--app-text-secondary);
  }

  .register-link {
    color: var(--app-accent);
    text-decoration: none;
    &:hover { text-decoration: underline; }
  }
}
</style>
