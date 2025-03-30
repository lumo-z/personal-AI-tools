<template>
  <div class="register">
    <el-form>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="form.phone" placeholder="请输入手机号"></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码"></el-input>
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码"></el-input>
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">注册</el-button>
        <el-span @click="login">已有账户？去登录</el-span>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { registerApi } from '@/api/user'
export default {
  name: 'Register',
  data () {
    return {
      form: {
        username: '',
        phone: '',
        password: '',
        confirmPassword: '',
        email: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3456789]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 12, message: '密码长度不能少于6位,不能多于12位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          {
            validator: (value, callback) => {
              if (value !== this.form.password) {
                callback(new Error('两次输入密码不一致'))
              } else if (this.form.password.length < 6 || this.form.password.length > 12) {
                callback(new Error('密码长度不能少于6位,不能多于12位'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ]
      }
    }
  },
  methods: {
    handleSubmit () {
      const response = registerApi(this.form)
      if (response.status === 200) {
        this.$message.success('注册成功')
        this.$router.push({ path: '/login' })
      }
    },
    handleCaptcha () {
      console.log('Captcha sent to:', this.form.phone)
    },
    login () {
      this.$router.push({ path: '/' })
    }
  }
}
</script>

<style lang="less" scoped></style>
