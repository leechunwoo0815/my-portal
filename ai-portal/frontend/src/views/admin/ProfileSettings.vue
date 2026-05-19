<template>
  <div class="profile-settings">
    <el-card>
      <template #header><h3>个人设置</h3></template>
      <el-form :model="form" label-width="100px" v-loading="loading">
        <el-form-item label="头像">
          <div class="avatar-row">
            <el-avatar :size="64" :src="form.avatar_url">{{ form.username?.charAt(0) }}</el-avatar>
            <div class="avatar-actions">
              <el-input v-model="form.avatar_url" placeholder="头像URL或上传本地图片" />
              <el-upload
                :before-upload="beforeAvatarUpload"
                :http-request="handleAvatarUpload"
                accept="image/*"
                :show-file-list="false"
              >
                <el-button size="small" type="primary">上传头像</el-button>
              </el-upload>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="昵称"><el-input v-model="form.nickname" placeholder="请输入昵称" /></el-form-item>
        <el-form-item label="个人简介"><el-input v-model="form.bio" type="textarea" :rows="3" placeholder="介绍一下自己" /></el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
            <el-radio value="保密">保密</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="所在地"><el-input v-model="form.location" placeholder="所在城市" /></el-form-item>
        <el-form-item label="个人网站"><el-input v-model="form.website" placeholder="https://" /></el-form-item>
        <el-form-item label="GitHub"><el-input v-model="form.github" placeholder="GitHub 用户名" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveProfile" :loading="saving">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:20px">
      <template #header><h3>等级信息</h3></template>
      <div class="level-info">
        <el-tag :type="levelType" size="large">{{ levelText }}</el-tag>
        <p>积分: {{ form.points }} | 粉丝: {{ form.followers_count }} | 关注: {{ form.following_count }}</p>
        <p>注册时间: {{ new Date(form.created_at).toLocaleDateString() }}</p>
      </div>
    </el-card>

    <el-card style="margin-top:20px">
      <template #header><h3>修改密码</h3></template>
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="旧密码"><el-input v-model="passwordForm.old_password" type="password" show-password /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="passwordForm.new_password" type="password" show-password /></el-form-item>
        <el-form-item label="确认密码"><el-input v-model="passwordForm.confirm_password" type="password" show-password /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="changingPassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { getProfile, updateProfile, changePassword as changePasswordApi } from '@/api/auth'
import { uploadImage } from '@/api/upload'

const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const form = reactive({
  username: '', nickname: '', bio: '', avatar_url: '', gender: '', location: '',
  website: '', github: '', points: 0, followers_count: 0, following_count: 0,
  created_at: '', level: 1,
})
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const levelText = computed(() => form.level === 999 ? '管理员' : `LV${form.level}`)
const levelType = computed(() => {
  if (form.level === 999) return 'success'
  if (form.level >= 8) return 'warning'
  return 'info'
})

const loadProfile = async () => {
  loading.value = true
  try {
    const res: any = await getProfile()
    Object.assign(form, res)
  } finally { loading.value = false }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const res: any = await updateProfile({
      nickname: form.nickname,
      bio: form.bio,
      avatar_url: form.avatar_url,
      gender: form.gender,
      location: form.location,
      website: form.website,
      github: form.github,
    })
    Object.assign(form, res)
    await authStore.fetchUser()
    ElMessage.success('保存成功')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally { saving.value = false }
}

const beforeAvatarUpload = (file: File) => {
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB')
    return false
  }
  return true
}

const handleAvatarUpload = async (options: any) => {
  try {
    const res: any = await uploadImage(options.file, 'avatar')
    form.avatar_url = res.url
    await updateProfile({ avatar_url: res.url })
    await authStore.fetchUser()
    ElMessage.success('头像上传成功')
  } catch (e: any) {
    ElMessage.error(e?.message || e?.response?.data?.detail || '上传失败')
  }
}

const changePassword = async () => {
  if (!passwordForm.old_password || !passwordForm.new_password) {
    ElMessage.warning('请填写完整密码信息')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  if (passwordForm.new_password.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  changingPassword.value = true
  try {
    await changePasswordApi(passwordForm.old_password, passwordForm.new_password)
    ElMessage.success('密码修改成功，请重新登录')
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    authStore.logout()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '密码修改失败')
  } finally { changingPassword.value = false }
}

onMounted(loadProfile)
</script>

<style scoped>
.level-info { display: flex; flex-direction: column; gap: 12px; }
.avatar-row { display: flex; align-items: center; gap: 16px; }
.avatar-actions { display: flex; flex-direction: column; gap: 8px; flex: 1; }
</style>
