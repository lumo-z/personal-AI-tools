<template>
  <div class="login-container">
    <!-- 打开弹窗的按钮 -->
    <el-button type="primary" @click="openDialog">打开登录弹窗</el-button>

    <!-- 登录弹窗 -->
    <el-dialog
      title="登录"
      :visible.sync="dialogVisible"
      width="400px"
      :before-close="handleClose">

      <!-- 登录表单 -->
      <el-form :model="form" :rules="rules" ref="loginForm" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="form.password" placeholder="请输入密码"></el-input>
        </el-form-item>
      </el-form>
      <span class="register">
        没有账号？<router-link to ="/register">注册</router-link>
      </span>
      <!-- 弹窗底部按钮 -->
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">登录</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  data () {
    return {
      // 控制弹窗的显示状态
      dialogVisible: false,
      // 表单数据
      form: {
        username: '',
        password: ''
      },
      // 表单校验规则
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 12, message: '密码长度不能少于6位,不能多于12位', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    // 打开弹窗
    openDialog () {
      this.dialogVisible = true
    },
    // 关闭弹窗并清空表单
    handleClose () {
      this.dialogVisible = false
      this.$refs.loginForm.resetFields() // 清空表单
    },
    // 提交表单
    async handleSubmit () {
      try {
        const valid = await this.$refs.loginForm.validate()
        if (!valid) {
          console.log(valid)
          return
        }
        const { success, user, error } = await this.$store.dispatch(
          'user/login',
          this.form
        )

        if (success) {
          this.$message.success(`欢迎回来，${user.username}`)
          this.$router.go(0)
        } else {
          this.handleClose()
          this.$message.error(error)
        }
      } catch (err) {
        this.$message.error('表单验证失败')
      } finally {
        this.handleClose()
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.register{
  display: flex;
  justify-content: right;
}
</style>
